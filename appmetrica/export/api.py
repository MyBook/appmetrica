# coding: utf-8
import logging
from appmetrica.base import BaseAPI
from appmetrica.export import exceptions
from appmetrica.utils import format_appmetrica_date

logger = logging.getLogger(__name__)


class ExportAPI(BaseAPI):
    base_url = 'https://api.appmetrica.yandex.ru/logs/v1/export/'

    def export_push_tokens(self, *fields):
        """
        Download all push tokens registered in the application
        :param fields: list of requested fields
        :return: list of push tokens
        """
        params = {
            'application_id': self.app_id,
            'fields': ','.join(fields)
        }
        try:
            response_data = self._request('get', 'push_tokens.json', params=params)
        except exceptions.AppMetricaPrepareData:
            raise
        except Exception as exc:
            logger.error('push_tokens request failed due to %s', exc, exc_info=True)
            raise exceptions.AppMetricaExportPushTokenError

        # response_data contains dict like:
        # {
        #   "data": [
        #     {
        #       "token": '85059BF7C6A07F7088FA75189BE045AAE9A584ACB80840A8622A8913C2ED7B40'
        #     },
        #     {
        #       "token": 'EAA690AF9A76D843A2DE6837ECC352DEED2783C7BC2C510934583B13996A1B04'
        #     }
        #   ]
        # }
        return response_data['data']

    def export_installations(self, *fields, **kwargs):
        """
        Download installations
        :param fields: list of requested fields
        :param date_from (optional): from which date to download data
        :param date_till (optional): till which date to download data
        :return: list of devices
        """
        params = {
            'application_id': self.app_id,
            'fields': ','.join(fields),
            'date_dimension': 'receive'
        }
        if kwargs.get('date_from'):
            params['date_since'] = format_appmetrica_date(kwargs['date_from'])
        if kwargs.get('date_till'):
            params['date_until'] = format_appmetrica_date(kwargs['date_till'])

        try:
            response_data = self._request('get', 'installations.json', params=params)
        except exceptions.AppMetricaPrepareData:
            raise
        except Exception as exc:
            logger.error('installations request failed due to %s', exc, exc_info=True)
            raise exceptions.AppMetricaExportInstallationsError

        # response_data contains dict like:
        # {
        #   "data": [
        #     {
        #       "ios_ifv": 'DD01EF7E-1848-4C9A-85C3-13563A2A272C'
        #     },
        #     {
        #       "ios_ifv": '5B2AAD52-BEB2-4B39-B54F-5EFB26125FCE'
        #     }
        #   ]
        # }
        return response_data['data']

    def _data_from_response(self, response):
        if response.status_code == 202:
            # Query is added to the queue
            raise exceptions.AppMetricaPrepareData

        return super(ExportAPI, self)._data_from_response(response)
