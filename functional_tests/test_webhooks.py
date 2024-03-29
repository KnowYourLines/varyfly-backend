from http import HTTPStatus

from django.core import mail
from django.test import TestCase
from django.test.utils import override_settings


# @override_settings(EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend")
class WebhooksTest(TestCase):
    def test_order_created_webhook_sends_confirmation(self):
        response = self.client.post(
            "/webhooks/",
            data={
                "data": {"object": {"id": "ord_0000AeRyKFdHOCbUCO9CHj"}},
                "id": "wev_0000AeRyKLH8gidmN4xgYK",
                "type": "order.created",
                "live_mode": False,
                "created_at": "2024-02-01T21:00:00.430510Z",
                "api_version": "v1",
                "idempotency_key": "ord_0000AeRyKFdHOCbUCO9CHj",
                "identity_organisation_id": "hello_world",
            },
            content_type="application/json",
        )
        assert response.status_code == HTTPStatus.OK
        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == "Flight Booking WZQ4ET"
        assert mail.outbox[0].to == ["johnkcli@hotmail.com"]
        assert mail.outbox[0].from_email == "Varyfly <varyfly.booking@gmail.com>"

    def test_invalid_order(self):
        response = self.client.post(
            "/webhooks/",
            data={
                "data": {"object": {"id": "hello_world"}},
                "id": "wev_0000AeRyKLH8gidmN4xgYK",
                "type": "order.created",
                "live_mode": False,
                "created_at": "2024-02-01T21:00:00.430510Z",
                "api_version": "v1",
                "idempotency_key": "ord_0000AeRyKFdHOCbUCO9CHj",
                "identity_organisation_id": "hello_world",
            },
            content_type="application/json",
        )
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_missing_order(self):
        response = self.client.post(
            "/webhooks/",
            data={
                "data": {"object": {"id": ""}},
                "id": "wev_0000AeRyKLH8gidmN4xgYK",
                "type": "order.created",
                "live_mode": False,
                "created_at": "2024-02-01T21:00:00.430510Z",
                "api_version": "v1",
                "idempotency_key": "ord_0000AeRyKFdHOCbUCO9CHj",
                "identity_organisation_id": "hello_world",
            },
            content_type="application/json",
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_missing_idempotency(self):
        response = self.client.post(
            "/webhooks/",
            data={
                "data": {"object": {"id": "ord_0000AeRyKFdHOCbUCO9CHj"}},
                "id": "wev_0000AeRyKLH8gidmN4xgYK",
                "type": "order.created",
                "live_mode": False,
                "created_at": "2024-02-01T21:00:00.430510Z",
                "api_version": "v1",
                "idempotency_key": "",
                "identity_organisation_id": "hello_world",
            },
            content_type="application/json",
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_checks_idempotency(self):
        response = self.client.post(
            "/webhooks/",
            data={
                "data": {"object": {"id": "ord_0000AeRyKFdHOCbUCO9CHj"}},
                "id": "wev_0000AeRyKLH8gidmN4xgYK",
                "type": "order.created",
                "live_mode": False,
                "created_at": "2024-02-01T21:00:00.430510Z",
                "api_version": "v1",
                "idempotency_key": "ord_0000AeRyKFdHOCbUCO9CHj",
                "identity_organisation_id": "hello_world",
            },
            content_type="application/json",
        )
        assert response.status_code == HTTPStatus.OK
        response = self.client.post(
            "/webhooks/",
            data={
                "data": {"object": {"id": "ord_0000AeRyKFdHOCbUCO9CHj"}},
                "id": "wev_0000AeRyKLH8gidmN4xgYK",
                "type": "order.created",
                "live_mode": False,
                "created_at": "2024-02-01T21:00:00.430510Z",
                "api_version": "v1",
                "idempotency_key": "ord_0000AeRyKFdHOCbUCO9CHj",
                "identity_organisation_id": "hello_world",
            },
            content_type="application/json",
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert (
            response.data["idempotency_key"][0] == "Duplicate webhook request received."
        )
        response = self.client.post(
            "/webhooks/",
            data={
                "data": {"object": {"id": "ord_0000AeRyKFdHOCbUCO9CHj"}},
                "id": "wev_0000AeRyKLH8gidmN4xgYK",
                "type": "order.created",
                "live_mode": False,
                "created_at": "2024-02-01T21:00:00.430510Z",
                "api_version": "v1",
                "idempotency_key": "ord_0000AeRyKFdHOCbUCO9CHk",
                "identity_organisation_id": "hello_world",
            },
            content_type="application/json",
        )
        assert response.status_code == HTTPStatus.OK
