from http import HTTPStatus
from django.test import TestCase


class CitySearchTest(TestCase):
    def test_searches_for_cities(self):
        response = self.client.get("/search-cities/?query=Dubl", format="json")
        assert response.status_code == HTTPStatus.OK
        assert response.data == [
            {
                "city_iata": "DUB",
                "city_name": "Dublin",
                "country_iata": "IE",
                "country_name": "Ireland",
                "state_code": None,
            },
            {
                "city_iata": "DBN",
                "city_name": "Dublin",
                "country_iata": "US",
                "country_name": "United States",
                "state_code": "GA",
            },
            {
                "city_iata": "PSK",
                "city_name": "Dublin",
                "country_iata": "US",
                "country_name": "United States",
                "state_code": "VA",
            },
        ]

    def test_removes_duplicate_casablanca(self):
        response = self.client.get("/search-cities/?query=Casabl", format="json")
        assert response.status_code == HTTPStatus.OK
        assert response.data == [
            {
                "city_iata": "CMN",
                "city_name": "Casablanca",
                "country_iata": "MA",
                "country_name": "Morocco",
                "state_code": None,
            },
        ]
