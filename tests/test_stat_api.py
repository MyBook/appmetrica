import pytest
import responses

from appmetrica.stat.api import StatAPI

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin


@pytest.fixture
def api():
    yield StatAPI(app_id=123, access_token='123')


@responses.activate
def test_get_stat_data(api):
    query = {
        'ids': 123,
        'metrics': ['ym:pc:users'],
    },
    data = {
        'data': [{'total_rows': 999, 'query': query, 'metrics': 12345}]
    }
    url = urljoin(StatAPI.base_url, 'data')
    with responses.RequestsMock(assert_all_requests_are_fired=True) as resp_mock:
        resp_mock.add(responses.GET, url, status=200, json=data, match_querystring=False)
        assert api.export_stat(query)
