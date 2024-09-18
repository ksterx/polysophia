from datetime import datetime, timedelta, timezone
from typing import Any

from pydantic import BaseModel, Field

from .data import DataPacket


class Buffer(BaseModel):
    content: list[DataPacket] = Field(..., description="Data stored in the buffer")
    max_size: int | None = Field(None, description="Maximum size of the buffer")

    def add(self, data: DataPacket):
        self.content.append(data)
        if self.max_size:
            self.content = self.content[-self.max_size :]

    def read(self, n: int = 1) -> list[DataPacket]:
        return self.content[-n:]

    def add_sequence(self, content: list[DataPacket]):
        self.content = self.content + content
        if self.max_size:
            self.content = self.content[-self.max_size :]

    def clear(self):
        self.content.clear()

    @property
    def size(self) -> int:
        return len(self.content)

    @property
    def oldest(self) -> DataPacket:
        return self.content[0]

    @property
    def newest(self) -> DataPacket:
        return self.content[-1]


class Memory(BaseModel):
    buffer: dict[str, Buffer] = Field({}, description="Data stored in the memory")

    def read_buffer(self, key: str) -> Buffer:
        return self.buffer.get(key)

    def read_newest(self, key: str) -> DataPacket:
        return self.buffer.get(key).newest

    def read_newest_n(self, key: str, n: int) -> list[DataPacket]:
        return self.buffer.get(key).content[-n:]

    def read_oldest(self, key: str) -> DataPacket:
        return self.buffer.get(key).oldest

    def read_oldest_n(self, key: str, n: int) -> list[DataPacket]:
        return self.buffer.get(key).content[:n]

    def overwrite_buffer(self, key: str, value: Any):
        self.buffer[key] = value

    def delete_buffer(self, key: str):
        self.buffer.pop(key, None)
