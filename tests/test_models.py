import pytest

from app.models import (
    AccountNotFoundError,
    Bank,
    InsufficientFundsError,
    InvalidAmountError,
)


@pytest.fixture
def bank():
    return Bank()


def test_create_account(bank):
    account = bank.create_account("Alice", 100)
    assert account.owner == "Alice"
    assert account.balance == 100


def test_create_account_negative_balance_rejected(bank):
    with pytest.raises(InvalidAmountError):
        bank.create_account("Alice", -10)


def test_deposit_increases_balance(bank):
    account = bank.create_account("Alice", 100)
    bank.deposit(account.id, 50)
    assert bank.get_account(account.id).balance == 150


def test_deposit_zero_or_negative_rejected(bank):
    account = bank.create_account("Alice", 100)
    with pytest.raises(InvalidAmountError):
        bank.deposit(account.id, 0)
    with pytest.raises(InvalidAmountError):
        bank.deposit(account.id, -5)


def test_withdraw_decreases_balance(bank):
    account = bank.create_account("Alice", 100)
    bank.withdraw(account.id, 30)
    assert bank.get_account(account.id).balance == 70


def test_withdraw_insufficient_funds(bank):
    account = bank.create_account("Alice", 20)
    with pytest.raises(InsufficientFundsError):
        bank.withdraw(account.id, 50)


def test_get_unknown_account_raises(bank):
    with pytest.raises(AccountNotFoundError):
        bank.get_account(9999)


def test_transfer_moves_money(bank):
    a = bank.create_account("Alice", 100)
    b = bank.create_account("Bob", 10)
    bank.transfer(a.id, b.id, 40)
    assert bank.get_account(a.id).balance == 60
    assert bank.get_account(b.id).balance == 50


def test_transfer_rolls_back_if_destination_unknown(bank):
    a = bank.create_account("Alice", 100)
    with pytest.raises(AccountNotFoundError):
        bank.transfer(a.id, 9999, 40)
    # le montant doit être resté sur le compte source (rollback)
    assert bank.get_account(a.id).balance == 100
