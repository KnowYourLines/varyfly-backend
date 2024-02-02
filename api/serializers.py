import datetime

from django.core.cache import cache
from rest_framework import serializers


class ObjectSerializer(serializers.Serializer):
    id = serializers.CharField(required=True)


class DataSerializer(serializers.Serializer):
    object = ObjectSerializer(required=True)


class OrderCreatedSerializer(serializers.Serializer):
    data = DataSerializer(required=True)
    idempotency_key = serializers.CharField(required=True)

    def validate_idempotency_key(self, idempotency_key):
        cached_idempotency_key = cache.get(idempotency_key)
        if cached_idempotency_key:
            if (
                cached_idempotency_key + datetime.timedelta(days=3)
                >= datetime.datetime.now()
            ):
                raise serializers.ValidationError("Duplicate webhook request received.")
            else:
                cache.touch(cached_idempotency_key, 0)
        else:
            cache.set(idempotency_key, datetime.datetime.now(), 60 * 60 * 72)
