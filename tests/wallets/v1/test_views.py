"""Tests views V1."""

import uuid
from threading import Barrier, Thread
from unittest import mock

from django.db import close_old_connections
from django.urls import reverse
from parameterized import parameterized
from rest_framework.response import Response
from rest_framework.test import APIClient, APITestCase, APITransactionTestCase
from wallets.models import Operation, Wallet
from wallets.v1.serializers import (
    OperationCreateSerializer,
    WalletRetrieveSerializer,
)
from wallets.v1.views import OperationCreateViewV1, WalletRetrieveViewV1


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


class OperationCreateViewTestsMixin:
    """
    Reusable test mixin for wallet operation view tests.

    Provides helper methods for creating requests and setting
    wallet balances in test cases.
    """

    url_path = {'first_part': '/api/v1/wallets/', 'last_part': '/operation/'}
    url_name = 'operation-create-v1'

    def setUp(self):
        """Create test wallet instance for all test methods."""
        Wallet.objects.create()
        self.exist_wallet = Wallet.objects.first()

    def add_start_balance(self, start_balance: int) -> None:
        """Set the starting balance for the existing wallet."""
        self.exist_wallet.balance = start_balance
        self.exist_wallet.save(update_fields=['balance'])

    def create_request_post(
        self,
        operation_type: str,
        amount: int,
        barrier: None | Barrier = None,
        wallet_uuid: None | uuid.UUID = None,
    ) -> Response:
        """
        Send a POST request to create a wallet operation.

        Supports an optional synchronization barrier for concurrent tests.
        """
        if not wallet_uuid:
            wallet_uuid = self.exist_wallet.uuid

        client = APIClient()
        if barrier:
            barrier.wait()
        resp = client.post(
            path=reverse(
                self.url_name, kwargs={'wallet_uuid': str(wallet_uuid)}
            ),
            data={'operation_type': operation_type, 'amount': amount},
        )
        if barrier:
            close_old_connections()

        return resp


