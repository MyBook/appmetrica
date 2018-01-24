# coding: utf-8
import logging
import requests
from appmetrica.export import exceptions
from appmetrica.exceptions import AppMetricaRequestError

logger = logging.getLogger(__name__)


class API(object):
    base_url = 'https://api.appmetrica.yandex.ru/logs/v1/export/'
    request_timeout = 5
    access_token = None
    app_id = None

    def __init__(self, app_id, access_token):
        self.access_token = access_token
        self.app_id = app_id

    def push_tokens(self):
        try:
            response_data = self._request('get', 'push_tokens.json',
                                          params={'application_id': 416934, 'fields': 'ios_ifa,google_aid'})
        except exceptions.AppMetricaPrepareData:
            raise
        except Exception as exc:
            logger.error('push_tokens request failed due to %s', exc, exc_info=True)
            raise exceptions.AppMetricaExportPushTokenError

        return response_data

    def _request(self, method, endpoint, params=None, headers=None):
        params = params or {}
        headers = headers or {}
        headers.setdefault('Content-Type', 'application/json')
        headers.setdefault('Authorization',
                           'OAuth {access_token}'.format(access_token=self.access_token))

        url = '{base_url}/{endpoint}'.format(base_url=self.base_url.rstrip('/'), endpoint=endpoint)

        try:
            response = requests.request(method, url, params=params, headers=headers,
                                        timeout=self.request_timeout)
        except Exception as exc:
            logger.error('failed to request %s %s with headers=%s, params=%s due to %s',
                         method, url, headers, params, exc,
                         exc_info=True,
                         extra={'data': {'params': params}})
            raise AppMetricaRequestError

        if response.status_code not in (200, 202):
            logger.error('failed to request %s %s with headers=%s, params=%s due to %s',
                         method, url, headers, params, response.content,
                         extra={'data': {'params': params}})
            raise AppMetricaRequestError

        if response.status_code == 202:
            # Query is added to the queue
            raise exceptions.AppMetricaPrepareData

        if response.status_code == 200:
            try:
                response_data = response.json()
            except Exception as exc:
                logger.warning('unable to parse json response due to %s', exc, exc_info=True,
                               extra={'data': {'content': response.content}})
                raise AppMetricaRequestError

            return response_data
