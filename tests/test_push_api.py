import pytest
import responses
from requests.exceptions import ConnectionError

from appmetrica.push.api import PushAPI, TokenTypes
from appmetrica.push.exceptions import (AppMetricaCreateGroupError, AppMetricaSendPushError,
                                        AppMetricaCheckStatusError, AppMetricaGetGroupsError)

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin


@pytest.fixture
def api():
    yield PushAPI(app_id=123, access_token='123')


@pytest.fixture
def devices():
    yield [
        {
            'id_type': TokenTypes.APPMETRICA_DEVICE_ID,
            'id_values': ['123456789', '42']
        },
        {
            'id_type': TokenTypes.IOS_IFA,
            'id_values': ['29868ed6-826e-442c-a234-5c5ad8a42b72']
        },
        {
            'id_type': TokenTypes.ANDROID_PUSH_TOKEN,
            'id_values': ['WYMYUV6NSWj0kePNP-tCPtXon4exEpqv4yZmtvuLF0qgAgQB5FoUG1XwhYwA6RPz1Wa8U']
        }
    ]


@pytest.fixture
def ios_message():
    yield PushAPI.build_ios_message(
        title='Subject',
        text='Body',
        data={'book': 77}
    )


@responses.activate
def test_create_group_success(api):
    data = {
        'group': {
            'id': 9,
            'app_id': 123,
            'name': 'foobar'
        }
    }
    url = urljoin(PushAPI.base_url, 'management/groups')
    responses.add(responses.POST, url, status=200, json=data)
    assert api.create_group('foobar') == 9


@pytest.mark.parametrize('params', [
    {'status': 500},
    {'body': ConnectionError()},
])
@responses.activate
def test_create_group_error(params, api):
    url = urljoin(PushAPI.base_url, 'management/groups')
    responses.add(responses.POST, url, **params)
    with pytest.raises(AppMetricaCreateGroupError):
        api.create_group('foobar')


@responses.activate
def test_get_groups_success(api):
    groups = [
        {
            'id': 11,
            'app_id': 123,
            'name': 'foobar'
        },
        {
            'id': 12,
            'app_id': 123,
            'name': 'alexbob'
        }
    ]
    url = urljoin(PushAPI.base_url, 'management/groups')
    responses.add(responses.GET, url, status=200, json={'groups': groups})
    assert api.get_groups() == groups


@pytest.mark.parametrize('params', [
    {'status': 500},
    {'body': ConnectionError()},
])
@responses.activate
def test_get_groups_error(params, api):
    url = urljoin(PushAPI.base_url, 'management/groups')
    responses.add(responses.GET, url, **params)
    with pytest.raises(AppMetricaGetGroupsError):
        api.get_groups()


@responses.activate
def test_send_push_success(api, devices, ios_message):
    data = {
        'push_response': {
            'transfer_id': 1020
        }
    }
    url = urljoin(PushAPI.base_url, 'send-batch')
    responses.add(responses.POST, url, status=200, json=data)
    assert api.send_push(9, devices=devices, ios_message=ios_message) == 1020
    assert api.send_push(10, devices=devices, android_message=ios_message) == 1020


@responses.activate
def test_send_push_error(api, devices, ios_message):
    url = urljoin(PushAPI.base_url, 'send-batch')
    responses.add(responses.POST, url, body=ConnectionError())
    with pytest.raises(AppMetricaSendPushError):
        api.send_push(9, devices=devices, ios_message=ios_message)


def test_send_push_error_params(api, devices, ios_message):
    with pytest.raises(AppMetricaSendPushError):
        api.send_push(9, ios_message=ios_message)
    with pytest.raises(AppMetricaSendPushError):
        api.send_push(9, devices=devices)


@responses.activate
def test_check_status_success(api):
    data = {
        'transfer': {
            'id': 505,
            'status': 'sent',
            'errors': []
        }
    }
    url = urljoin(PushAPI.base_url, 'status/505')
    responses.add(responses.GET, url, status=200, json=data)
    assert api.check_status(505) == 'sent'


@pytest.mark.parametrize('params', [
    {'status': 500},
    {'status': 200, 'json': {'transfer': {'id': 2999, 'status': 'failed', 'errors': ['Error']}}},
])
@responses.activate
def test_check_status_error(api, params):
    url = urljoin(PushAPI.base_url, 'status/2999')
    responses.add(responses.GET, url, **params)
    with pytest.raises(AppMetricaCheckStatusError):
        api.check_status(2999)
