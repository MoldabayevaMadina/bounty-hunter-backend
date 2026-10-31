from django.urls import path

from . import views

urlpatterns = [
    path("criminals/", views.CriminalList.as_view(), name="criminal-list"),
    path("criminals/<int:pk>/", views.CriminalDetail.as_view(), name="criminal-detail"),
    path("hunts/", views.HuntList.as_view(), name="hunt-list"),
    path("hunts/<int:pk>/", views.HuntDetail.as_view(), name="hunt-detail"),
]