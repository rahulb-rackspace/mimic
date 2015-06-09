# -*- test-case-name: mimic.test.test_mailgun -*-
"""
API Mock for Mail Gun.
https://documentation.mailgun.com/api-sending.html
"""

import json
import time
import urlparse

from mimic.rest.mimicapp import MimicApp
from mimic.util.helper import seconds_to_timestamp

count = 0


class MailGunApi(object):
    """
    Rest endpoints for mocked Mail Gun api.
    """

    app = MimicApp()

    def __init__(self, core):
        """
        :param MimicCore core: The core to which this Mail Gun Api will be
        communicating.
        """
        self.core = core

    @app.route('/messages', methods=['POST'])
    def send_messages(self, request):
        """
        Responds with a 200 with a static response.
        """
        content = urlparse.parse_qs(request.content.read())
        to_address = content.get('to')
        headers = {}
        for key, value in content.items():
            if key.startswith("h:") or key.startswith("v:"):
                headers[key] = value
        if 'bademail@example.com' in to_address:
            request.setResponseCode(500)
            global count
            count += 1
            return b''

        if 'failingemail@example.com' in to_address:
            request.setResponseCode(400)
            return b''

        request.setResponseCode(200)
        message_id = "{0}@samples.mailgun.org".format(
            seconds_to_timestamp(time.time(),
                                 "%Y%m%d%H%M%S.%f"))
        self.core.message_store._add_to_message_store(
            message_id=message_id,
            to=content.get('to')[0], msg_from=content.get('from'),
            subject=content.get('subject')[0], body=content.get('html'),
            headers=headers)
        return json.dumps({
            "message": "Queued. Thank you.",
            "id": message_id})

    @app.route('/messages', methods=['GET'])
    def get_messages(self, request):
        """
        Responds with a 200 and the number of messages POSTed
        through the ``/messages`` endpoint.
        """
        filter_by_to = request.args.get("to")
        request.setResponseCode(200)
        return json.dumps(self.core.message_store._list_messages(filter_by_to))

    @app.route('/messages/500s', methods=['GET'])
    def get_messages_500_count(self, request):
        """
        Responds with a 200 and the number of messages resulting in 500s
        i.e. when the `to` address is bademail@example.com.
        """
        request.setResponseCode(200)
        return json.dumps({"count": count})

    @app.route('/messages/headers', methods=['GET'])
    def get_message_headers(self, request):
        """
        Responds with a 200 and returns the headers recieved when the
        message with the `to` address was POSTed.
        """
        request.setResponseCode(200)
        to_addr = request.args.get("to")
        msg = self.core.message_store.message_by_to_address(to_addr)
        return json.dumps({msg.to: msg.headers})
