from appmetrica.exceptions import AppMetricaException


class AppMetricaExportPushTokenError(AppMetricaException):
    """Raised when yandex export api responds with an error that get push tokens"""
    pass


class AppMetricaPrepareData(AppMetricaException):
    pass
