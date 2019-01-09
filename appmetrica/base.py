# coding: utf-8
import logging
import requests
from appmetrica.exceptions import AppMetricaRequestError

logger = logging.getLogger(__name__)


class BaseAPI(object):
    base_url = None
    request_timeout = 30
    access_token = None
    app_id = None

    def __init__(self, app_id, access_token):
        self.app_id = app_id
        self.access_token = access_token

    def _request(self, method, endpoint, params=None, headers=None, json=None):
        params = params or {}
        headers = headers or {}
        headers.setdefault('Content-Type', 'application/json')
        headers.setdefault('Authorization',
                           'OAuth {access_token}'.format(access_token=self.access_token))

        url = '{base_url}/{endpoint}'.format(base_url=self.base_url.rstrip('/'), endpoint=endpoint)

        try:
            response = requests.request(method, url, params=params, json=json,
                                        headers=headers, timeout=self.request_timeout)
        except Exception as exc:
            logger.error('failed to request %s %s with headers=%s, params=%s json=%s due to %s',
                         method, url, headers, params, json, exc,
                         exc_info=True,
                         extra={'data': {'json': json, 'params': params}})
            raise AppMetricaRequestError

        if not (200 <= response.status_code < 300):
            logger.error('failed to request %s %s with headers=%s, params=%s json=%s due to %s',
                         method, url, headers, params, json, response.content,
                         extra={'data': {'json': json, 'params': params}})
            raise AppMetricaRequestError

        return self._data_from_response(response)

    def _data_from_response(self, response):
        try:
            return response.json()
        except Exception as exc:
            logger.warning('unable to parse json response due to %s', exc, exc_info=True,
                           extra={'data': {'content': response.content}})
            raise AppMetricaRequestError
