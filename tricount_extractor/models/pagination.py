from dataclasses import  dataclass


@dataclass
class Pagination:
    future_url: str | None
    newer_url: str | None
    older_url: str | None

    @classmethod
    def from_json(cls, data: dict) -> Pagination:
        return cls(
            future_url=data.get("future_url"),
            newer_url=data.get("newer_url"),
            older_url=data.get("older_url")
        )
