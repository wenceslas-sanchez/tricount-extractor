from dataclasses import dataclass
import datetime
import enum
from tricount_extractor.models.amount import Amount
from tricount_extractor.models.allocation import Allocation


class EntryType(enum.StrEnum):
    MANUAL = "MANUAL"


class EntryTypeTransaction(enum.StrEnum):
    NORMAL = "NORMAL"
    BALANCE = "BALANCE"


@dataclass
class Entry:
    id: int
    uuid: str
    created: datetime.datetime
    date: datetime.datetime
    description: str
    amount: Amount
    status: str
    type: EntryType
    type_transaction: EntryTypeTransaction
    payer_uuid: str
    payer_name: str
    allocations: list[Allocation]
    category: str

    @classmethod
    def from_json(cls, data: dict) -> Entry:
        data = data.get("RegistryEntry", data)
        payer = data["membership_owned"].get(
            "RegistryMembershipNonUser", data["membership_owned"]
        )
        return cls(
            id=data["id"],
            uuid=data["uuid"],
            created=datetime.datetime.fromisoformat(data["created"]),
            date=datetime.datetime.fromisoformat(data["date"]),
            description=data["description"],
            amount=Amount.from_json(data["amount"]),
            status=data["status"],
            type=EntryType(data["type"]),
            type_transaction=EntryTypeTransaction(data["type_transaction"]),
            payer_uuid=payer["uuid"],
            payer_name=payer["alias"]["display_name"],
            allocations=[Allocation.from_json(a) for a in data["allocations"]],
            category=data.get("category", "UNCATEGORIZED"),
        )

    @property
    def is_reimbursement(self) -> bool:
        return self.type_transaction is EntryTypeTransaction.BALANCE

    def to_dict(self) -> dict:
        return {
            "entry_id": self.id,
            "date": self.date,
            "description": self.description,
            "amount": abs(self.amount.value),
            "currency": self.amount.currency,
            "payer": self.payer_name,
            "is_reimbursement": self.is_reimbursement,
            "category": self.category,
        }

    def to_allocation_dicts(self) -> list[dict]:
        base = {
            "entry_id": self.id,
            "date": self.date,
            "description": self.description,
            "payer": self.payer_name,
            "is_reimbursement": self.is_reimbursement,
        }
        return [{**base, **a.to_dict()} for a in self.allocations]
