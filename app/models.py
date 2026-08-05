"""
Modèles métier pour la mini API bancaire.

Règles métier volontairement strictes (pense compliance bancaire) :
- Un compte ne peut pas être créé avec un solde négatif
- Un dépôt/retrait doit être un montant strictement positif
- Un retrait ne peut pas mettre le compte à découvert
- Un virement doit respecter les deux règles ci-dessus sur les deux comptes
"""
from dataclasses import dataclass
from itertools import count
from typing import Dict


class InsufficientFundsError(Exception):
    pass


class InvalidAmountError(Exception):
    pass


class AccountNotFoundError(Exception):
    pass


_id_counter = count(1)


@dataclass
class Account:
    id: int
    owner: str
    balance: float = 0.0


class Bank:
    """Stockage en mémoire (volontairement simple pour se concentrer sur CI/CD,
    pas sur la persistance)."""

    def __init__(self) -> None:
        self.accounts: Dict[int, Account] = {}

    def create_account(self, owner: str, initial_balance: float = 0.0) -> Account:
        if initial_balance < 0:
            raise InvalidAmountError("Le solde initial ne peut pas être négatif")
        account = Account(id=next(_id_counter), owner=owner, balance=initial_balance)
        self.accounts[account.id] = account
        return account

    def get_account(self, account_id: int) -> Account:
        if account_id not in self.accounts:
            raise AccountNotFoundError(f"Compte {account_id} introuvable")
        return self.accounts[account_id]

    def deposit(self, account_id: int, amount: float) -> Account:
        if amount <= 0:
            raise InvalidAmountError("Le montant doit être strictement positif")
        account = self.get_account(account_id)
        account.balance += amount
        return account

    def withdraw(self, account_id: int, amount: float) -> Account:
        if amount <= 0:
            raise InvalidAmountError("Le montant doit être strictement positif")
        account = self.get_account(account_id)
        if account.balance < amount:
            raise InsufficientFundsError("Solde insuffisant")
        account.balance -= amount
        return account

    def transfer(self, from_id: int, to_id: int, amount: float) -> None:
        self.withdraw(from_id, amount)
        try:
            self.deposit(to_id, amount)
        except AccountNotFoundError:
            # rollback si le compte destinataire n'existe pas
            self.deposit(from_id, amount)
            raise
