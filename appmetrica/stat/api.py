# coding: utf-8
import logging

from appmetrica.exceptions import AppMetricaException

from appmetrica.base import BaseAPI

logger = logging.getLogger(__name__)


class StatAPI(BaseAPI):
    base_url = 'https://api.appmetrica.yandex.ru/stat/v1/'

    def export_stat(self, params):
        """
        Download stat reports https://appmetrica.yandex.ru/docs/mobile-api/api_v1/data.html

        :param params: dict with query params
        :return: dict with stat data
        """
        try:
            response_data = self._request('get', endpoint='data', params=params)
        except AppMetricaException as exc:  # pragma: no cover
            logger.error('failed to export stat due to %s', exc, exc_info=True)
            raise exc

        # response_data contains dict like:
        # {
        #     "total_rows" : <long>,
        #     "sampled" : <boolean>,
        #     "sample_share" : <double>,
        #     "sample_size" : <long>,
        #     "sample_space" : <long>,
        #     "data_lag" : <int>,
        #     "query" : {
        #         "ids" : [ <int>, ... ],
        #         "dimensions" : [ <string>, ... ],
        #         "metrics" : [ <string>, ... ],
        #         "sort" : [ <string>, ... ],
        #         "date1" : <string>,
        #         "date2" : <string>,
        #         "filters" : <string>,
        #         "limit" : <integer>,
        #         "offset" : <integer>
        #     },
        #     "totals" : [ <double>, ... ],
        #     "min" : [ <double>, ... ],
        #     "max" : [ <double>, ... ],
        #     "data" : [ {
        #         "dimensions" : [ {
        #             "key_1" : <string>,
        #             "key_2" : ...
        #         }, ... ],
        #         "metrics" : [ <double>, ... ]
        #     }, ... ]
        # }
        return response_data['data']
