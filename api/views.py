import json
import logging
import os
import uuid

import pycountry
import requests

from rest_framework.response import Response
from rest_framework.views import APIView

from api.helpers import access_token_and_type, get_direct_destinations


class BookingLinkView(APIView):
    def get(self, request):
        try:
            auth_token = os.environ.get("DUFFEL_ACCESS_TOKEN")
            url = "https://api.duffel.com/links/sessions"
            headers = {
                "Duffel-Version": "v1",
                "Authorization": f"Bearer {auth_token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Accept-Encoding": "gzip",
            }
            payload = {
                "data": {
                    "traveller_currency": "GBP",
                    "success_url": "https://varyfly.com/",
                    "should_hide_traveller_currency_selector": "false",
                    "secondary_color": "#000000",
                    "reference": str(uuid.uuid4()),
                    "primary_color": "#000000",
                    "markup_rate": "0.01",
                    "markup_currency": "GBP",
                    "markup_amount": "1.00",
                    "logo_url": "",
                    "failure_url": "https://varyfly.com/",
                    "checkout_display_text": "Thank you for booking with us.",
                    "abandonment_url": "https://varyfly.com/",
                }
            }
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            response = response.json()["data"]
            return Response(response)
        except requests.HTTPError as exc:
            logging.error(
                f"Error response {exc.response.status_code} while requesting {exc.request.url}: {exc.response.text}"
            )


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