class OperationCreateViewV1Tests(OperationCreateViewTestsMixin, APITestCase):
    """Tests for OperationCreateViewV1 endpoint behavior and validation."""

    @parameterized.expand(
        (
            ['model', Operation],
            ['serializer_class', OperationCreateSerializer],
        )
    )
    def test_view_attr(self, attr, expect_value):
        """Verify view class has required attribute with correct value."""
        fact_value = getattr(OperationCreateViewV1, attr)
        self.assertEqual(fact_value, expect_value)

    def test_view_url_exists(self):
        """
        Verify named URL resolves correctly.

        Url:  /api/v1/wallets/<uuid:wallet_uuid>/operation/
        """
        resp = self.client.post(
            path=(
                self.url_path['first_part']
                + str(self.exist_wallet.uuid)
                + self.url_path['last_part']
            ),
            data={'operation_type': 'DEPOSIT', 'amount': 1000},
        )
        self.assertEqual(resp.status_code, 201)

    def test_view_url_name(self):
        """Verify named URL resolves correctly."""
        resp = self.create_request_post('DEPOSIT', 1000)
        self.assertEqual(resp.status_code, 201)

    def test_view_url_not_exists(self):
        """Ensure 404 response for non-existent wallet UUID."""
        not_exist_uuid = uuid.UUID('00000000-0000-0000-0000-000000000000')
        resp = self.create_request_post(
            'DEPOSIT', 1000, wallet_uuid=not_exist_uuid
        )
        self.assertEqual(resp.status_code, 404)

    @parameterized.expand(
        (
            ['get', 'GET'],
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

    @mock.patch('wallets.v1.views.preform_wallet_operation')
    def test_call_service_preform_wallet_operation(
        self, mock_preform_wallet_operation
    ):
        """
        Ensure the service function `preform_wallet_operation` is called.

        It must be invoked with the given serializer and wallet UUID.
        """
        mock_serializer = mock.MagicMock()
        mock_serializer.is_valid.return_value = True
        mock_serializer.data = None

        with mock.patch(
            'wallets.v1.views.OperationCreateViewV1.get_serializer',
            return_value=mock_serializer,
        ):
            self.create_request_post('DEPOSIT', 1000)
            mock_preform_wallet_operation.assert_called_once_with(
                mock_serializer, self.exist_wallet.uuid
            )

    @parameterized.expand(
        (
            ['amount_positive_1', 1],
            ['amount_positive_1000', 1000],
            ['amount_positive_1000000', 1000000],
            ['amount_max', 9223372036854775807],
        )
    )
    def test_view_valid_data_deposit(self, _, amount):
        """Check valid DEPOSIT operations return 201 Created."""
        resp = self.create_request_post('DEPOSIT', amount)
        self.assertEqual(resp.status_code, 201)

    @parameterized.expand(
        (
            ['amount_0', 0],
            ['amount_negative_1', -1],
            ['amount_negative_1000000', -1000000],
            ['amount_exceed_max', 9223372036854775808],
            ['amount_str', '100$'],
            ['amount_true', True],
        )
    )
    def test_view_invalid_data_deposit(self, _, amount):
        """Check invalid DEPOSIT operations return 400 Bad Request."""
        resp = self.create_request_post('DEPOSIT', amount)
        self.assertEqual(resp.status_code, 400)

    @parameterized.expand(
        (
            ['amount_positive_1', 1],
            ['amount_positive_1000', 1000],
            ['amount_positive_1000000', 1000000],
            ['amount_max', 9223372036854775807],
        )
    )
    def test_view_valid_data_withdraw(self, _, amount):
        """
        Check valid WITHDRAW operations.

        WITHDRAW operations with sufficient balance
        return a 201 Created response.
        """
        self.add_start_balance(9223372036854775807)
        resp = self.create_request_post('WITHDRAW', amount)
        self.assertEqual(resp.status_code, 201)

    @parameterized.expand(
        (
            ['amount_positive_1_balance_0', 0, 1],
            ['amount_0_balance_positive_100', 100, 0],
            ['amount_positive_20_balance_positive_10', 20, 10],
            ['amount_0_balance_0', 0, 0],
            ['amount_negative_10_balance_positive_100', -10, 100],
            ['amount_negative_1000_balance_0', -1000, 0],
            [
                'amount_exceed_max_balance_max',
                9223372036854775808,
                9223372036854775807,
            ],
            # ['amount_none_balance_positive_1000', None, 1000],
            ['amount_true_balance_positive_1000', True, 1000],
            ['amount_str_balance_positive_1000', '100$', 1000],
        )
    )
    def test_view_invalid_data_withdraw(self, _, amount, balance):
        """Check invalid WITHDRAW operations return 400 Bad Request."""
        self.add_start_balance(balance)
        resp = self.create_request_post('WITHDRAW', amount)
        self.assertEqual(resp.status_code, 400)

    @parameterized.expand(
        (
            [
                'start_balance_0_dep1000',
                0,
                {'operation_type': 'DEPOSIT', 'amount': 1000},
            ],
            [
                'start_balance_10_wdraw10',
                10,
                {'operation_type': 'WITHDRAW', 'amount': 10},
            ],
        ),
    )
    def test_view_return_data(self, _, balance, expect_data):
        """Verify API returns correct response data structure and values."""
        self.add_start_balance(balance)
        resp = self.create_request_post(**expect_data)
        fact_data = resp.data

        self.assertIn('id', fact_data)

        self.assertIn('operation_type', fact_data)
        self.assertEqual(
            fact_data['operation_type'], expect_data['operation_type']
        )

        self.assertIn('amount', fact_data)
        self.assertEqual(fact_data['amount'], expect_data['amount'])

        self.assertIn('wallet', fact_data)
        self.assertEqual(fact_data['wallet'], self.exist_wallet.uuid)


class OperationCreateViewV1TransactionsTests(
    OperationCreateViewTestsMixin, APITransactionTestCase
):
    """Tests for OperationCreateViewV1 with transactional behavior."""

    @parameterized.expand(
        (
            [
                'start_balance_10_dep50_dep30',
                10,
                [(50, 'DEPOSIT'), (30, 'DEPOSIT')],
                90,
            ],
            [
                'start_balance_100_wdraw60_wdraw40',
                100,
                [(60, 'WITHDRAW'), (40, 'WITHDRAW')],
                0,
            ],
            [
                'start_balance_80_dep50_wdraw30',
                80,
                [(50, 'DEPOSIT'), (30, 'WITHDRAW')],
                100,
            ],
            [
                'start_balance_70_dep20_wdraw20',
                70,
                [(20, 'DEPOSIT'), (20, 'WITHDRAW')],
                70,
            ],
            [
                'start_balance_30_wdraw50_wdraw40',
                30,
                [(50, 'WITHDRAW'), (40, 'WITHDRAW')],
                30,
            ],
        )
    )
    def test_view_select_for_update(
        self,
        _,
        start_balance,
        amount_list,
        expect_balance,
    ):
        """
        Simulate concurrent requests.

        Verify select_for_update and correct final balance.
        """
        self.add_start_balance(start_balance)

        barrier = Barrier(2)
        thread_list = []
        for amount, operation_type in amount_list:
            thread_list.append(
                Thread(
                    target=self.create_request_post,
                    args=(operation_type, amount, barrier),
                )
            )
        for thread in thread_list:
            thread.start()
        for thread in thread_list:
            thread.join()

        self.exist_wallet.refresh_from_db()
        fact_balance = self.exist_wallet.balance
        # Check balance.
        self.assertEqual(fact_balance, expect_balance)

    @parameterized.expand(
        (
            ['start_balance_100_wdraw1000', 100, 1000],
            ['start_balance_100_wdraw101', 100, 101],
            ['start_balance_0_wdraw1', 0, 1],
        ),
    )
    def test_view_atomic(self, _, start_balance, amount):
        """
        Ensure atomicity.

        Failed WITHDRAW leaves no create operation in DB.
        """
        self.add_start_balance(start_balance)
        resp = self.create_request_post('WITHDRAW', amount)
        self.assertEqual(resp.status_code, 400)
        self.assertFalse(Operation.objects.exists())

    @parameterized.expand(
        (
            [
                '50_operations_deposit_start_balance_0',
                50,
                0,
                50,
                'DEPOSIT',
                50,
            ],
            [
                '50_operations_withdraw_start_balance_50',
                55,
                50,
                0,
                'WITHDRAW',
                50,
            ],
        ),
    )
    def test_view_high_load_check_operations(
        self,
        _,
        num_operations,
        start_balance,
        expect_balance,
        operation_type,
        expect_num_db_operations,
    ):
        """
        Stress test with many concurrent operations.

        Checking balance consistency and operation count in DB.
        """
        self.add_start_balance(start_balance)

        barrier = Barrier(num_operations)
        thread_list = []
        for _ in range(num_operations):
            thread_list.append(
                Thread(
                    target=self.create_request_post,
                    args=(operation_type, 1, barrier),
                )
            )
        for thread in thread_list:
            thread.start()
        for thread in thread_list:
            thread.join()

        self.exist_wallet.refresh_from_db()

        # Check balance.
        self.assertEqual(self.exist_wallet.balance, expect_balance)

        # Check num operations in DB.
        fact_num_db_operations = Operation.objects.count()
        self.assertEqual(fact_num_db_operations, expect_num_db_operations)
