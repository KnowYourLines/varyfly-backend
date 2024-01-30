from http import HTTPStatus
from django.test import TestCase


class DirectDestinationsTest(TestCase):
    def test_direct_destinations_only_origin(self):
        response = self.client.get(
            "/direct-destinations/?city_name=London&city_iata=LON&country_iata=GB",
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

    def test_no_data_for_missing_params(self):
        response = self.client.get(
            "/direct-destinations/?city_name=London",
            format="json",
        )
        assert response.status_code == HTTPStatus.OK
        assert not response.data
