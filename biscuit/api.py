#coding: utf-8
import warnings
from django.conf.urls.defaults import *
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.db.models.base import ModelBase
from biscuit.exceptions import NotRegistered, BadRequest
from biscuit.resources import Resource, ModelResource, DeclarativeMetaclass
from biscuit.serializers import Serializer
from biscuit.utils import trailing_slash, is_valid_jsonp_callback_value
from biscuit.utils.mime import determine_format, build_content_type

class Api(object):
    """
    Implements a registry to tie together the various resources that make up
    an API.

    Especially useful for navigation, HATEOAS and for providing multiple
    versions of your API.

    Optionally supplying ``name`` allows you to name the API. Generally,
    this is done with version numbers (i.e. ``v1``, ``v2``, etc.) but can
    be named any string.

    You can also provide ``include`` argument that should be a list of `Api`
    instances to merge with this instance. This allows for more decoupled
    apps and cleaner imports.

    You can also provide ``defaults`` argument that should be a dictionary
    containing options used to construct Resources for Models.
    """
    def __init__(self, name=None, include=None,  model_defaults={}, forced_model_defaults={}, **kwargs):

        legacy_api_name = kwargs.get('api_name', None)
        self.api_name = name if name else legacy_api_name or 'v1'  # 'name' takes precedence and 'api_name' is a fallback
        self._registry = {}
        self._canonicals = {}
        self._model_defaults = model_defaults
        self._forced_defaults = forced_model_defaults

        if include is not None:
            if isinstance(include, Api):
                # it's more convenient not to wrap single object in list, so let's do it now
                include = [include]

            for snack in include:
                # should I update api_name for each snack?
                self._registry.update(snack._registry)      # a bit risky, overwrites previous values but it's developer's business
                self._canonicals.update(snack._canonicals)


    def register(self, res_mod_iter, defaults={}, canonical=True):
        """
        Registers a ``Resource`` subclass with the API. Allows registering
        list of ``Resource``s for convenience.

        Optionally accept a ``canonical`` argument, which indicates that the
        resources being registered are the canonical variant. Defaults to
        ``True``.

        You can also provide ``defaults`` argument that should be a dictionary
        containing options used to construct Resources for Models.
        This overrides ``defaults`` set when instantiating ``Api`` but not over
        ``forced_defaults``.
        """
        # DeclarativeMetaclas -> Resource subclass; let's instantiate it
        # Resource -> Resource subclass *instance*; issue DeprecationWarning
        # ModelBase -> Model subclass; let's make a ModelResource based on it

        if isinstance(res_mod_iter, DeclarativeMetaclass) or \
           isinstance(res_mod_iter, Resource) or \
           isinstance(res_mod_iter, ModelBase):
            res_mod_iter = [res_mod_iter]


        for obj in res_mod_iter:
            # if Model subclass, make a ModelResource with sane defaults
            # it's so hackish that it might actually work ;)
            if isinstance(obj, ModelBase):
                _defaults = {'resource_name': obj._meta.module_name,
                             'queryset': obj.objects.all(),
                             }
                _defaults.update(self._model_defaults)  # easy way to change default option for models
                _defaults.update(defaults)
                _defaults.update(self._forced_defaults)
                dummy_meta = type("Meta", (object,), _defaults)
                dummy_resource = type("%sResource" % obj.__name__, (ModelResource,), {'Meta': dummy_meta,})
                obj = dummy_resource()
            elif not isinstance(obj, Resource):
                obj = obj()
            else:
                warnings.warn(
                    "Passing of instances is deprecated and marked for removal in 1.0.0",
                    DeprecationWarning
                )

            resource_name = getattr(obj._meta, 'resource_name', None)

            if resource_name is None:
                raise ImproperlyConfigured("Resource %r must define a 'resource_name'." % obj)

            self._registry[resource_name] = obj

            if canonical is True:
                if resource_name in self._canonicals:
                    warnings.warn("A new resource '%r' is replacing the existing canonical URL for '%s'." % (obj, resource_name), Warning, stacklevel=2)

                self._canonicals[resource_name] = obj
                # TODO: This is messy, but makes URI resolution on FK/M2M fields
                #       work consistently.
                obj._meta.api_name = self.api_name           #?
                obj.__class__.Meta.api_name = self.api_name  #?!

    def unregister(self, resource_name):
        """
        If present, unregisters a resource from the API.
        """
        if resource_name in self._registry:
            del(self._registry[resource_name])

        if resource_name in self._canonicals:
            del(self._canonicals[resource_name])

    def canonical_resource_for(self, resource_name):
        """
        Returns the canonical resource for a given ``resource_name``.
        """
        if resource_name in self._canonicals:
            return self._canonicals[resource_name]

        raise NotRegistered("No resource was registered as canonical for '%s'." % resource_name)

    def wrap_view(self, view):
        def wrapper(request, *args, **kwargs):
            return getattr(self, view)(request, *args, **kwargs)
        return wrapper

    def override_urls(self):
        """
        Deprecated. Will be removed by v1.0.0. Please use ``prepend_urls`` instead.
        """
        warnings.warn("'override_urls' is a deprecated method & will be removed by v1.0.0. Please use ``prepend_urls`` instead.")
        return self.prepend_urls()

    def prepend_urls(self):
        """
        A hook for adding your own URLs or matching before the default URLs.
        """
        return []

    @property
    def urls(self):
        """
        Provides URLconf details for the ``Api`` and all registered
        ``Resources`` beneath it.
        """
        pattern_list = [
            url(r"^(?P<api_name>%s)%s$" % (self.api_name, trailing_slash()), self.wrap_view('top_level'), name="api_%s_top_level" % self.api_name),
        ]

        for name in sorted(self._registry.keys()):
            self._registry[name].api_name = self.api_name
            pattern_list.append((r"^(?P<api_name>%s)/" % self.api_name, include(self._registry[name].urls)))

        urlpatterns = self.prepend_urls()

        if self.override_urls():
            warnings.warn("'override_urls' is a deprecated method & will be removed by v1.0.0. Please rename your method to ``prepend_urls``.")
            urlpatterns += self.override_urls()

        urlpatterns += patterns('',
            *pattern_list
        )
        return urlpatterns

    def top_level(self, request, api_name=None):
        """
        A view that returns a serialized list of all resources registers
        to the ``Api``. Useful for discovery.
        """
        serializer = Serializer()
        available_resources = {}

        if api_name is None:
            api_name = self.api_name

        for name in sorted(self._registry.keys()):
            available_resources[name] = {
                'list_endpoint': self._build_reverse_url("api_dispatch_list", kwargs={
                    'api_name': api_name,
                    'resource_name': name,
                }),
                'schema': self._build_reverse_url("api_get_schema", kwargs={
                    'api_name': api_name,
                    'resource_name': name,
                }),
            }

        desired_format = determine_format(request, serializer)
        options = {}

        if 'text/javascript' in desired_format:
            callback = request.GET.get('callback', 'callback')

            if not is_valid_jsonp_callback_value(callback):
                raise BadRequest('JSONP callback name is invalid.')

            options['callback'] = callback

        serialized = serializer.serialize(available_resources, desired_format, options)
        return HttpResponse(content=serialized, content_type=build_content_type(desired_format))

    def _build_reverse_url(self, name, args=None, kwargs=None):
        """
        A convenience hook for overriding how URLs are built.

        See ``NamespacedApi._build_reverse_url`` for an example.
        """
        return reverse(name, args=args, kwargs=kwargs)


class NamespacedApi(Api):
    """
    An API subclass that respects Django namespaces.
    """
    def __init__(self, name="v1", urlconf_namespace=None):
        super(NamespacedApi, self).__init__(name=name)
        self.urlconf_namespace = urlconf_namespace

    def register(self, resource, canonical=True):
        super(NamespacedApi, self).register(resource, canonical=canonical)

        if canonical is True:
            # Plop in the namespace here as well.
            resource._meta.urlconf_namespace = self.urlconf_namespace

    def _build_reverse_url(self, name, args=None, kwargs=None):
        namespaced = "%s:%s" % (self.urlconf_namespace, name)
        return reverse(namespaced, args=args, kwargs=kwargs)
