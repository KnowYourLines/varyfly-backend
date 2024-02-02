import datetime

from django.test import TestCase

from .serializers import OrderCreatedSerializer


class OrderCreatedSerializerTest(TestCase):
    def test_new_idempotency_key_valid(self):
        serializer = OrderCreatedSerializer(
            data={
                "data": {"object": {"id": "hello"}},
                "idempotency_key": "world",
            },
            context={"now": datetime.datetime.now()},
        )
        serializer.is_valid(raise_exception=True)
        assert serializer.validated_data == {
            "data": {"object": {"id": "hello"}},
            "idempotency_key": "world",
        }
        serializer = OrderCreatedSerializer(
            data={
                "data": {"object": {"id": "hello"}},
                "idempotency_key": "goodbye",
            },
            context={"now": datetime.datetime.now()},
        )
        serializer.is_valid(raise_exception=True)
        assert serializer.validated_data == {
            "data": {"object": {"id": "hello"}},
            "idempotency_key": "goodbye",
        }

    def test_duplicate_idempotency_key_invalid(self):
        now = datetime.datetime.now()
        serializer = OrderCreatedSerializer(
            data={
                "data": {"object": {"id": "hello"}},
                "idempotency_key": "world",
            },
            context={"now": now},
        )
        serializer.is_valid(raise_exception=True)
        assert serializer.validated_data == {
            "data": {"object": {"id": "hello"}},
            "idempotency_key": "world",
        }
        serializer = OrderCreatedSerializer(
            data={
                "data": {"object": {"id": "hello"}},
                "idempotency_key": "world",
            },
            context={"now": now + datetime.timedelta(days=2)},
        )
        assert not serializer.is_valid()

    def test_duplicate_idempotency_valid_after_3_days(self):
        now = datetime.datetime.now()
        serializer = OrderCreatedSerializer(
            data={
                "data": {"object": {"id": "hello"}},
                "idempotency_key": "world",
            },
            context={"now": now},
        )
        serializer.is_valid(raise_exception=True)
        assert serializer.validated_data == {
            "data": {"object": {"id": "hello"}},
            "idempotency_key": "world",
        }
        serializer = OrderCreatedSerializer(
            data={
                "data": {"object": {"id": "hello"}},
                "idempotency_key": "world",
            },
            context={"now": now + datetime.timedelta(days=3)},
        )
        serializer.is_valid(raise_exception=True)
        assert serializer.validated_data == {
            "data": {"object": {"id": "hello"}},
            "idempotency_key": "world",
        }
