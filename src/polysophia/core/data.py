from datetime import datetime, timezone
from typing import Any

import numpy as np
import torch
from pydantic import BaseModel, Field
from pydantic.types import constr


class DataPacket(BaseModel):
    data: Any = Field(..., description="Data to be sent")
    timestamp: datetime = Field(
        datetime.now(timezone.utc), description="Timestamp of the data"
    )


class TextPacket(DataPacket):
    data: constr(strict=True) = Field(..., description="Text data to be sent")


# class VectorPacket(DataPacket):
#     data: np.ndarray | torch.Tensor = Field(..., description="Vector data to be sent")


# class ImagePacket(DataPacket):
#     data: np.ndarray | torch.Tensor = Field(..., description="Image data to be sent")
