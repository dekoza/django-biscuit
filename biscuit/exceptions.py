from django.http import HttpResponse


class BiscuitError(Exception):
    """A base exception for other biscuit-related errors."""
    pass


class HydrationError(BiscuitError):
    """Raised when there is an error hydrating data."""
    pass


class NotRegistered(BiscuitError):
    """
    Raised when the requested resource isn't registered with the ``Api`` class.
    """
    pass


class NotFound(BiscuitError):
    """
    Raised when the resource/object in question can't be found.
    """
    pass


class ApiFieldError(BiscuitError):
    """
    Raised when there is a configuration error with a ``ApiField``.
    """
    pass


class UnsupportedFormat(BiscuitError):
    """
    Raised when an unsupported serialization format is requested.
    """
    pass


class BadRequest(BiscuitError):
    """
    A generalized exception for indicating incorrect request parameters.

    Handled specially in that the message tossed by this exception will be
    presented to the end user.
    """
    pass


class BlueberryFillingFound(BiscuitError):
    pass


class InvalidFilterError(BadRequest):
    """
    Raised when the end user attempts to use a filter that has not be
    explicitly allowed.
    """
    pass


class InvalidSortError(BiscuitError):
    """
    Raised when the end user attempts to sort on a field that has not be
    explicitly allowed.
    """
    pass


class ImmediateHttpResponse(BiscuitError):
    """
    This exception is used to interrupt the flow of processing to immediately
    return a custom HttpResponse.

    Common uses include::

        * for authentication (like digest/OAuth)
        * for throttling

    """
    response = HttpResponse("Nothing provided.")

    def __init__(self, response):
        self.response = response