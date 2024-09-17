from typing import Any

import numpy as np
import torch
from pydantic import BaseModel, Field


class DataPacket(BaseModel):
    data: Any = Field(..., description="Data to be sent")


class TextPacket(DataPacket):
    data: str = Field(..., description="Text data to be sent")


# class VectorPacket(DataPacket):
#     data: np.ndarray | torch.Tensor = Field(..., description="Vector data to be sent")


# class ImagePacket(DataPacket):
#     data: np.ndarray | torch.Tensor = Field(..., description="Image data to be sent")
