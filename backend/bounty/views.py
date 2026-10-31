from django.shortcuts import render
from rest_framework import generics
from rest_framework.exceptions import NotFound, ValidationError

from .models import HuntLog, WantedCriminal
from .serializers import HuntLogSerializer, WantedCriminalSerializer

TRUE_VALUES = {"true", "1", "yes"}
FALSE_VALUES = {"false", "0", "no"}
SORT_OPTIONS = {"reward", "-reward"}


def parse_int(params, name):
    """Read a non-negative integer query parameter or raise 400."""
    value = params.get(name)
    if value is None or value == "":
        return None
    if not value.isdigit():
        raise ValidationError({name: "Must be a non-negative integer."})
    return int(value)


def parse_bool(params, name):
    """Read a true/false query parameter or raise 400."""
    value = params.get(name)
    if value is None or value == "":
        return None
    value = value.lower()
    if value in TRUE_VALUES:
        return True
    if value in FALSE_VALUES:
        return False
    raise ValidationError({name: "Must be true or false."})


class CriminalList(generics.ListAPIView):
    """GET /api/criminals/?min_reward=&max_reward=&armed=&has_crew=&escape_master=&sort=reward|-reward"""

    serializer_class = WantedCriminalSerializer

    def get_queryset(self):
        params = self.request.query_params
        qs = WantedCriminal.objects.all()

        min_reward = parse_int(params, "min_reward")
        max_reward = parse_int(params, "max_reward")
        if min_reward is not None and max_reward is not None and min_reward > max_reward:
            raise ValidationError({"min_reward": "min_reward can't be greater than max_reward."})
        if min_reward is not None:
            qs = qs.filter(reward__gte=min_reward)
        if max_reward is not None:
            qs = qs.filter(reward__lte=max_reward)

        for flag in ("armed", "has_crew", "escape_master"):
            value = parse_bool(params, flag)
            if value is not None:
                qs = qs.filter(**{flag: value})

        sort = params.get("sort")
        if sort:
            if sort not in SORT_OPTIONS:
                raise ValidationError({"sort": "Use reward or -reward."})
            qs = qs.order_by(sort, "id")
        return qs


class CriminalDetail(generics.RetrieveAPIView):
    """GET /api/criminals/{id}/"""

    queryset = WantedCriminal.objects.all()
    serializer_class = WantedCriminalSerializer


class HuntList(generics.ListCreateAPIView):
    """GET /api/hunts/?criminal_id=  |  POST /api/hunts/"""

    serializer_class = HuntLogSerializer

    def get_queryset(self):
        qs = HuntLog.objects.select_related("criminal")
        criminal_id = parse_int(self.request.query_params, "criminal_id")
        if criminal_id is not None:
            if not WantedCriminal.objects.filter(pk=criminal_id).exists():
                raise NotFound(f"Criminal {criminal_id} not found.")
            qs = qs.filter(criminal_id=criminal_id)
        return qs


class HuntDetail(generics.RetrieveUpdateDestroyAPIView):
    """GET / PATCH / DELETE /api/hunts/{id}/"""

    queryset = HuntLog.objects.select_related("criminal")
    serializer_class = HuntLogSerializer
    http_method_names = ["get", "patch", "delete", "head", "options"]