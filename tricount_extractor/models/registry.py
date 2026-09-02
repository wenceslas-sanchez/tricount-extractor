from dataclasses import dataclass
import datetime
import pandas as pd
import json
from tricount_extractor.models.member import Member
from tricount_extractor.models.entry import Entry
from tricount_extractor.models.pagination import Pagination


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
            "split_view": self._to_split_view_dataframe(),
        }

    def _to_entries_dataframe(self) -> pd.DataFrame:
        rows = [e.to_dict() for e in self.entries]
        return pd.DataFrame(rows).sort_values("date").reset_index(drop=True)

    def _to_allocations_dataframe(self) -> pd.DataFrame:
        rows = [d for e in self.entries for d in e.to_allocation_dicts()]
        return pd.DataFrame(rows).sort_values("date").reset_index(drop=True)

    def _to_balance_dataframe(self) -> pd.DataFrame:
        balances = {m.display_name: 0.0 for m in self.members}
        for e in self.entries:
            balances[e.payer_name] += e.amount.value
            for a in e.allocations:
                balances[a.member_name] -= a.amount.value
        rows = [{"member": k, "balance": round(v, 2)} for k, v in balances.items()]
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

    def _to_split_view_dataframe(self) -> pd.DataFrame:
        member_names = sorted([m.display_name for m in self.members])
        rows = []

        for e in self.entries:
            row = {
                "Date": e.date.strftime("%Y-%m-%d"),
                "Description": e.description,
                "Category": e.category,
                "Type": e.transaction_type_label,
                "Cost": e.amount.value if not e.is_reimbursement else 0.0,
                "Currency": e.amount.currency,
            }

            allocation_map = {a.member_name: a.amount.value for a in e.allocations}
            for member_name in member_names:
                amount_owed = allocation_map.get(member_name, 0.0)
                amount_paid = e.amount.value if member_name == e.payer_name else 0.0
                row[member_name] = amount_owed - amount_paid

            rows.append(row)

        if not rows:
            columns = ["Date", "Description", "Category", "Type", "Cost", "Currency"] + member_names
            return pd.DataFrame(columns=columns)

        return pd.DataFrame(rows).sort_values("Date").reset_index(drop=True)
