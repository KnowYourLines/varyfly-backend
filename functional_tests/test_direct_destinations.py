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
            "name": "Amsterdam",
            "iataCode": "AMS",
            "geoCode": {"latitude": 52.31028, "longitude": 4.76028},
            "address": {
                "countryName": "NETHERLANDS",
                "countryCode": "NL",
                "regionCode": "EUROP",
            },
            "timeZone": {"offSet": "+01:00"},
            "metrics": {"relevance": 100},
            "estimated_flight_time_hrs": 1.212412196056636,
            "estimated_flight_time_hrs_mins": "1h 12m",
            "state": None,
            "country": "Netherlands",
        }
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
