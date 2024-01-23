from http import HTTPStatus
from django.test import TestCase


class CitySearchTest(TestCase):
    def test_searches_for_cities(self):
        response = self.client.post("/search/cities/", {"query": "Lond"}, format="json")
        assert response.status_code == HTTPStatus.OK
        assert response.data == [
            {
                "city_iata": "LON",
                "city_name": "London",
                "country_iata": "GB",
                "country_name": "United Kingdom",
            }
        ]
