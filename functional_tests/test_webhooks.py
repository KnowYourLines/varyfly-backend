from http import HTTPStatus

from django.test import TestCase


class WebhooksTest(TestCase):
    def test_webhooks(self):
        response = self.client.post(
            "/webhooks/", data={"hello": "world"}, format="json"
        )
        assert response.status_code == HTTPStatus.OK
