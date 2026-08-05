import pytest

from app.main import app, bank


@pytest.fixture
def client():
    bank.accounts.clear()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_create_account(client):
    resp = client.post("/accounts", json={"owner": "Alice", "initial_balance": 100})
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["owner"] == "Alice"
    assert body["balance"] == 100


def test_create_account_missing_owner(client):
    resp = client.post("/accounts", json={"initial_balance": 100})
    assert resp.status_code == 400


def test_get_unknown_account_404(client):
    resp = client.get("/accounts/999")
    assert resp.status_code == 404


def test_deposit_and_withdraw_flow(client):
    created = client.post("/accounts", json={"owner": "Alice", "initial_balance": 0})
    account_id = created.get_json()["id"]

    dep = client.post(f"/accounts/{account_id}/deposit", json={"amount": 100})
    assert dep.status_code == 200
    assert dep.get_json()["balance"] == 100

    wd = client.post(f"/accounts/{account_id}/withdraw", json={"amount": 40})
    assert wd.status_code == 200
    assert wd.get_json()["balance"] == 60


def test_withdraw_insufficient_funds_returns_409(client):
    created = client.post("/accounts", json={"owner": "Alice", "initial_balance": 10})
    account_id = created.get_json()["id"]

    wd = client.post(f"/accounts/{account_id}/withdraw", json={"amount": 100})
    assert wd.status_code == 409


def test_transfer_between_accounts(client):
    a = client.post("/accounts", json={"owner": "Alice", "initial_balance": 100}).get_json()
    b = client.post("/accounts", json={"owner": "Bob", "initial_balance": 0}).get_json()

    resp = client.post(
        "/transfer", json={"from_id": a["id"], "to_id": b["id"], "amount": 30}
    )
    assert resp.status_code == 200

    balance_a = client.get(f"/accounts/{a['id']}").get_json()["balance"]
    balance_b = client.get(f"/accounts/{b['id']}").get_json()["balance"]
    assert balance_a == 70
    assert balance_b == 30
