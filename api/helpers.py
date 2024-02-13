import datetime
import logging
import os

import isodate
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
        direct_destinations = {}
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

                if city["iataCode"] not in direct_destinations and not irrelevant:
                    direct_destinations[city["iataCode"]] = city
                elif (
                    city["iataCode"] in direct_destinations
                    and direct_destinations[city["iataCode"]]["metrics"]["relevance"]
                    < city_relevance
                ):
                    direct_destinations[city["iataCode"]] = city
        direct_destinations = list(direct_destinations.values())
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


def get_trip_segments(trip_slices, trip_passengers):
    segments = []
    for trip_slice in trip_slices:
        for segment in trip_slice["segments"]:
            segment["departing_at"] = datetime.datetime.strptime(
                segment["departing_at"], "%Y-%m-%dT%H:%M:%S"
            )
            segment["departure_time"] = segment["departing_at"].strftime("%H:%Mh")
            segment["departure_date"] = segment["departing_at"].strftime("%d/%m/%Y")
            segment["arriving_at"] = datetime.datetime.strptime(
                segment["arriving_at"], "%Y-%m-%dT%H:%M:%S"
            )
            segment["arrival_time"] = segment["arriving_at"].strftime("%H:%Mh")
            duration_total_seconds = isodate.parse_duration(
                segment["duration"]
            ).total_seconds()
            duration_hours = int(duration_total_seconds // 3600)
            duration_minutes = int((duration_total_seconds % 3600) // 60)
            segment["duration"] = f"{duration_hours}h {duration_minutes}m"
            for passenger in segment["passengers"]:
                passenger_id = passenger["passenger_id"]
                passenger_details = next(
                    passenger
                    for passenger in trip_passengers
                    if passenger["id"] == passenger_id
                )
                passenger["given_name"] = passenger_details["given_name"]
                passenger["family_name"] = passenger_details["family_name"]
                passenger["cabin_class"] = passenger["cabin_class"].capitalize()
                if not passenger.get("seat"):
                    passenger["seat"] = "Not assigned"
                else:
                    passenger["seat"] = passenger["seat"]["designator"]
                passenger["baggage"] = next(
                    luggage["quantity"]
                    for luggage in passenger["baggages"]
                    if luggage["type"] == "checked"
                )
                passenger["carry_on"] = next(
                    luggage["quantity"]
                    for luggage in passenger["baggages"]
                    if luggage["type"] == "carry_on"
                )

            segments.append(segment)
    return segments


def search_cities(query, country_iata):
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
    if cities:
        return cities
    else:
        response = requests.get(
            f"https://{os.environ.get('AMADEUS_BASE_URL')}/v1/reference-data/locations/cities",
            params={"keyword": query},
            headers={"Authorization": f"{token_type} {access_token}"},
        )
        response.raise_for_status()
        cities = response.json().get("data", [])
        airport_cities = {}
        for city in cities:
            latitude = city.get("geoCode", {}).get("latitude")
            longitude = city.get("geoCode", {}).get("longitude")
            if not (latitude and longitude):
                continue
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "radius": 500,
                "sort": "distance",
                "page[limit]": 20,
                "page[offset]": 0,
            }
            response = requests.get(
                f"https://{os.environ.get('AMADEUS_BASE_URL')}/v1/reference-data/locations/airports",
                params=params,
                headers={"Authorization": f"{token_type} {access_token}"},
            )
            response.raise_for_status()
            airports = response.json().get("data", [])
            for airport in airports:
                city_iata = airport["address"]["cityCode"]
                if city_iata not in airport_cities and len(airport_cities) < 10:
                    airport_cities[city_iata] = {
                        "iataCode": city_iata,
                        "name": airport["address"]["cityName"],
                        "address": airport["address"],
                    }
        return [city_details for city_iata, city_details in airport_cities.items()]
