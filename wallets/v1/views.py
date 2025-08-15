"""Views V1."""

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from wallets.models import Operation, Wallet
from wallets.v1.serializers import (
    OperationCreateSerializer,
    WalletRetrieveSerializer,
)


class WalletRetrieveViewV1(generics.RetrieveAPIView):
    """
    API endpoint for retrieving wallet details (v1).

    Attributes:
        queryset: All Wallet objects available for retrieval
        serializer_class: Serializer defining response structure
        lookup_field: Model field used for object lookup (uuid)
        lookup_url_kwarg: URL keyword argument for lookup value
    """

    queryset = Wallet.objects.all()
    serializer_class = WalletRetrieveSerializer
    lookup_field = 'uuid'
    lookup_url_kwarg = 'wallet_uuid'


class OperationCreateViewV1(generics.CreateAPIView):
    """
    API endpoint for creating wallet operations (v1).

    Attributes:
        model: Operation model class for object creation
        serializer_class: Serializer for operation creation and validation
    """

    model = Operation
    serializer_class = OperationCreateSerializer

    @transaction.atomic
    def perform_create(self, serializer):
        """Perform create."""
        wallet = get_object_or_404(
            Wallet.objects.select_for_update(), uuid=self.kwargs['wallet_uuid']
        )
        operation = serializer.save(wallet=wallet)

        if operation.operation_type == Operation.DEPOSIT:
            wallet.balance += operation.amount
        elif operation.operation_type == Operation.WITHDRAW:
            if wallet.balance >= operation.amount:
                wallet.balance -= operation.amount
            else:
                raise ValidationError(
                    'На балансе недостаточно средств для проведения операции.'
                )
        else:
            raise ValidationError('Неизвестный тип операции.')

        wallet.save(update_fields=['balance'])
