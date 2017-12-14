class AppMetricaException(Exception):
    pass


class AppMetricaRequestError(AppMetricaException):
    pass


class AppMetricaCreateGroupError(AppMetricaException):
    pass


class AppMetricaSendPushError(AppMetricaException):
    pass


class AppMetricaCheckStatusError(AppMetricaException):
    pass
