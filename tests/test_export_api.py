import pytest
import responses
from requests.exceptions import ConnectionError

from appmetrica.export.api import API as ExportAPI
from appmetrica.export.exceptions import AppMetricaPrepareData, AppMetricaExportPushTokenError


@pytest.fixture
def export_api():
    yield ExportAPI(app_id=123, access_token='123')


@responses.activate
def test_get_push_tokens_success(export_api):
    url = ExportAPI.base_url + 'push_tokens.json'
    responses.add(responses.GET, url, status=202, body='')

    # first preparation of data
    with pytest.raises(AppMetricaPrepareData):
        assert export_api.push_tokens('token')

    # than return data
    data = {
        'data': [
            {'token': 'D7BB4C4F8B3CF81488DEAAC8ABC1B955'},
            {'token': 'E80C89308D7A8B142861ADC4875D3D88'}
        ]
    }
    responses.replace(responses.GET, url, status=200, json=data)
    resp = export_api.push_tokens('token')
    assert len(resp['data']) == 2
    assert resp['data'][0]['token'] == 'D7BB4C4F8B3CF81488DEAAC8ABC1B955'


@pytest.mark.parametrize('params', [
    {'status': 500},
    {'body': ConnectionError()},
])
def test_get_push_tokens_error(params, export_api):
    responses.add(responses.GET, ExportAPI.base_url + 'push_tokens.json', **params)
    with pytest.raises(AppMetricaExportPushTokenError):
        export_api.push_tokens('token')
