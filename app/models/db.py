from sqlalchemy import ForeignKey, UniqueConstraint, DECIMAL, UUID, Index
from sqlalchemy.orm import Mapped, mapped_column

from enum import Enum
from uuid import uuid4

from app.core.db import Base


class CodeEnum(str, Enum):
    RUB = 'rub'
    EUR = 'eur'
    USD = 'usd'


class AccountStatusEnum(str, Enum):
    ACTIVE = 'active'
    BLOCKED = 'blocked'
    CLOSED = 'closed'


class TransactionTypeEnum(str, Enum):
    DEBIT = "debit"
    CREDIT = "credit"


class StatusEnum(str, Enum):
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'


class User(Base):
    __tablename__ = 'users'

    email: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)


class Currency(Base):
    __tablename__ = 'currencies'

    code: Mapped[CodeEnum]
    name: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)


class Accounts(Base):
    __tablename__ = 'accounts'

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    currency_id: Mapped[int] = mapped_column(ForeignKey('currencies.id'))
    balance: Mapped[DECIMAL] = mapped_column(DECIMAL(18, 2), server_default="0")
    status: Mapped[AccountStatusEnum] = mapped_column(default=AccountStatusEnum.ACTIVE)

    __table_args__ = (
        UniqueConstraint("user_id", "currency_id"),
    )


class Transfer(Base):
    __tablename__ = 'transfers'

    public_id: Mapped[UUID] = mapped_column(default=uuid4, unique=True)
    from_account_id: Mapped[int] = mapped_column(ForeignKey('accounts.id'))
    to_account_id: Mapped[int] = mapped_column(ForeignKey('accounts.id'))
    amount: Mapped[DECIMAL] = mapped_column(DECIMAL(18, 2))
    status: Mapped[StatusEnum]


class Transaction(Base):
    __tablename__ = 'transactions'

    account_id: Mapped[int] = mapped_column(ForeignKey('accounts.id'))
    reference: Mapped[UUID | None] = mapped_column(ForeignKey('transfers.id'))
    type: Mapped[TransactionTypeEnum]
    amount: Mapped[DECIMAL] = mapped_column(DECIMAL(18, 2))
    status: Mapped[StatusEnum]

    Index("ix_transactions_account_id", "account_id")
    Index("ix_transfers_status", "status")

