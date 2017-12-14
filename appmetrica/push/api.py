# coding: utf-8
import json
import logging
import requests
from appmetrica.push import exceptions

# APPMETRICA_APP_ID = '416934'
# APPMETRICA_PUSH_ACCESS_TOKEN = 'AQAAAAAiYljrAAS1-wqZtJm9NEN8k8_I3ZxJBWo'

logger = logging.getLogger(__name__)


class TokenTypes(object):
    APPMETRICA_DEVICE_ID = 'appmetrica_device_id'
    IOS_IFA = 'ios_ifa'
    GOOGLE_AID = 'google_aid'
    ANDROID_PUSH_TOKEN = 'android_push_token'
    IOS_PUSH_TOKEN = 'ios_push_token'


class API(object):
    base_url = 'https://push.api.appmetrica.yandex.net/push/v1/'
    request_timeout = 5
    access_token = None
    app_id = None

    def __init__(self, app_id, access_token):
        self.access_token = access_token
        self.app_id = app_id

    def create_group(self, name):
        """
        Create group to combine the sending in the report
        :param name: Unique name of the group
        :return: Identifier of the created group
        """
        assert name
        data = {
            'group': {
                'app_id': self.app_id,
                'name': name
            }
        }
        try:
            response_data = self._request('post', 'management/groups', json=data)
        except exceptions.AppMetricaRequestError as exc:
            logger.error('create_group request with json %s failed due to %s', data, exc, exc_info=True)
            raise exceptions.AppMetricaCreateGroupError
        except Exception as exc:
            logger.error('create_group request with json %s failed due to %s', data, exc, exc_info=True)
            raise exceptions.AppMetricaCreateGroupError

        # response_data contain dict like:
        # {
        #   "group": {
        #     "id": XXXXXX,
        #     "app_id": XXXXXX,
        #     "name": "the_name_of_the_group"
        #   }
        # }
        return response_data['group']['id']

    def send_push(self, messages, devices, group_id, tag=None):
        assert group_id

        # A message that is processed by the application in the background without displaying to the user.
        # Using silent push, you can send additional data, or check the delivery of notifications.
        silent = False

        content = {
            'title': u'Заголовок',  # required for not-silent
            'text': u'Содержимое',
            'data': json.dumps({'book': 225473})
        }

        data = {
            'push_request': {
                'group_id': group_id,
                'tag': tag or 'test',
                'messages': {
                    # 'android': {
                    #     'silent': silent,
                    #     'content': content
                    # },
                    'iOS': {
                        'silent': silent,
                        'content': content
                    }
                },
                'devices': [
                    {
                        'id_type': 'ios_ifa',
                        'id_values': ['BABDF74E-92AC-45DD-9E3A-9FC6A6C6FCCA']
                    }
                    # {
                    #     'id_type': 'android_push_token',
                    #     'id_values': ['']
                    # }
                ]
            }
        }

        # data = {
        #     'push_request': {
        #         'group_id': group_id,
        #         'tag': tag or 'test',
        #         'messages': {
        #             'android': {
        #                 'silent': silent,
        #                 'content': {
        #                     "title": "string",
        #                     "text": "string",
        #                     "icon": "string",
        #                     "icon_background": -7829368,
        #                     "image": "https://example.com/picture.jpg",
        #                     "banner": "https://example.com/picture.jpg",
        #                     "data": json.dumps(extra_data),
        #                     "priority": -2,
        #                     "collapse_key": 2001,
        #                     "vibration": [0, 500],
        #                     "led_color": 10000,
        #                     "led_interval": 50,
        #                     "led_pause_interval": 50,
        #                     "time_to_live": 180
        #                 },
        #                 "open_action": {
        #                     "deeplink": "yandexmaps://?"
        #                 }
        #             },
        #             'iOS': {
        #                 "silent": silent,
        #                 "content": {
        #                     "title": "string",
        #                     "text": "string",
        #                     "badge": 1,
        #                     "sound": "disable",
        #                     "media_attachment": "string",
        #                     "expiration": 3600,
        #                     "data": json.dumps(extra_data)
        #                 },
        #                 "open_action": {
        #                     "url": "https://ya.ru"
        #                 }
        #             }
        #         },
        #         "devices": [
        #             {
        #                 "id_type": "appmetrica_device_id",
        #                 "id_values": ["123456789", "42"]
        #             },
        #             {
        #                 "id_type": "ios_ifa",
        #                 "id_values": ["8A690667-6204-4A6A-9B38-85DE016....."]
        #             },
        #             {
        #                 "id_type": "google_aid",
        #                 "id_values": ["eb5f3ec8-2e3e-492f-b15b-d21860b....."]
        #             },
        #             {
        #                 "id_type": "android_push_token",
        #                 "id_values": ["eFfxdO7uCMw:APA91bF1tN3X3BAbiJXsQhk-..."]
        #             },
        #             {
        #                 "id_type": "ios_push_token",
        #                 "id_values": ["F6A79E9F844A24C5FBED5C58A4C71561C180F........."]
        #             }
        #         ]
        #     }
        # }
        try:
            response_data = self._request('post', 'send', json=data)
        except Exception as exc:
            raise exceptions.AppMetricaSendPushError

        # response_data contain dict like:
        # {
        #   "push_response": {
        #     "transfer_id": XXXXXX
        #   }
        # }
        return response_data['push_response']['transfer_id']

    def check_status(self, transfer_id):
        endpoint = 'status/{transfer_id}'.format(transfer_id=transfer_id)

        try:
            response_data = self._request('get', endpoint)
        except Exception as exc:
            raise exceptions.AppMetricaCheckStatusError

        # response_data contain dict like:
        # {
        #   "transfer": {
        #     "creation_date": "2017-11-03T18:29:25+03:00",
        #     "id": XXXXXX,
        #     "status": "failed",
        #     "tag": "some_tag",
        #     "group_id": XXXXXX,
        #     "errors": [
        #       "Invalid push credentials for platform android"
        #     ]
        #   }
        # }
        if response_data['transfer']['status'] == 'failed':
            errors = response_data['transfer']['errors']
            if errors:
                raise exceptions.AppMetricaCheckStatusError(errors[0])

        return response_data['transfer']['id'], response_data['transfer']['status']

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
            raise exceptions.AppMetricaRequestError

        print(response.content)
        try:
            response_data = response.json()
        except Exception as exc:
            logger.warning('unable to parse json response due to %s', exc, exc_info=True,
                           extra={'data': {'content': response.content}})
            raise exceptions.AppMetricaRequestError

        return response_data
