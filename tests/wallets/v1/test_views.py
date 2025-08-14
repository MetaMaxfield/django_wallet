"""Tests views V1."""

import uuid

from django.urls import reverse
from parameterized import parameterized
from rest_framework.test import APITestCase
from wallets.models import Wallet
from wallets.v1.serializers import WalletRetrieveSerializer
from wallets.v1.views import WalletRetrieveViewV1


class WalletRetrieveViewV1Tests(APITestCase):
    """
    API v1 wallet retrieval view test case.

    Tests view attributes, URL routing, HTTP method restrictions
    and response data structure.
    """

    url_path = '/api/v1/wallets/'
    url_name = 'wallet-retrieve-v1'

    @classmethod
    def setUpTestData(cls):
        """Create test wallet instance for all test methods."""
        Wallet.objects.create()
        cls.exist_wallet = Wallet.objects.first()

    @parameterized.expand(
        (
            ['serializer_class', WalletRetrieveSerializer],
            ['lookup_field', 'uuid'],
            ['lookup_url_kwarg', 'wallet_uuid'],
        ),
    )
    def test_view_attr(self, attr, expect_value):
        """Verify view class has required attribute with correct value."""
        fact_value = getattr(WalletRetrieveViewV1, attr)
        self.assertEqual(fact_value, expect_value)

    def test_view_url_exists(self):
        """Check wallet retrieval URL returns 200 for existing wallet."""
        resp = self.client.get(f'{self.url_path}{self.exist_wallet.uuid}/')
        self.assertEqual(resp.status_code, 200)

    def test_view_url_name(self):
        """Verify named URL resolves correctly."""
        resp = self.client.get(
            reverse(
                self.url_name, kwargs={'wallet_uuid': self.exist_wallet.uuid}
            )
        )
        self.assertEqual(resp.status_code, 200)

    def test_view_url_not_exists(self):
        """Ensure 404 response for non-existent wallet UUID."""
        not_exist_uuid = uuid.UUID('00000000-0000-0000-0000-000000000000')
        resp = self.client.get(
            reverse(self.url_name, kwargs={'wallet_uuid': not_exist_uuid})
        )
        self.assertEqual(resp.status_code, 404)

    @parameterized.expand(
        (
            ['post', 'POST'],
            ['put', 'PUT'],
            ['patch', 'PATCH'],
            ['delete', 'DELETE'],
        ),
    )
    def test_no_allow_http_method(self, _, http_method):
        """Confirm 405 response for disallowed HTTP methods."""
        resp = self.client.generic(
            method=http_method,
            path=reverse(
                self.url_name, kwargs={'wallet_uuid': self.exist_wallet.uuid}
            ),
        )
        self.assertEqual(resp.status_code, 405)

    def test_view_return_data(self):
        """Validate response data structure and values."""
        resp = self.client.get(
            reverse(
                self.url_name, kwargs={'wallet_uuid': self.exist_wallet.uuid}
            )
        )

        self.assertIn('id', resp.data)
        self.assertEqual(resp.data['id'], self.exist_wallet.id)

        self.assertIn('balance', resp.data)
        self.assertEqual(resp.data['balance'], self.exist_wallet.balance)
