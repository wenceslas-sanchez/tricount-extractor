from dataclasses import  dataclass
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
            pagination=Pagination.from_json(data["Pagination"])
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
            "balances": self._to_balance_dataframe()
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
            balances[e.payer_name] += abs(e.amount.value)
            for a in e.allocations:
                balances[a.member_name] -= abs(a.amount.value)
        rows = [{"member": k, "balance": round(v, 2)} for k, v in balances.items()]
        return pd.DataFrame(rows).sort_values("balance", ascending=False).reset_index(drop=True)

    def _to_members_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame([m.to_dict() for m in self.members])
