import os

from geopy import distance
import pycountry
import requests

from rest_framework.response import Response
from rest_framework.views import APIView

from api.helpers import access_token_and_type, get_city_details


class CitySearchView(APIView):
    def get(self, request):
        query = request.query_params.get("query")
        token_type, access_token = access_token_and_type()
        response = requests.get(
            f"https://{os.environ.get('AMADEUS_BASE_URL')}/v1/reference-data/locations",
            params={
                "subType": "CITY",
                "keyword": query,
                "sort": "analytics.travelers.score",
                "view": "FULL",
            },
            headers={"Authorization": f"{token_type} {access_token}"},
        )
        city_suggestions = [
            {
                "city_iata": city["iataCode"],
                "city_name": city["name"].title(),
                "country_iata": city["address"]["countryCode"],
                "country_name": pycountry.countries.get(
                    alpha_2=city["address"]["countryCode"]
                ).name,
                "state_code": city["address"].get("stateCode"),
            }
            for city in response.json().get("data", [])
        ]
        return Response(city_suggestions)


class DirectDestinationsView(APIView):
    def get(self, request):
        city_name = request.query_params.get("city_name")
        country_iata = request.query_params.get("country_iata")
        city_iata = request.query_params.get("city_iata")
        token_type, access_token = access_token_and_type()
        home_city_details = get_city_details(
            city_iata, country_iata, token_type, access_token
        )
        home_latitude = home_city_details["geoCode"]["latitude"]
        home_longitude = home_city_details["geoCode"]["longitude"]
        response = requests.get(
            f"https://{os.environ.get('AMADEUS_BASE_URL')}/v1/reference-data/locations",
            params={
                "subType": "AIRPORT",
                "keyword": city_name,
                "countryCode": country_iata,
            },
            headers={"Authorization": f"{token_type} {access_token}"},
        )
        airports = [
            airport["iataCode"]
            for airport in response.json().get("data", [])
            if airport["address"]["cityCode"] == city_iata
        ]
        direct_destinations = []
        added_cities = set()
        for airport_iata in airports:
            response = requests.get(
                f"https://{os.environ.get('AMADEUS_BASE_URL')}/v1/airport/direct-destinations",
                params={
                    "departureAirportCode": airport_iata,
                },
                headers={"Authorization": f"{token_type} {access_token}"},
            )
            destinations = response.json().get("data", [])
            for city in destinations:
                irrelevant = (
                    city.get("metrics", {}).get("relevance", 0) == 0
                    and city["address"]["countryCode"] == country_iata
                )

                if city["iataCode"] not in added_cities and not irrelevant:
                    added_cities.add(city["iataCode"])
                    direct_destinations.append(city)
        for destination in direct_destinations:
            destination_latitude = destination["geoCode"]["latitude"]
            destination_longitude = destination["geoCode"]["longitude"]
            travel_distance = distance.distance(
                (home_latitude, home_longitude),
                (destination_latitude, destination_longitude),
            )
            estimated_flight_speed_mph = 575
            takeoff_landing_hrs = 5 / 6
            estimated_flight_time = (
                travel_distance.miles / estimated_flight_speed_mph + takeoff_landing_hrs
            )
            destination["estimated_flight_time_hrs"] = estimated_flight_time
            destination[
                "estimated_flight_time_hrs_mins"
            ] = f"{int(estimated_flight_time // 1)}h {int(estimated_flight_time % 1 * 60)}m"
            destination["name"] = destination["name"].title()
            destination["state"] = destination["address"].get("stateCode")
            destination["country"] = destination["address"]["countryName"].title()
            del destination["timeZone"]["referenceLocalDateTime"]
        direct_destinations = sorted(
            direct_destinations,
            key=lambda destination_city: destination_city["estimated_flight_time_hrs"],
        )
        return Response(direct_destinations)
