from django.urls import path
from . import views

urlpatterns = [
    path("", views.lookup, name="lookup"),
    path("stats/", views.stats, name="stats"),
    path("history/", views.history, name="history")
]
