"""Url patterns V1."""

from django.urls import URLPattern, path
from wallets.v1.views import WalletRetrieveViewV1

urlpatterns: list[URLPattern] = [
    path(
        '<uuid:wallet_uuid>/',
        WalletRetrieveViewV1.as_view(),
        name='wallet-retrieve-v1',
    ),
    # path('<WALLET_UUID>/operation/' WalletOperationViewV1.as_view()),
]
