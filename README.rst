==============
django-biscuit
==============

Letting you slack off while developing tasty APIs for Django apps since 2012.

This project is a fork of `django-tastypie` and the main aim is to
make Tastypie DRY as hell. It means  that you shouldn't be forced
to write any classes just to get a basic functionality. Just like you
don't have to write ModelAdmin classes to get your Admin Panel working.

This will be a drop-in replacement for Tastypie, i.e. it should work out
of the box for your old Tastypie APIs but provide you with more DRY approach
if you want to add something more. As a drop-in replacement Biscuit will
benefit also from all API consumers tailored/optimized for Tastypie like drest.

The whole rationale behind this fork is outlined here: https://github.com/toastdriven/django-tastypie/issues/599

Currently in alpha (v0.0.1) and pretty much identical to Tastypie.

.. warning::
    I'll say it once again: **this project is early alpha**.
    Do **NOT** use this unless you want to contribute.


Requirements
============

Required
--------

* Python 2.6+
* Django 1.3+
* mimeparse 0.1.3+ (http://code.google.com/p/mimeparse/)

  * Older versions will work, but their behavior on JSON/JSONP is a touch wonky.

* dateutil (http://labix.org/python-dateutil) >= 1.5, < 2.0

Optional
--------

* python_digest (https://bitbucket.org/akoha/python-digest/)
* lxml (http://lxml.de/) if using the XML serializer
* pyyaml (http://pyyaml.org/) if using the YAML serializer
* biplist (http://explorapp.com/biplist/) if using the binary plist serializer


What's It Look Like?
====================

At this stage it's more like  "What It **SHOULD** Look Like?"

A basic example *should* look like this::

    # myapp/api.py
    # ============
    from biscuit.api import Api
    from myapp.models import Entry

    myapi = Api()
    myapi.register(Entry)

    # urls.py
    # =======
    from django.conf.urls.defaults import *
    from biscuit.api import Api
    from myapp.api import myapi

    api = Api(name='v1', consume=[myapi])

    urlpatterns = patterns('',
        # The normal jazz here then...
        (r'^api/', include(api.urls)),
    )

That should get you a fully working, read-write API for the ``Entry`` model that
supports all CRUD operations in a RESTful way. JSON/XML/YAML support is already
there, and it's easy to add related data/authentication/caching. And all this
without writing a single class.


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


Reference Material
==================

* http://en.wikipedia.org/wiki/REST
* http://en.wikipedia.org/wiki/List_of_HTTP_status_codes
* http://www.ietf.org/rfc/rfc2616.txt
* http://jacobian.org/writing/rest-worst-practices/
