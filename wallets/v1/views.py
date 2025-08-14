"""Views V1."""

from rest_framework import generics
from wallets.models import Wallet
from wallets.v1.serializers import WalletRetrieveSerializer


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
