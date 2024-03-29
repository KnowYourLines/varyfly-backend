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

    def test_gets_nearest_cities_with_airports_for_cities_without_airports(self):
        response = self.client.get(
            "/search-cities/?query=southend", content_type="application/json"
        )
        assert response.status_code == HTTPStatus.OK
        assert response.data == [
            {
                "city_iata": "LON",
                "city_name": "London",
                "country_iata": "GB",
                "country_name": "United Kingdom",
                "state_code": None,
            },
            {
                "city_iata": "CBG",
                "city_name": "Cambridge",
                "country_iata": "GB",
                "country_name": "United Kingdom",
                "state_code": None,
            },
            {
                "city_iata": "NWI",
                "city_name": "Norwich",
                "country_iata": "GB",
                "country_name": "United Kingdom",
                "state_code": None,
            },
            {
                "city_iata": "OST",
                "city_name": "Oostende Brugge",
                "country_iata": "BE",
                "country_name": "Belgium",
                "state_code": None,
            },
            {
                "city_iata": "SOU",
                "city_name": "Southampton",
                "country_iata": "GB",
                "country_name": "United Kingdom",
                "state_code": None,
            },
            {
                "city_iata": "BHX",
                "city_name": "Birmingham",
                "country_iata": "GB",
                "country_name": "United Kingdom",
                "state_code": None,
            },
            {
                "city_iata": "BOH",
                "city_name": "Bournemouth",
                "country_iata": "GB",
                "country_name": "United Kingdom",
                "state_code": None,
            },
            {
                "city_iata": "LIL",
                "city_name": "Lille",
                "country_iata": "FR",
                "country_name": "France",
                "state_code": None,
            },
            {
                "city_iata": "NQT",
                "city_name": "Nottingham",
                "country_iata": "GB",
                "country_name": "United Kingdom",
                "state_code": None,
            },
            {
                "city_iata": "GLO",
                "city_name": "Gloucester Cheltenham",
                "country_iata": "GB",
                "country_name": "United Kingdom",
                "state_code": None,
            },
        ]

    def test_handles_cities_with_missing_latitude_and_longitude(self):
        response = self.client.get(
            "/search-cities/?query=Kingston upon thames",
            content_type="application/json",
        )
        assert response.status_code == HTTPStatus.OK
        assert response.data == [
            {
                "city_iata": "LON",
                "city_name": "London",
                "country_iata": "GB",
                "country_name": "United Kingdom",
                "state_code": None,
            },
            {
                "city_iata": "SOU",
                "city_name": "Southampton",
                "country_iata": "GB",
                "country_name": "United Kingdom",
                "state_code": None,
            },
            {
                "city_iata": "CBG",
                "city_name": "Cambridge",
                "country_iata": "GB",
                "country_name": "United Kingdom",
                "state_code": None,
            },
            {
                "city_iata": "BOH",
                "city_name": "Bournemouth",
                "country_iata": "GB",
                "country_name": "United Kingdom",
                "state_code": None,
            },
            {
                "city_iata": "GLO",
                "city_name": "Gloucester Cheltenham",
                "country_iata": "GB",
                "country_name": "United Kingdom",
                "state_code": None,
            },
            {
                "city_iata": "BHX",
                "city_name": "Birmingham",
                "country_iata": "GB",
                "country_name": "United Kingdom",
                "state_code": None,
            },
            {
                "city_iata": "BRS",
                "city_name": "Bristol",
                "country_iata": "GB",
                "country_name": "United Kingdom",
                "state_code": None,
            },
            {
                "city_iata": "NQT",
                "city_name": "Nottingham",
                "country_iata": "GB",
                "country_name": "United Kingdom",
                "state_code": None,
            },
            {
                "city_iata": "NWI",
                "city_name": "Norwich",
                "country_iata": "GB",
                "country_name": "United Kingdom",
                "state_code": None,
            },
            {
                "city_iata": "CWL",
                "city_name": "Cardiff",
                "country_iata": "GB",
                "country_name": "United Kingdom",
                "state_code": None,
            },
        ]
