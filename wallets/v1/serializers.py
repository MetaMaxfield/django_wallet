"""Serializers V1."""

from rest_framework import serializers
from wallets.models import Wallet


class WalletRetrieveSerializer(serializers.ModelSerializer):
    """Serializer for retrieve Wallet data."""

    class Meta:
        """Serialize wallet ID and balance."""

        model = Wallet
        fields = ('id', 'balance')
