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
            country_iata = request.query_params.get("country_iata")
            city_suggestions = []
            if query:
                params = {
                    "subType": "CITY",
                    "keyword": query,
                    "sort": "analytics.travelers.score",
                    "view": "FULL",
                }
                if country_iata:
                    params["countryCode"] = country_iata
                token_type, access_token = access_token_and_type()
                response = requests.get(
                    f"https://{os.environ.get('AMADEUS_BASE_URL')}/v1/reference-data/locations",
                    params=params,
                    headers={"Authorization": f"{token_type} {access_token}"},
                )
                response.raise_for_status()
                cities = response.json().get("data", [])
                invalid_city_iatas = {"CAS"}
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
                    for city in cities
                    if city["iataCode"] not in invalid_city_iatas
                ]
            return Response(city_suggestions)
        except requests.HTTPError as exc:
            logging.error(
                f"Error response {exc.response.status_code} while requesting {exc.request.url}: {exc.response.text}"
            )


class DirectDestinationsView(APIView):
    def get(self, request):
        city_name = request.query_params.get("city_name")
        country_iata = request.query_params.get("country_iata")
        city_iata = request.query_params.get("city_iata")
        token_type, access_token = access_token_and_type()
        direct_destinations = []
        if city_iata and city_name and country_iata and len(country_iata) == 2:
            direct_destinations = get_direct_destinations(
                city_iata,
                city_name,
                country_iata,
                token_type,
                access_token,
            )
        return Response(direct_destinations)
