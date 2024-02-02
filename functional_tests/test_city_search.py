from http import HTTPStatus
from django.test import TestCase


class CitySearchTest(TestCase):
    def test_searches_for_cities(self):
        response = self.client.get(
            "/search-cities/?query=Dubl", content_type="application/json"
        )
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

    def test_searches_for_cities_by_country(self):
        response = self.client.get(
            "/search-cities/?query=Dubl&country_iata=IE",
            content_type="application/json",
        )
        assert response.status_code == HTTPStatus.OK
        assert response.data == [
            {
                "city_iata": "DUB",
                "city_name": "Dublin",
                "country_iata": "IE",
                "country_name": "Ireland",
                "state_code": None,
            }
        ]

    def test_removes_duplicate_casablanca(self):
        response = self.client.get(
            "/search-cities/?query=Casabl", content_type="application/json"
        )
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
