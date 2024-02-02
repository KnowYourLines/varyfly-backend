from rest_framework import serializers


class ObjectSerializer(serializers.Serializer):
    id = serializers.CharField(required=True)


class DataSerializer(serializers.Serializer):
    object = ObjectSerializer(required=True)


class OrderCreatedSerializer(serializers.Serializer):
    data = DataSerializer(required=True)
    idempotency_key = serializers.CharField(required=True)
