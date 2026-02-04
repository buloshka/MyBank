from sqlalchemy import ForeignKey, UniqueConstraint, DECIMAL, UUID, Index, CheckConstraint
from sqlalchemy import Enum as SQLEnum
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
    DEBIT = 'debit'
    CREDIT = 'credit'


class StatusEnum(str, Enum):
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'


class User(Base):
    __tablename__ = 'users'

    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    __table_args__ = (
        Index('ix_user_email', 'email'),
    )


class Currency(Base):
    __tablename__ = 'currencies'

    code: Mapped[CodeEnum] = mapped_column(
        SQLEnum(CodeEnum, name='code_enum'),
        unique=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)


class Account(Base):
    __tablename__ = 'accounts'

    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'),
        nullable=False
    )
    currency_id: Mapped[int] = mapped_column(
        ForeignKey('currencies.id'),
        nullable=False
    )
    balance: Mapped[DECIMAL] = mapped_column(
        DECIMAL(18, 2),
        server_default='0',
        nullable=False
    )
    status: Mapped[AccountStatusEnum] = mapped_column(
        SQLEnum(AccountStatusEnum, name='account_status_enum'),
        nullable=False,
        default=AccountStatusEnum.ACTIVE,
    )

    __table_args__ = (
        Index('ix_account_fk_user_id', 'user_id'),
        UniqueConstraint('user_id', 'currency_id'),
        CheckConstraint('balance >= 0', name='check_balance_non_negative'),
    )


class Transfer(Base):
    __tablename__ = 'transfers'

    public_id: Mapped[UUID] = mapped_column(
        default=uuid4,
        unique=True,
        nullable=False
    )
    from_account_id: Mapped[int] = mapped_column(ForeignKey('accounts.id'))
    to_account_id: Mapped[int] = mapped_column(ForeignKey('accounts.id'))
    amount: Mapped[DECIMAL] = mapped_column(
        DECIMAL(18, 2),
        nullable=False,
    )
    status: Mapped[StatusEnum] = mapped_column(
        SQLEnum(StatusEnum, name='transfer_status_enum'),
        nullable=False,
    )

    __table_args__ = (
        Index('ix_transfers_from_account_id', 'from_account_id'),
        Index('ix_transfers_to_account_id', 'to_account_id'),
        Index('ix_transfers_status', 'status'),
        CheckConstraint('amount > 0', name='check_tf_amount_non_negative'),
    )


class Transaction(Base):
    __tablename__ = 'transactions'

    account_id: Mapped[int] = mapped_column(ForeignKey('accounts.id'))
    reference: Mapped[int | None] = mapped_column(
        ForeignKey('transfers.id'),
        nullable=False
    )
    type: Mapped[TransactionTypeEnum] = mapped_column(
    SQLEnum(TransactionTypeEnum, name='transaction_type_enum'),
        nullable=False,
    )
    amount: Mapped[DECIMAL] = mapped_column(DECIMAL(18, 2))
    status: Mapped[StatusEnum] = mapped_column(
        SQLEnum(StatusEnum, name='transaction_status_enum'),
        nullable=False,
    )

    __table_args__ = (
        Index('ix_transactions_account_id', 'account_id'),
        CheckConstraint('amount > 0', name='check_tr_amount_non_negative'),
    )

