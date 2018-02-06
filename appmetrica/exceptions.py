class AppMetricaException(Exception):
    """Base Exception class for all AppMetrica errors"""
    pass


class AppMetricaRequestError(AppMetricaException):
    """Raised when received an expected error code from yandex push api"""
    pass
