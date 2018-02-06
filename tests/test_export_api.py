import pytest
import responses
from requests.exceptions import ConnectionError

from appmetrica.export.api import ExportAPI
from appmetrica.export.exceptions import AppMetricaPrepareData, AppMetricaExportPushTokenError

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin


@pytest.fixture
def api():
    yield ExportAPI(app_id=123, access_token='123')


@responses.activate
def test_get_push_tokens_success(api):
    url = urljoin(ExportAPI.base_url, 'push_tokens.json')
    responses.add(responses.GET, url, status=202, body='')

    # first preparation of data
    with pytest.raises(AppMetricaPrepareData):
        assert api.export_push_tokens('token')

    # then return data
    data = {
        'data': [
            {'token': 'D7BB4C4F8B3CF81488DEAAC8ABC1B955'},
            {'token': 'E80C89308D7A8B142861ADC4875D3D88'}
        ]
    }
    responses.replace(responses.GET, url, status=200, json=data)
    data = api.export_push_tokens('token')
    assert len(data) == 2
    assert data[0]['token'] == 'D7BB4C4F8B3CF81488DEAAC8ABC1B955'


@pytest.mark.parametrize('params', [
    {'status': 500},
    {'body': ConnectionError()},
])
@responses.activate
def test_get_push_tokens_error(params, api):
    url = urljoin(ExportAPI.base_url, 'push_tokens.json')
    responses.add(responses.GET, url, **params)
    with pytest.raises(AppMetricaExportPushTokenError):
        api.export_push_tokens('token')
