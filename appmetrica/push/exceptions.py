class AppMetricaException(Exception):
    """Base Exception class for all AppMetrica errors"""
    pass


class AppMetricaRequestError(AppMetricaException):
    """Raised when received an expected error code from yandex push api"""
    pass


class AppMetricaCreateGroupError(AppMetricaException):
    """Raised when yandex push api responds with an error that creating a group"""
    pass


class AppMetricaSendPushError(AppMetricaException):
    """Raised when yandex push api responds with an error that sending a push"""
    pass


class AppMetricaCheckStatusError(AppMetricaException):
    """Raised when yandex push api responds with an error that checking status"""
    pass
