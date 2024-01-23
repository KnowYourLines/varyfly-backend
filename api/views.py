import os

import pycountry
import requests

from rest_framework.response import Response
from rest_framework.views import APIView


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
