from typing import Any

from pydantic import BaseModel, Field

from .data import DataPacket


class Memory(BaseModel):
    data: dict[str, DataPacket] = Field({}, description="Data stored in the memory")

    def read(self, key: str) -> Any:
        return self.data.get(key)

    def write(self, key: str, value: Any):
        self.data[key] = value

    def delete(self, key: str):
        self.data.pop(key, None)
