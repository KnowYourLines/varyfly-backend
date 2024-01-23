import os

from geopy import distance
import pycountry
import requests

from rest_framework.response import Response
from rest_framework.views import APIView

from api.helpers import access_token_and_type, get_city_details


class CitySearchView(APIView):
    def get(self, request):
        auth_token = os.environ.get("DUFFEL_ACCESS_TOKEN")
        query = request.query_params.get("query")
        url = "https://api.duffel.com/places/suggestions"
        headers = {
            "Duffel-Version": "v1",
            "Authorization": f"Bearer {auth_token}",
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
        }
        params = {"name": query}
        response = requests.get(url, headers=headers, params=params)
        suggestions = response.json()["data"]
        city_suggestions = [
            {
                "city_iata": suggestion["iata_city_code"],
                "city_name": suggestion["name"],
                "country_iata": suggestion["iata_country_code"],
                "country_name": pycountry.countries.get(
                    alpha_2=suggestion["iata_country_code"]
                ).name,
            }
            for suggestion in suggestions
            if suggestion.get("type") == "city"
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
        added_cities = {city_iata}
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
                if city["iataCode"] not in added_cities:
                    added_cities.add(city["iataCode"])
                    direct_destinations.append(city)
        for destination in direct_destinations:
            destination_latitude = destination["geoCode"]["latitude"]
            destination_longitude = destination["geoCode"]["longitude"]
            travel_distance = distance.distance(
                (home_latitude, home_longitude),
                (destination_latitude, destination_longitude),
            )
            destination["travel_distance_km"] = travel_distance.km
            destination["travel_distance_miles"] = travel_distance.miles
            del destination["timeZone"]["referenceLocalDateTime"]
        direct_destinations = sorted(
            direct_destinations,
            key=lambda destination_city: destination_city["travel_distance_km"],
        )
        return Response(direct_destinations)
