from typing import Any

import cv2
from pydantic import Field, StrictInt, field_validator

from polysophia import logger
from polysophia.core.connection import Processor, Publisher


class Camera(Processor):
    name: str = "Camera"
    device: StrictInt = Field(0, description="ID of the camera device", ge=0)

    @field_validator("device")
    @classmethod
    def start_device(cls, value):
        if isinstance(value, int):
            cap = cv2.VideoCapture(value)
        else:
            cap = value

        if not cap.isOpened():
            raise ValueError("Camera device is not connected")
        else:
            logger.success(f"Camera device {value} is connected")
            return cap

    def __del__(self):
        cv2.destroyAllWindows()
        self.device.release()

    def __repr__(self) -> str:
        return f"Camera({self.device})"

    def __str__(self) -> str:
        return self.__repr__()

    def __call__(self, view: bool = False, *args, **kwargs) -> Any:
        ret, frame = self.device.read()
        if ret:
            if view:
                cv2.imshow(self.name, frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    cv2.destroyAllWindows()
            return frame
        else:
            logger.warning("Failed to read frame")
            return None


class CameraPublisher(Publisher):
    def __init__(self, device: StrictInt = 0):
        camera = Camera(device=device)
        super().__init__(name=camera.name, processor=camera)
