import logging
import os

import pycountry
import requests

from rest_framework.response import Response
from rest_framework.views import APIView

from api.helpers import access_token_and_type, get_direct_destinations


class CitySearchView(APIView):
    def get(self, request):
        try:
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
            response.raise_for_status()
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
        except requests.HTTPError as exc:
            logging.error(
                f"Error response {exc.response.status_code} while requesting {exc.request.url}: {exc.response.text}"
            )


class DirectDestinationsView(APIView):
    def get(self, request):
        origin_city_name = request.query_params.get("origin_city_name")
        origin_country_iata = request.query_params.get("origin_country_iata")
        origin_city_iata = request.query_params.get("origin_city_iata")
        token_type, access_token = access_token_and_type()
        origin_direct_destinations = []
        if origin_city_iata and origin_city_name and origin_country_iata:
            origin_direct_destinations = get_direct_destinations(
                origin_city_iata,
                origin_city_name,
                origin_country_iata,
                token_type,
                access_token,
            )
        destination_city_name = request.query_params.get("destination_city_name")
        destination_country_iata = request.query_params.get("destination_country_iata")
        destination_city_iata = request.query_params.get("destination_city_iata")
        destination_direct_destinations = []
        if destination_city_iata and destination_city_name and destination_country_iata:
            destination_direct_destinations = get_direct_destinations(
                destination_city_iata,
                destination_city_name,
                destination_country_iata,
                token_type,
                access_token,
            )
        if destination_direct_destinations and origin_direct_destinations:
            direct_destinations = [
                destination
                for destination in origin_direct_destinations
                if destination in destination_direct_destinations
            ]
        else:
            direct_destinations = (
                origin_direct_destinations or destination_direct_destinations
            )
        return Response(direct_destinations)
