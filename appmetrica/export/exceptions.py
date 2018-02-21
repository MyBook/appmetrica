from appmetrica.exceptions import AppMetricaException


class AppMetricaExportInstallationsError(AppMetricaException):
    """Raised when yandex export api responds with an error that get installations"""
    pass


class AppMetricaExportPushTokenError(AppMetricaException):
    """Raised when yandex export api responds with an error that get push tokens"""
    pass


class AppMetricaPrepareData(AppMetricaException):
    """Raised when yandex export api responds that the request is queued for processing"""
    pass
