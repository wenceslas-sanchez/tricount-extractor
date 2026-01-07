from dataclasses import dataclass


@dataclass
class Amount:
    currency: str
    value: float

    @classmethod
    def from_json(cls, data: dict) -> Amount:
        return cls(currency=data["currency"], value=float(data["value"]))
