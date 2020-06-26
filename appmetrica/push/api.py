# coding: utf-8
import datetime
import json
import logging

from appmetrica.base import BaseAPI
from appmetrica.push import exceptions

logger = logging.getLogger(__name__)

MAX_NUMBER_IN_BATCH = 250000
MAX_NUMBER_OF_GROUPS = 5


class TokenTypes(object):
    APPMETRICA_DEVICE_ID = 'appmetrica_device_id'
    IOS_IFA = 'ios_ifa'
    GOOGLE_AID = 'google_aid'
    ANDROID_PUSH_TOKEN = 'android_push_token'
    IOS_PUSH_TOKEN = 'ios_push_token'


class PushAPI(BaseAPI):
    base_url = 'https://push.api.appmetrica.yandex.net/push/v1/'

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
        except Exception as exc:
            logger.error('create_group request with json %s failed due to %s', data, exc, exc_info=True)
            raise exceptions.AppMetricaCreateGroupError

        # response_data contains dict like:
        # {
        #   "group": {
        #     "id": XXXXXX,
        #     "app_id": XXXXXX,
        #     "name": "the_name_of_the_group"
        #   }
        # }
        return response_data['group']['id']

    def get_groups(self):
        """
        List of all available groups
        :return: List of dict with groups metadata
        """
        try:
            response_data = self._request('get', 'management/groups', params={'app_id': self.app_id})
        except Exception as exc:
            logger.error('get_groups request failed due to %s', exc, exc_info=True)
            raise exceptions.AppMetricaGetGroupsError

        # response_data contains dict like:
        # {
        #   "groups": [
        #     {
        #       "id": 1,
        #       "app_id": 3,
        #       "name": "name of group"
        #     },
        #     {
        #       "id": 2,
        #       "app_id": 3,
        #       "name": "name of other group"
        #     }
        #   ]
        # }
        return response_data['groups']

    def send_push(self, group_id, devices=None, ios_message=None, android_message=None, tag=None):
        """
        Sends push messages to the specified devices
        :param group_id: group to combine the sending in the report
        :param devices: list of token objects like:
            [
                {
                    "id_type": "appmetrica_device_id",
                    "id_values": ["123456789", "42"]
                },
                {
                    "id_type": "ios_ifa",
                    "id_values": ["8A690667-6204-4A6A-9B38-85DE016....."]
                },
                {
                    "id_type": "android_push_token",
                    "id_values": ["eFfxdO7uCMw:APA91bF1tN3X3BAbiJXsQhk-..."]
                }
            ]
        :param ios_message: push message for ios devices. dict like:
            {
                "silent": false,
                "content": {
                    "title": "string",
                    "text": "string",
                    "sound": "disable",
                    "data": "string"
                }
            }
        :param android_message: similarly ios_message param
        :param tag: send tag to combine the sending in the report
        :return: Identifier of the sending push (transfer_id)
        """
        if not devices:
            logger.error('send push error: devices are not provided')
            raise exceptions.AppMetricaSendPushError('devices are not provided')
        if not ios_message and not android_message:
            logger.error('send push error: messages are not provided')
            raise exceptions.AppMetricaSendPushError('messages are not provided')

        messages = {}
        if ios_message:
            messages['iOS'] = ios_message
        if android_message:
            messages['android'] = android_message

        tag = tag or datetime.datetime.now().isoformat()  # default tag
        data = {
            'push_batch_request': {
                'group_id': group_id,
                'tag': tag,
                'batch': [{
                    'messages': messages,
                    'devices': devices
                }]
            }
        }
        return self.send(data)

    def send(self, data):
        """
        Send batch of push messages

        :param data: dict with data, see https://appmetrica.yandex.ru/docs/mobile-api/push/post-send-batch.html
        :return: Identifier of the sending push (transfer_id)
        """
        self._validate(data)
        try:
            response_data = self._request('post', 'send-batch', json=data)
        except Exception as exc:
            logger.error('send_push request with json %s failed due to %s', data, exc, exc_info=True)
            raise exceptions.AppMetricaSendPushError
        return response_data['push_response']['transfer_id']

    def check_status(self, transfer_id):
        """
        Check status of sending pushes
        raise AppMetricaCheckStatusError if got an error

        :param transfer_id: Push identifier (return after call `send_push`)
        :return: status of push:
            failed — validation error. See `errors` field for detail
            in_progress — validation success. Sending messages in process
            pending — the request is accepted and waits for validation
            sent — sending completed
        """
        endpoint = 'status/{transfer_id}'.format(transfer_id=transfer_id)

        try:
            response_data = self._request('get', endpoint)
        except Exception as exc:
            logger.error('check_status request for transfer_id %s failed due to %s',
                         transfer_id, exc, exc_info=True)
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

        return response_data['transfer']['status']

    @staticmethod
    def build_ios_message(**kwargs):
        """
        Create message object for ios platform
        :param kwargs:
            title (required) - subject of push
            text (required) - body of push
            data (optional) - extra data for client
        :return: Message object (dict)
        """
        # A message that is processed by the application in the background without displaying to the user.
        # Using silent push, you can send additional data, or check the delivery of notifications.
        silent = kwargs.get('silent') or False

        content = {
            'title': kwargs['title'],
            'text': kwargs['text'],
            'sound': kwargs.get('sound') or 'disable',
        }
        if 'extra_data' in kwargs:
            content['data'] = json.dumps(kwargs['extra_data'])

        return {
            "silent": silent,
            "content": content,
        }

    def _validate(self, data):
        required_fileds = ['group_id', 'tag', 'batch']
        for field in required_fileds:
            if field not in data['push_batch_request']:
                raise exceptions.AppMetricaSendPushError('field %s is required' % field)

        batch = data['push_batch_request']['batch']
        if not batch:
            logger.error('send push error: batch cant be empty')
            raise exceptions.AppMetricaSendPushError('batch cant be empty')

        try:
            num_devices = 0
            for messages in batch:
                device_groups = messages['devices']
                if len(device_groups) > MAX_NUMBER_OF_GROUPS:
                    logger.error('send push error: too many devices groups')
                    raise exceptions.AppMetricaSendPushError('too many devices groups')
                num_devices += sum([len(devices['id_values']) for devices in device_groups])
            if num_devices > MAX_NUMBER_IN_BATCH:
                logger.error('send push error: too many devices')
                raise exceptions.AppMetricaSendPushError('too many devices')
        except KeyError:
            raise exceptions.AppMetricaSendPushError('invalid format of data')
