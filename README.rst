==========
APPMETRICA
==========

Application for integrating with Yandex AppMetrica https://appmetrica.yandex.ru/

.. image:: https://travis-ci.org/MyBook/appmetrica.svg?branch=master
    :target: https://travis-ci.org/MyBook/appmetrica
.. image:: https://codecov.io/gh/MyBook/appmetrica/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/MyBook/appmetrica

Sens push
---------

1. Get `application id` from your account in appmetrica.yandex.ru

2. Generate `access token`::

    https://tech.yandex.ru/appmetrica/doc/mobile-api/intro/authorization-docpage/

3. Create `API` instance and send push::

    from appmetrica.push.api import API

    api = API(application_id, access_token)

4. Create group to combine the sending in the report::

    grp_id = api.create_group('test-push-1')

5. Pass `group_id`, `device list` and `message` to send_push method and call::

    transfer_id = api.send_push(grp_id, devices=devices, ios_message=ios_message,
                                android_message=android_message, tag='harry potter')

    devices - list of token objects like:
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

    ios_message - push message for ios devices
    android_message - push message for android devices:
        {
            "silent": false,
            "content": {
                "title": "string",
                "text": "string",
                "sound": "disable",
                "data": "string"
            }
        }

6. For check status of push call `check_status` method::

    status = api.check_status(transfer_id)
