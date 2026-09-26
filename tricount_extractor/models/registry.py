from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import datetime
import pandas as pd
import json
from tricount_extractor.models.member import Member
from tricount_extractor.models.entry import Entry
from tricount_extractor.models.pagination import Pagination


LEDGER_COLUMNS = ["date", "description", "category", "type", "cost", "currency"]


@dataclass
class Registry:
    id: int
    uuid: str
    title: str
    currency: str
    created: datetime.datetime
    updated: datetime.datetime
    members: list[Member]
    entries: list[Entry]
    pagination: Pagination

    @classmethod
    def from_json(cls, data: dict) -> Registry:
        pagination = data["Pagination"]
        data = data["Response"][0]["Registry"]

        return cls(
            id=data["id"],
            uuid=data["uuid"],
            title=data["title"],
            currency=data["currency"],
            created=datetime.datetime.fromisoformat(data["created"]),
            updated=datetime.datetime.fromisoformat(data["updated"]),
            members=[Member.from_json(m) for m in data["memberships"]],
            entries=[Entry.from_json(e) for e in data.get("all_registry_entry", [])],
            pagination=Pagination.from_json(pagination),
        )

    @classmethod
    def from_file(cls, path: str) -> Registry:
        with open(path, "r", encoding="utf-8") as f:
            return cls.from_json(json.load(f))

    def to_dataframe(self) -> dict[str, pd.DataFrame]:
        return {
            "members": self._to_members_dataframe(),
            "entries": self._to_entries_dataframe(),
            "allocations": self._to_allocations_dataframe(),
            "attachments": self._to_attachments_dataframe(),
            "balances": self._to_balance_dataframe(),
            "transaction_ledger": self._to_transaction_ledger_dataframe(),
        }

    def _to_entries_dataframe(self) -> pd.DataFrame:
        rows = [e.to_dict() for e in self.entries]
        return pd.DataFrame(rows).sort_values("date").reset_index(drop=True)

    def _to_allocations_dataframe(self) -> pd.DataFrame:
        rows = [d for e in self.entries for d in e.to_allocation_dicts()]
        return pd.DataFrame(rows).sort_values("date").reset_index(drop=True)

    def _to_balance_dataframe(self) -> pd.DataFrame:
        balances = {m.uuid: 0.0 for m in self.members}
        for e in self.entries:
            for member_uuid, position in e.net_positions().items():
                balances[member_uuid] += position
        labels = self._member_labels()
        rows = [
            {"member": labels[k], "balance": round(v, 2)} for k, v in balances.items()
        ]
        return (
            pd.DataFrame(rows)
            .sort_values("balance", ascending=False)
            .reset_index(drop=True)
        )

    def _to_members_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame([m.to_dict() for m in self.members])

    def _to_attachments_dataframe(self) -> pd.DataFrame:
        rows = [d for e in self.entries for d in e.to_attachment_dicts()]
        if not rows:
            return pd.DataFrame(columns=["entry_id", "url"])
        return pd.DataFrame(rows)

    def _to_transaction_ledger_dataframe(self) -> pd.DataFrame:
        labels = self._member_labels()
        members = sorted(labels.items(), key=lambda item: item[1])
        rows = []

        for e in self.entries:
            row = {
                "date": e.date,
                "description": e.description,
                "category": e.category,
                "type": e.transaction_type_label,
                "cost": 0.0 if e.is_reimbursement else abs(e.amount.value),
                "currency": e.amount.currency,
            }
            positions = e.net_positions()
            for member_uuid, label in members:
                row[label] = positions.get(member_uuid, 0.0)
            rows.append(row)

        if not rows:
            columns = LEDGER_COLUMNS + [label for _, label in members]
            return pd.DataFrame(columns=columns)

        return pd.DataFrame(rows).sort_values("date").reset_index(drop=True)

    def _member_labels(self) -> dict[str, str]:
        """Column label per member uuid; ambiguous display names get the member id."""
        names = Counter(m.display_name for m in self.members)
        return {
            m.uuid: m.display_name
            if names[m.display_name] == 1 and m.display_name not in LEDGER_COLUMNS
            else f"{m.display_name} (#{m.id})"
            for m in self.members
        }
