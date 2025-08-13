"""Create your models here."""

import uuid

from django.db import models


class Operation(models.Model):
    """Financial operation on a wallet."""

    DEPOSIT = 'DEPOSIT'
    WITHDRAW = 'WITHDRAW'
    OPERATION_TYPES = [(DEPOSIT, 'Пополнение'), (WITHDRAW, 'Снятие')]
    operation_type = models.CharField(
        verbose_name='Тип операции',
        choices=OPERATION_TYPES,
        blank=False,
        null=False,
        editable=False,
    )
    amount = models.PositiveBigIntegerField(
        verbose_name='Величина', blank=False, null=False, editable=False
    )
    date = models.DateTimeField(auto_now_add=True, editable=False)
    wallet = models.ForeignKey(
        to='wallets.Wallet',
        blank=False,
        null=False,
        on_delete=models.PROTECT,
        editable=False,
        related_name='operations',
    )

    def __str__(self):
        """Represent a string."""
        return f'Операция id: {self.id} у кошелька id: {self.wallet.id}'

    class Meta:
        """Metadata options."""

        verbose_name = 'Операция'
        verbose_name_plural = 'Операции'


class Wallet(models.Model):
    """Digital wallet holding financial balance."""

    uuid = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, db_index=True
    )
    balance = models.PositiveBigIntegerField(
        verbose_name='Баланс', default=0, editable=False
    )

    def __str__(self):
        """Represent a string."""
        return f'Кошелёк id: {self.id}'

    class Meta:
        """Metadata options."""

        verbose_name = 'Кошелёк'
        verbose_name_plural = 'Кошельки'
