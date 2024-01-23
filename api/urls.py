from django.urls import path

from api import views

urlpatterns = [
    path(r"search/cities/", views.CitySearchView.as_view()),
]
