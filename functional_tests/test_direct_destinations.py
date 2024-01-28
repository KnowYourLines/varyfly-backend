from http import HTTPStatus
from django.test import TestCase


class DirectDestinationsTest(TestCase):
    def test_direct_destinations_only_origin(self):
        response = self.client.get(
            "/direct-destinations/?destination_city_name=Dubai&"
            "origin_city_name=London&origin_city_iata=LON&origin_country_iata=GB",
            format="json",
        )
        assert response.status_code == HTTPStatus.OK
        assert response.data == sorted(
            response.data,
            key=lambda destination_city: destination_city["estimated_flight_time_hrs"],
        )
        assert response.data[0] == {
            "type": "location",
            "subtype": "city",
            "name": "Manchester",
            "iataCode": "MAN",
            "geoCode": {"latitude": 53.35362, "longitude": -2.275},
            "address": {
                "countryName": "UNITED KINGDOM",
                "countryCode": "GB",
                "regionCode": "EUROP",
            },
            "timeZone": {"offSet": "+00:00"},
            "metrics": {"relevance": 4},
            "estimated_flight_time_hrs": 1.1047879718721132,
            "estimated_flight_time_hrs_mins": "1h 6m",
            "state": None,
            "country": "United Kingdom",
        }
        assert response.data[-1] == {
            "type": "location",
            "subtype": "city",
            "name": "Perth",
            "iataCode": "PER",
            "geoCode": {"latitude": -31.94027, "longitude": 115.967},
            "address": {
                "countryName": "AUSTRALIA",
                "countryCode": "AU",
                "stateCode": "WA",
                "regionCode": "AUSTL",
            },
            "timeZone": {"offSet": "+08:00"},
            "metrics": {"relevance": 13},
            "estimated_flight_time_hrs": 16.479845565220053,
            "estimated_flight_time_hrs_mins": "16h 28m",
            "state": "WA",
            "country": "Australia",
        }

    def test_no_data_for_missing_origin_params(self):
        response = self.client.get(
            "/direct-destinations/?origin_city_name=London",
            format="json",
        )
        assert response.status_code == HTTPStatus.OK
        assert not response.data

    def test_no_data_for_missing_destination_params(self):
        response = self.client.get(
            "/direct-destinations/?destination_city_name=London",
            format="json",
        )
        assert response.status_code == HTTPStatus.OK
        assert not response.data

    def test_direct_destinations_only_destination(self):
        response = self.client.get(
            "/direct-destinations/?origin_city_name=Dubai&"
            "destination_city_name=London&destination_city_iata=LON&destination_country_iata=GB",
            format="json",
        )
        assert response.status_code == HTTPStatus.OK
        assert response.data == sorted(
            response.data,
            key=lambda destination_city: destination_city["estimated_flight_time_hrs"],
        )
        assert response.data[0] == {
            "type": "location",
            "subtype": "city",
            "name": "Manchester",
            "iataCode": "MAN",
            "geoCode": {"latitude": 53.35362, "longitude": -2.275},
            "address": {
                "countryName": "UNITED KINGDOM",
                "countryCode": "GB",
                "regionCode": "EUROP",
            },
            "timeZone": {"offSet": "+00:00"},
            "metrics": {"relevance": 4},
            "estimated_flight_time_hrs": 1.1047879718721132,
            "estimated_flight_time_hrs_mins": "1h 6m",
            "state": None,
            "country": "United Kingdom",
        }
        assert response.data[-1] == {
            "type": "location",
            "subtype": "city",
            "name": "Perth",
            "iataCode": "PER",
            "geoCode": {"latitude": -31.94027, "longitude": 115.967},
            "address": {
                "countryName": "AUSTRALIA",
                "countryCode": "AU",
                "stateCode": "WA",
                "regionCode": "AUSTL",
            },
            "timeZone": {"offSet": "+08:00"},
            "metrics": {"relevance": 13},
            "estimated_flight_time_hrs": 16.479845565220053,
            "estimated_flight_time_hrs_mins": "16h 28m",
            "state": "WA",
            "country": "Australia",
        }

    def test_common_direct_destinations(self):
        response = self.client.get(
            "/direct-destinations/?origin_city_name=New York&origin_city_iata=NYC&origin_country_iata=US&"
            "destination_city_name=London&destination_city_iata=LON&destination_country_iata=GB",
            format="json",
        )
        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 121
        assert response.data[0] == {
            "type": "location",
            "subtype": "city",
            "name": "Boston",
            "iataCode": "BOS",
            "geoCode": {"latitude": 42.36528, "longitude": -71.01777},
            "address": {
                "countryName": "UNITED STATES OF AMERICA",
                "countryCode": "US",
                "stateCode": "MA",
                "regionCode": "NAMER",
            },
            "timeZone": {"offSet": "-05:00"},
            "metrics": {"relevance": 7},
            "estimated_flight_time_hrs": 1.1677705881354619,
            "estimated_flight_time_hrs_mins": "1h 10m",
            "state": "MA",
            "country": "United States Of America",
        }

        assert response.data[-1] == {
            "type": "location",
            "subtype": "city",
            "name": "Singapore",
            "iataCode": "SIN",
            "geoCode": {"latitude": 1.35028, "longitude": 103.9945},
            "address": {
                "countryName": "SINGAPORE",
                "countryCode": "SG",
                "regionCode": "SEASI",
            },
            "timeZone": {"offSet": "+08:00"},
            "metrics": {"relevance": 5},
            "estimated_flight_time_hrs": 17.41197832473083,
            "estimated_flight_time_hrs_mins": "17h 24m",
            "state": None,
            "country": "Singapore",
        }
