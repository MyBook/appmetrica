==========
AppMetrica
==========

Application for integrating with Yandex AppMetrica https://appmetrica.yandex.ru/

Yandex Docs https://tech.yandex.ru/appmetrica/doc/mobile-api/push/use-cases-docpage/

.. image:: https://travis-ci.org/MyBook/appmetrica.svg?branch=master
    :target: https://travis-ci.org/MyBook/appmetrica
.. image:: https://codecov.io/gh/MyBook/appmetrica/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/MyBook/appmetrica

Before using API it is necessary:

1. Get `application id` from your account in appmetrica.yandex.ru

2. [Generate access token](https://tech.yandex.ru/appmetrica/doc/mobile-api/intro/authorization-docpage/)

Send push
---------

1. Create `API` instance::

    from appmetrica.push.api import PushAPI

    api = PushAPI(application_id, access_token)

2. Create group to combine the sending in the report::

    group_id = api.create_group('test-push-1', send_rate=500)

3. Pass `group_id`, `device list` and `message` to send_push method and call::

    from appmetrica.push.api import TokenTypes

    transfer_id = api.send_push(group_id, devices=devices, ios_message=ios_message,
                                android_message=android_message, tag='harry potter')

    devices - list of token objects like:
        [
            {
                "id_type": TokenTypes.APPMETRICA_DEVICE_ID,
                "id_values": ["123456789", "42"]
            },
            {
                "id_type": TokenTypes.IOS_IFA,
                "id_values": ["8A690667-6204-4A6A-9B38-85DE016....."]
            },
            {
                "id_type": TokenTypes.ANDROID_PUSH_TOKEN,
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

4. To check status of push call `check_status` method::

    status = api.check_status(transfer_id)


List of available groups
------------------------

1. Create `API` instance::

    from appmetrica.push.api import PushAPI

    api = PushAPI(application_id, access_token)

2. Get list of groups

    group_id = api.get_groups()


Export tokens
-------------

1. Create `API` instance::

    from appmetrica.export.api import ExportAPI

    api = ExportAPI(application_id, access_token)

2. Call push_tokens method with necessary fields::

    data = api.export_push_tokens('token', 'ios_ifa', 'google_aid')


Export devices
--------------

1. Create `API` instance::

    from appmetrica.export.api import ExportAPI

    api = ExportAPI(application_id, access_token)

2. Call push_tokens method with necessary fields::

    date_till = datetime.now()
    date_from = date_till - timedelta(days=7)

    data = api.export_installations('ios_ifv', date_from=date_from, date_till=date_till)



Publish a release on PyPi
-------------------------

Install `twine <https://pypi.org/project/twine/>`_ globally::

  pip install twine

1. Don't forget to bump the package version::

    __version__ = '1.0.5'

2. Build the release::

    python setup.py sdist bdist_wheel

3. Publish the release on PyPi::

    twine upload dist/*
