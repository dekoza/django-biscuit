==============
django-biscuit
==============

Letting you slack off while developing tasty APIs for Django apps.

This project is a fork of `django-tastypie <https://github.com/toastdriven/django-tastypie>`_ and the main aim is to
refactor it in such a way, that the DRY principle will be respected.
I mean - seriously - you shouldn't have to be forced to write any classes
just to get a simple basic API functionality like listing your Models.
Just like you don't have to write ModelAdmin classes to get your Admin
Panel working.

The whole rationale behind this fork is outlined in Tastypie's issue
`#599 <https://github.com/toastdriven/django-tastypie/issues/599>`_.

Current version (v0.2.0) is considered **beta** - seems to work but needs heavy testing.

.. warning::
    This project is **NOT YET** properly tested. Use at your own risk.

Any help and suggestions will be appreciated.

.. note::
    All the rest of the documentation - for now - is a mirror of Tastypie's
    docs and as such is not 100% relevant to Biscuit. Expect corrections
    anytime soon. I'll accept any help to straighten this up.


Requirements
============

Required
--------

* Python 2.6+
* Django 1.3+
* mimeparse 0.1.3+ (http://code.google.com/p/mimeparse/)

  * Older versions will work, but their behavior on JSON/JSONP is a touch wonky.

* dateutil (https://launchpad.net/dateutil) == 1.5 (should also work with >= 2.1)

Optional
--------

* python_digest (https://bitbucket.org/akoha/python-digest/)
* lxml (http://lxml.de/) if using the XML serializer
* pyyaml (http://pyyaml.org/) if using the YAML serializer
* biplist (http://explorapp.com/biplist/) if using the binary plist serializer


What's It Look Like?
====================

The most basic example looks like this::

    # myapp/api.py
    # ============
    from biscuit.api import Api
    from myapp.models import Entry

    myapi = Api()
    myapi.register(Entry)

    # urls.py
    # =======
    from django.conf.urls.defaults import *
    from myapp.api import myapi

    urlpatterns = patterns('',
        # The normal jazz here then...
        (r'^api/', include(myapi.urls)),
    )

That should get you a fully working, read-write API for the ``Entry`` model that
supports all CRUD operations in a RESTful way. Behind the scenes a ``ModelResource``
is created with sane defaults based on the Model you registered. JSON/XML/YAML
support is already there, and it's easy to add related data/authentication/caching.
And all this without writing a single class.

Why Biscuit?
=============

There are other, better known API frameworks out there for Django. You need to
assess the options available and decide for yourself. That said, here are some
common reasons for biscuit.

* You need an API that is RESTful and uses HTTP well.
* You want to support deep relations.
* You DON'T want to be forced to write any classes to get basic functionality.
* You DON'T want to have to write your own serializer to make the output right.
* You want an API framework that is very flexible, doesn't push you around and
  maps well to the problem domain.
* You want/need XML serialization that is treated equally to JSON (and YAML is
  there too).
* You want to read only a short Tutorial to get started.
* Biscuit benefits from all API consumers tailored/optimized for Tastypie,
  like `drest <http://drest.rtfd.org/>`_.


Tastypie drop-in replacement
----------------------------

As the module has a different name, Biscuit itself is not a painless
drop-in replacement for Tastypie as you'd need to refactor your code
to get everything normally. But if you do want to benefit from *some*
of Biscuit's goodness, you can checkout ``tastypie`` branch. I try
to keep it up to date with current Tastypie development plus it
includes all the patches that do not break compatibility.


Differences with Tastypie
-------------------------

* You can register ``Model`` subclasses and appropriate ModelResource with sane defaults
  (meaning ``resource_name = <Model>._meta.module_name`` and ``queryset = <Model>.objects.all()``) is
  tailored behind the scenes.
* You can register ``Resource`` subclasses (compare new ``v1.register(MyResource)`` with old ``v1.register(MyResource())``)
* You can put all those in a list and write a single register: ``v1.register([MyFirstResource, MyOtherResource]``).
  This list is not restricted and can contain both ``Resource`` and ``Model`` subclasses.
* You can of course register ``Resource`` subclass' instances, just like you did in Tastypie (that's what "drop-in replacement" really means)
* No more cluttering urls.py - create ``Api`` instances in your app and then just import and include it in urls.py. Compare::

    # urls.py - Tastypie
    from tastypie.api import Api
    from myapp.api import FirstResource, SecondResource
    from otherapp.api import ThirdResource, FourthResource

    v1 = Api(api_name='v1')

    v1.register(FirstResource)
    v1.register(SecondResource)
    v1.register(ThirdResource)
    v1.register(FourthResource)

    urlpatterns = patterns('',
        # (...)
        url(r'^api/', include(v1.urls)),
    )

  with::

    # urls.py - Biscuit
    from biscuit import Api
    from myapp.api import myapi
    from otherapp.api import otherapi

    v1 = Api(name='v1', include=[myapi, otherapi])

    urlpatterns = patterns('',
        # (...)
        url(r'^api/', include(v1.urls)),
    )

  DRY and clean, isn't it? :)


Versioning
----------

Starting from 0.2.0 I'll try to follow Semantic Version guidelines.

Releases will be numbered with the following format:

  ``<major>.<minor>.<patch>``

And constructed with the following guidelines:

* Breaking backward compatibility bumps the major (and resets the minor and patch)
* New additions without breaking backward compatibility bumps the minor (and resets the patch)
* Bug fixes and misc changes bumps the patch
* Major version ``0`` means early development stage

For more information on SemVer, please visit http://semver.org/.

Reference Material
==================

* http://en.wikipedia.org/wiki/REST
* http://en.wikipedia.org/wiki/List_of_HTTP_status_codes
* http://www.ietf.org/rfc/rfc2616.txt
* http://jacobian.org/writing/rest-worst-practices/
