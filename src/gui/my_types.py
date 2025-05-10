from typing import Protocol


class CodeBankApp(Protocol):
    def __init__(self):
        self.frames = None

    def show_frame(self, frame_class: type) -> None:
        pass
