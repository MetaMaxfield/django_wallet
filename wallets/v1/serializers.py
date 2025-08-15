"""Serializers V1."""

from rest_framework import serializers
from wallets.models import Operation, Wallet


class WalletRetrieveSerializer(serializers.ModelSerializer):
    """Serializer for retrieve Wallet data."""

    class Meta:
        """Serialize wallet ID and balance."""

        model = Wallet
        fields = ('id', 'balance')


class OperationCreateSerializer(serializers.ModelSerializer):
    """Serializer for create Operation data."""

    wallet = serializers.SlugRelatedField(
        queryset=Wallet.objects.all(),
        slug_field='uuid',
        required=False,  # for dispay 'wallet' in response.data
    )

    class Meta:
        """Serialize operation ID, operation_type, mount, wallet."""

        model = Operation
        fields = ('id', 'operation_type', 'amount', 'wallet')
