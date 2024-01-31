import logging
import os

import requests
from geopy import distance


def access_token_and_type():
    try:
        response = requests.post(
            f"https://{os.environ.get('AMADEUS_BASE_URL')}/v1/security/oauth2/token",
            data={
                "grant_type": "client_credentials",
                "client_id": os.environ.get("AMADEUS_API_KEY"),
                "client_secret": os.environ.get("AMADEUS_API_SECRET"),
            },
        )
        response.raise_for_status()
        response = response.json()
        access_token = response["access_token"]
        token_type = response["token_type"]
        return token_type, access_token
    except requests.HTTPError as exc:
        logging.error(
            f"Error response {exc.response.status_code} while requesting {exc.request.url}: {exc.response.text}"
        )


def get_city_details(
    city_iata,
    country_code,
    token_type,
    access_token,
):
    try:
        response = requests.get(
            f"https://{os.environ.get('AMADEUS_BASE_URL')}/v1/reference-data/locations",
            params={
                "keyword": city_iata,
                "countryCode": country_code,
                "subType": "CITY",
            },
            headers={"Authorization": f"{token_type} {access_token}"},
        )
        response.raise_for_status()
        city_data = response.json().get("data", [])
        city = next(city for city in city_data if city["iataCode"] == city_iata)
        return city
    except requests.HTTPError as exc:
        logging.error(
            f"Error response {exc.response.status_code} while requesting {exc.request.url}: {exc.response.text}"
        )


def get_direct_destinations(
    city_iata,
    city_name,
    country_iata,
    token_type,
    access_token,
):
    try:
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
        response.raise_for_status()
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
            response.raise_for_status()
            destinations = response.json().get("data", [])
            for city in destinations:
                city_relevance = city.get("metrics", {}).get("relevance", 0)
                city["metrics"] = {"relevance": city_relevance}
                irrelevant = (
                    city_relevance == 0
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
            key=lambda destination_city: (
                -destination_city["metrics"]["relevance"],
                destination_city["estimated_flight_time_hrs"],
            ),
        )
        return direct_destinations
    except requests.HTTPError as exc:
        logging.error(
            f"Error response {exc.response.status_code} while requesting {exc.request.url}: {exc.response.text}"
        )
