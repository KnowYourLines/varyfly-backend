import datetime
import json
import logging
import os
import uuid

import pycountry
import requests
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from rest_framework.response import Response
from rest_framework.views import APIView

from api.helpers import (
    access_token_and_type,
    get_direct_destinations,
    get_trip_segments,
    search_cities,
)
from api.serializers import OrderCreatedSerializer


class WebhooksView(APIView):
    def post(self, request):
        serializer = OrderCreatedSerializer(
            data=request.data, context={"now": datetime.datetime.now()}
        )
        if serializer.is_valid(raise_exception=True):
            order_id = serializer.validated_data["data"]["object"]["id"]
            try:
                auth_token = os.environ.get("DUFFEL_ACCESS_TOKEN")
                url = f"https://api.duffel.com/air/orders/{order_id}"
                headers = {
                    "Duffel-Version": "v1",
                    "Authorization": f"Bearer {auth_token}",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Accept-Encoding": "gzip",
                }
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                response = response.json()["data"]
                passengers = response["passengers"]
                segments = get_trip_segments(response["slices"], passengers)
                fare = f"{response['base_amount']} {response['base_currency']}"
                fees_and_taxes = f"{response['tax_amount']} {response['tax_currency']}"
                total = f"{response['total_amount']} {response['total_currency']}"
                change_condition = response["conditions"]["change_before_departure"]
                if change_condition["allowed"]:
                    change_condition = (
                        f"Flight changes allowed at any time up until the initial departure date, with a penalty of "
                        f"{change_condition['penalty_amount']} {change_condition['penalty_currency']}."
                    )
                else:
                    change_condition = "No flight changes allowed."
                refund_condition = response["conditions"]["refund_before_departure"]
                if refund_condition["allowed"]:
                    refund_condition = (
                        f"Refunds allowed at any time up until the initial departure date, with a penalty of "
                        f"{refund_condition['penalty_amount']} {refund_condition['penalty_currency']}."
                    )
                else:
                    refund_condition = "No refunds allowed."
                passenger_emails = [
                    passenger["email"] for passenger in response["passengers"]
                ]
                booking_reference = response["booking_reference"]
                context = {
                    "booking_reference": booking_reference,
                    "segments": segments,
                    "refund_condition": refund_condition,
                    "change_condition": change_condition,
                    "fare": fare,
                    "fees_and_taxes": fees_and_taxes,
                    "total": total,
                }
                html_message = render_to_string(
                    "confirmation_email.html", context=context
                )
                plain_message = strip_tags(html_message)

                message = EmailMultiAlternatives(
                    subject=f"Flight Booking {booking_reference}",
                    from_email=f"Varyfly <{os.environ.get('EMAIL_HOST_USER')}>",
                    body=plain_message,
                    to=passenger_emails,
                )

                message.attach_alternative(html_message, "text/html")
                message.send()
                return Response(response)
            except requests.HTTPError as exc:
                logging.error(
                    f"Error response {exc.response.status_code} while requesting {exc.request.url}: {exc.response.text}"
                )
                return Response(
                    {"request_url": exc.request.url, "message": exc.response.text},
                    status=exc.response.status_code,
                )


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
                    "secondary_color": "#003dcc",
                    "reference": str(uuid.uuid4()),
                    "primary_color": "#003dcc",
                    "markup_rate": "0.01",
                    "markup_currency": "GBP",
                    "markup_amount": "2.25",
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
                cities = search_cities(query, country_iata)
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
