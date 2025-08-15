"""Service lawyer for change balance logic."""

from uuid import UUID

from django.db import transaction
from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from wallets.models import Operation, Wallet
from wallets.v1.serializers import OperationCreateSerializer


@transaction.atomic
def preform_wallet_operation(
    serializer: OperationCreateSerializer, wallet_uuid: UUID
) -> None:
    """
    Perform a financial operation on a wallet.

    Creates an Operation instance via the serializer and updates
    the wallet's balance based on the operation type (deposit or withdrawal)
    within an atomic transaction.

    Args:
        serializer (OperationCreateSerializer): serializer with operation data.
        wallet_uuid (UUID): UUID of the wallet to apply the operation to.

    Raises:
        ValidationError: if the operation type is unknown or insufficient funds
        for withdrawal.
        Http404: if no wallet with the given UUID exists.
    """
    wallet = get_object_or_404(
        Wallet.objects.select_for_update(), uuid=wallet_uuid
    )
    operation = serializer.save(wallet=wallet)

    if operation.operation_type == Operation.DEPOSIT:
        wallet.deposit(operation.amount)
    elif operation.operation_type == Operation.WITHDRAW:
        wallet.withdraw(operation.amount)
    else:
        raise ValidationError('Неизвестный тип операции.')
