from dataclasses import dataclass
from typing import Literal
from tricount_extractor.models.amount import Amount
import enum


class AllocationType(enum.StrEnum):
    RATIO = "RATIO"
    AMOUNT = "AMOUNT"


@dataclass
class Allocation:
    amount: Amount
    member_uuid: str
    member_name: str
    type: AllocationType
    share_ratio: int | None = None

    @classmethod
    def from_json(cls, data: dict) -> Allocation:
        membership = data["membership"].get(
            "RegistryMembershipNonUser", data["membership"]
        )
        return cls(
            amount=Amount.from_json(data["amount"]),
            member_uuid=membership["uuid"],
            member_name=membership["alias"]["display_name"],
            type=AllocationType(data["type"]),
            share_ratio=data.get("share_ratio"),
        )

    def to_dict(self) -> dict:
        return {
            "participant": self.member_name,
            "share": abs(self.amount.value),
            "currency": self.amount.currency,
        }
