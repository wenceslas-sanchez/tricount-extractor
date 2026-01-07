from dataclasses import dataclass


@dataclass
class Member:
    id: int
    uuid: str
    display_name: str
    status: str

    @classmethod
    def from_json(cls, data: dict) -> Member:
        d = data.get("RegistryMembershipNonUser", data)
        return cls(
            id=d["id"],
            uuid=d["uuid"],
            display_name=d["alias"]["display_name"],
            status=d["status"],
        )

    def to_dict(self) -> dict:
        return {
            "member_id": self.id,
            "member_uuid": self.uuid,
            "member_name": self.display_name,
            "status": self.status,
        }
