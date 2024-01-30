from http import HTTPStatus

from django.test import TestCase


class BookingLinkTest(TestCase):
    def test_gets_booking_link(self):
        response = self.client.get("/booking/", format="json")
        assert response.status_code == HTTPStatus.OK
        assert response.data["url"].startswith("https://links.duffel.com?token=")
