"""Url patterns V1."""

from django.urls import URLPattern, path
from wallets.v1.views import OperationCreateViewV1, WalletRetrieveViewV1

urlpatterns: list[URLPattern] = [
    path(
        '<uuid:wallet_uuid>/',
        WalletRetrieveViewV1.as_view(),
        name='wallet-retrieve-v1',
    ),
    path(
        '<uuid:wallet_uuid>/operation/',
        OperationCreateViewV1.as_view(),
        name='operation-create-v1',
    ),
]
