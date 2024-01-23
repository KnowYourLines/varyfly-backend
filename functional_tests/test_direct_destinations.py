from http import HTTPStatus
from django.test import TestCase


class DirectDestinationsTest(TestCase):
    def test_direct_destinations(self):
        response = self.client.get(
            "/direct-destinations/?city_name=London&city_iata=LON&country_iata=GB",
            format="json",
        )
        assert response.status_code == HTTPStatus.OK
        assert response.data == sorted(
            response.data,
            key=lambda destination_city: destination_city["travel_distance_km"],
        )
        assert response.data[-1] == {
            "type": "location",
            "subtype": "city",
            "name": "PERTH",
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
            "travel_distance_km": 14478.856834255264,
            "travel_distance_miles": 8996.744533334864,
        }
