import datetime
import pytest

from tricount_extractor.models.allocation import Allocation
from tricount_extractor.models.amount import Amount
from tricount_extractor.models.entry import Entry, EntryType, EntryTypeTransaction


@pytest.fixture
def normal_expense_entry():
    """A normal expense entry."""
    return Entry(
        id=1,
        uuid="entry-001",
        created=datetime.datetime(2025, 1, 1),
        date=datetime.datetime(2025, 1, 1),
        description="Lunch",
        amount=Amount(currency="USD", value=-20.0),
        amount_local=Amount(currency="USD", value=-20.0),
        status="ACTIVE",
        type=EntryType.MANUAL,
        type_transaction=EntryTypeTransaction.NORMAL,
        payer_uuid="user-a",
        payer_name="Alice",
        category="FOOD",
        allocations=[],
    )


@pytest.fixture
def income_entry():
    """An income entry."""
    return Entry(
        id=2,
        uuid="entry-002",
        created=datetime.datetime(2025, 1, 2),
        date=datetime.datetime(2025, 1, 2),
        description="Refund",
        amount=Amount(currency="USD", value=100.0),
        amount_local=Amount(currency="USD", value=100.0),
        status="ACTIVE",
        type=EntryType.MANUAL,
        type_transaction=EntryTypeTransaction.INCOME,
        payer_uuid="user-b",
        payer_name="Bob",
        category="INCOME",
        allocations=[],
    )


@pytest.fixture
def reimbursement_entry():
    """A balance/reimbursement entry."""
    return Entry(
        id=3,
        uuid="entry-003",
        created=datetime.datetime(2025, 1, 3),
        date=datetime.datetime(2025, 1, 3),
        description="Payment",
        amount=Amount(currency="USD", value=-50.0),
        amount_local=Amount(currency="USD", value=-50.0),
        status="ACTIVE",
        type=EntryType.MANUAL,
        type_transaction=EntryTypeTransaction.BALANCE,
        payer_uuid="user-a",
        payer_name="Alice",
        category="BALANCE",
        allocations=[],
    )


def test_is_income_returns_true_for_income_entry(income_entry):
    """Test that is_income property returns True for INCOME transaction type."""
    assert income_entry.is_income is True


def test_is_income_returns_false_for_normal_entry(normal_expense_entry):
    """Test that is_income property returns False for NORMAL transaction type."""
    assert normal_expense_entry.is_income is False


def test_is_income_returns_false_for_reimbursement(reimbursement_entry):
    """Test that is_income property returns False for BALANCE transaction type."""
    assert reimbursement_entry.is_income is False


def test_transaction_type_label_for_expense(normal_expense_entry):
    """Test that transaction_type_label returns 'Expense' for normal entries."""
    assert normal_expense_entry.transaction_type_label == "Expense"


def test_transaction_type_label_for_income(income_entry):
    """Test that transaction_type_label returns 'Income' for income entries."""
    assert income_entry.transaction_type_label == "Income"


def test_transaction_type_label_for_reimbursement(reimbursement_entry):
    """Test that transaction_type_label returns 'Transfer' for balance entries."""
    assert reimbursement_entry.transaction_type_label == "Transfer"


def test_to_dict_includes_is_income(income_entry):
    """Test that to_dict includes is_income field."""
    entry_dict = income_entry.to_dict()
    assert "is_income" in entry_dict
    assert entry_dict["is_income"] is True


def test_to_allocation_dicts_includes_is_income():
    """Test that to_allocation_dicts includes is_income field."""
    entry = Entry(
        id=1,
        uuid="entry-001",
        created=datetime.datetime(2025, 1, 1),
        date=datetime.datetime(2025, 1, 1),
        description="Refund",
        amount=Amount(currency="USD", value=100.0),
        amount_local=Amount(currency="USD", value=100.0),
        status="ACTIVE",
        type=EntryType.MANUAL,
        type_transaction=EntryTypeTransaction.INCOME,
        payer_uuid="user-a",
        payer_name="Alice",
        category="INCOME",
        allocations=[
            Allocation(
                member_uuid="user-a",
                member_name="Alice",
                amount=Amount(currency="USD", value=50.0),
                amount_local=Amount(currency="USD", value=50.0),
                type="RATIO",
                share_ratio=1,
            ),
        ],
    )

    allocation_dicts = entry.to_allocation_dicts()
    assert len(allocation_dicts) == 1
    assert "is_income" in allocation_dicts[0]
    assert allocation_dicts[0]["is_income"] is True
    assert allocation_dicts[0]["is_reimbursement"] is False
