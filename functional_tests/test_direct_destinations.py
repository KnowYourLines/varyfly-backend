from http import HTTPStatus
from django.test import TestCase


class DirectDestinationsTest(TestCase):
    def test_direct_destinations_only_origin(self):
        response = self.client.get(
            "/direct-destinations/?city_name=London&city_iata=LON&country_iata=GB",
            format="json",
        )
        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 367
        assert response.data == sorted(
            response.data,
            key=lambda destination_city: (
                -destination_city["metrics"]["relevance"],
                destination_city["estimated_flight_time_hrs"],
            ),
        )
        assert response.data[0] == {
            "type": "location",
            "subtype": "city",
            "name": "New York",
            "iataCode": "NYC",
            "geoCode": {"latitude": 40.71417, "longitude": -74.00583},
            "address": {
                "countryName": "UNITED STATES OF AMERICA",
                "countryCode": "US",
                "stateCode": "NY",
                "regionCode": "NAMER",
            },
            "timeZone": {"offSet": "-05:00"},
            "metrics": {"relevance": 100},
            "estimated_flight_time_hrs": 6.866388995181392,
            "estimated_flight_time_hrs_mins": "6h 51m",
            "state": "NY",
            "country": "United States Of America",
        }
        print(response.data[-1])
        assert response.data[-1] == {
            "type": "location",
            "subtype": "city",
            "name": "Shenzhen",
            "iataCode": "SZX",
            "geoCode": {"latitude": 22.63917, "longitude": 113.8106},
            "address": {
                "countryName": "CHINA",
                "countryCode": "CN",
                "regionCode": "ASIA",
            },
            "timeZone": {"offSet": "+08:00"},
            "metrics": {"relevance": 0},
            "estimated_flight_time_hrs": 11.19921362967568,
            "estimated_flight_time_hrs_mins": "11h 11m",
            "state": None,
            "country": "China",
        }

    def test_no_data_for_missing_params(self):
        response = self.client.get(
            "/direct-destinations/?city_name=London",
            format="json",
        )
        assert response.status_code == HTTPStatus.OK
        assert not response.data
