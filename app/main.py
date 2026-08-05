from flask import Flask, jsonify, request

from app.models import (
    AccountNotFoundError,
    Bank,
    InsufficientFundsError,
    InvalidAmountError,
)

app = Flask(__name__)
bank = Bank()


def account_to_dict(account):
    return {"id": account.id, "owner": account.owner, "balance": account.balance}


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/accounts")
def list_accounts():
    return jsonify([account_to_dict(a) for a in bank.accounts.values()])


@app.post("/accounts")
def create_account():
    data = request.get_json(force=True, silent=True) or {}
    owner = data.get("owner")
    initial_balance = data.get("initial_balance", 0.0)
    if not owner:
        return jsonify({"error": "Le champ 'owner' est requis"}), 400
    try:
        account = bank.create_account(owner, initial_balance)
    except InvalidAmountError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify(account_to_dict(account)), 201


@app.get("/accounts/<int:account_id>")
def get_account(account_id):
    try:
        account = bank.get_account(account_id)
    except AccountNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    return jsonify(account_to_dict(account))


@app.post("/accounts/<int:account_id>/deposit")
def deposit(account_id):
    data = request.get_json(force=True, silent=True) or {}
    amount = data.get("amount")
    try:
        account = bank.deposit(account_id, amount)
    except (InvalidAmountError, TypeError) as e:
        return jsonify({"error": str(e)}), 400
    except AccountNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    return jsonify(account_to_dict(account))


@app.post("/accounts/<int:account_id>/withdraw")
def withdraw(account_id):
    data = request.get_json(force=True, silent=True) or {}
    amount = data.get("amount")
    try:
        account = bank.withdraw(account_id, amount)
    except (InvalidAmountError, TypeError) as e:
        return jsonify({"error": str(e)}), 400
    except AccountNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except InsufficientFundsError as e:
        return jsonify({"error": str(e)}), 409
    return jsonify(account_to_dict(account))


@app.post("/transfer")
def transfer():
    data = request.get_json(force=True, silent=True) or {}
    from_id = data.get("from_id")
    to_id = data.get("to_id")
    amount = data.get("amount")
    try:
        bank.transfer(from_id, to_id, amount)
    except (InvalidAmountError, TypeError) as e:
        return jsonify({"error": str(e)}), 400
    except AccountNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except InsufficientFundsError as e:
        return jsonify({"error": str(e)}), 409
    return jsonify({"status": "success"})


if __name__ == "__main__":
    app.run(debug=True)
