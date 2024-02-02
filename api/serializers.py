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
        cached_idempotency_key_expiration = cache.get(idempotency_key)
        if (
            cached_idempotency_key_expiration
            and self.context["now"] < cached_idempotency_key_expiration
        ):
            raise serializers.ValidationError("Duplicate webhook request received.")
        cache.set(
            idempotency_key,
            self.context["now"] + datetime.timedelta(days=3),
            60 * 60 * 72,
        )
        return idempotency_key
