import pytest
import responses
from requests.exceptions import ConnectionError

from appmetrica.push.api import API as PushAPI, TokenTypes
from appmetrica.push.exceptions import (AppMetricaCreateGroupError, AppMetricaSendPushError,
                                        AppMetricaCheckStatusError)


@pytest.fixture
def push_api():
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
def test_create_group_success(push_api):
    data = {
        'group': {
            'id': 9,
            'app_id': 123,
            'name': 'foobar'
        }
    }
    responses.add(responses.POST, PushAPI.base_url + 'management/groups',
                  status=200, json=data)
    assert push_api.create_group('foobar') == 9


@pytest.mark.parametrize('params', [
    {'status': 500},
    {'body': ConnectionError()},
])
@responses.activate
def test_create_group_error(params, push_api):
    responses.add(responses.POST, PushAPI.base_url + 'management/groups', **params)
    with pytest.raises(AppMetricaCreateGroupError):
        push_api.create_group('foobar')


@responses.activate
def test_send_push_success(push_api, devices, ios_message):
    data = {
        'push_response': {
            'transfer_id': 1020
        }
    }
    responses.add(responses.POST, PushAPI.base_url + 'send', status=200, json=data)
    assert push_api.send_push(9, devices=devices, ios_message=ios_message) == 1020
    assert push_api.send_push(10, devices=devices, android_message=ios_message) == 1020


@responses.activate
def test_send_push_error(push_api, devices, ios_message):
    responses.add(responses.POST, PushAPI.base_url + 'send', body=ConnectionError())
    with pytest.raises(AppMetricaSendPushError):
        push_api.send_push(9, devices=devices, ios_message=ios_message)


def test_send_push_error_params(push_api, devices, ios_message):
    with pytest.raises(AppMetricaSendPushError):
        push_api.send_push(9, ios_message=ios_message)
    with pytest.raises(AppMetricaSendPushError):
        push_api.send_push(9, devices=devices)


@responses.activate
def test_check_status_success(push_api):
    data = {
        'transfer': {
            'id': 505,
            'status': 'sent',
            'errors': []
        }
    }
    responses.add(responses.GET, PushAPI.base_url + 'status/505', status=200, json=data)
    assert push_api.check_status(505) == 'sent'


@pytest.mark.parametrize('params', [
    {'status': 500},
    {'status': 200, 'json': {'transfer': {'id': 2999, 'status': 'failed', 'errors': ['Error']}}},
])
@responses.activate
def test_check_status_error(push_api, params):
    responses.add(responses.GET, PushAPI.base_url + 'status/2999', **params)
    with pytest.raises(AppMetricaCheckStatusError):
        push_api.check_status(2999)
