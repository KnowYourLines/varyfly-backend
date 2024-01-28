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
        if (
            origin_city_iata
            and origin_city_name
            and origin_country_iata
            and len(origin_country_iata) == 2
        ):
            origin_direct_destinations = get_direct_destinations(
                origin_city_iata,
                origin_city_name,
                origin_country_iata,
                token_type,
                access_token,
            )
            for destination in origin_direct_destinations:
                destination["origin_estimated_flight_time_hrs"] = destination.pop(
                    "estimated_flight_time_hrs"
                )
                destination["origin_estimated_flight_time_hrs_mins"] = destination.pop(
                    "estimated_flight_time_hrs_mins"
                )
                destination["destination_estimated_flight_time_hrs"] = None
                destination["destination_estimated_flight_time_hrs_mins"] = None
        destination_city_name = request.query_params.get("destination_city_name")
        destination_country_iata = request.query_params.get("destination_country_iata")
        destination_city_iata = request.query_params.get("destination_city_iata")
        destination_direct_destinations = []
        if (
            destination_city_iata
            and destination_city_name
            and destination_country_iata
            and len(destination_country_iata) == 2
        ):
            destination_direct_destinations = get_direct_destinations(
                destination_city_iata,
                destination_city_name,
                destination_country_iata,
                token_type,
                access_token,
            )
            for destination in destination_direct_destinations:
                destination["destination_estimated_flight_time_hrs"] = destination.pop(
                    "estimated_flight_time_hrs"
                )
                destination[
                    "destination_estimated_flight_time_hrs_mins"
                ] = destination.pop("estimated_flight_time_hrs_mins")
                destination["origin_estimated_flight_time_hrs"] = None
                destination["origin_estimated_flight_time_hrs_mins"] = None
        if destination_direct_destinations and origin_direct_destinations:
            direct_destinations = []
            for origin_destination in origin_direct_destinations:
                common_destination_index, common_destination = next(
                    (
                        (index, destination)
                        for index, destination in enumerate(
                            destination_direct_destinations
                        )
                        if destination["iataCode"] == origin_destination["iataCode"]
                    ),
                    (None, None),
                )
                if common_destination:
                    destination_direct_destinations.pop(common_destination_index)
                    common_destination[
                        "origin_estimated_flight_time_hrs"
                    ] = origin_destination["origin_estimated_flight_time_hrs"]
                    common_destination[
                        "origin_estimated_flight_time_hrs_mins"
                    ] = origin_destination["origin_estimated_flight_time_hrs_mins"]
                    direct_destinations.append(common_destination)
            direct_destinations = sorted(
                direct_destinations,
                key=lambda destination_city: destination_city[
                    "origin_estimated_flight_time_hrs"
                ],
            )

        else:
            direct_destinations = (
                origin_direct_destinations or destination_direct_destinations
            )
        return Response(direct_destinations)
