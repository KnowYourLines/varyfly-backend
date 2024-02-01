from django.urls import path

from api import views

urlpatterns = [
    path(r"webhooks/", views.WebhooksView.as_view()),
    path(r"booking/", views.BookingLinkView.as_view()),
    path(r"search-cities/", views.CitySearchView.as_view()),
    path(r"direct-destinations/", views.DirectDestinationsView.as_view()),
]
