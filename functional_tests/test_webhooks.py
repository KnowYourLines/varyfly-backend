from http import HTTPStatus

from django.test import TestCase


class WebhooksTest(TestCase):
    def test_order_created_webhook(self):
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

    # def test_checks_idempotency(self):
    #     response = self.client.post(
    #         "/webhooks/",
    #         data={
    #             "data": {"object": {"id": "ord_0000AeRyKFdHOCbUCO9CHj"}},
    #             "id": "wev_0000AeRyKLH8gidmN4xgYK",
    #             "type": "order.created",
    #             "live_mode": False,
    #             "created_at": "2024-02-01T21:00:00.430510Z",
    #             "api_version": "v1",
    #             "idempotency_key": "ord_0000AeRyKFdHOCbUCO9CHj",
    #             "identity_organisation_id": "hello_world",
    #         },
    #         content_type="application/json",
    #     )
    #     assert response.status_code == HTTPStatus.OK
