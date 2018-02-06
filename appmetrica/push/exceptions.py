from appmetrica.exceptions import AppMetricaException


class AppMetricaCreateGroupError(AppMetricaException):
    """Raised when yandex push api responds with an error that creating a group"""
    pass


class AppMetricaSendPushError(AppMetricaException):
    """Raised when yandex push api responds with an error that sending a push"""
    pass


class AppMetricaCheckStatusError(AppMetricaException):
    """Raised when yandex push api responds with an error that checking status"""
    pass
