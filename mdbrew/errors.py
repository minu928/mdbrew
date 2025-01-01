# fmt: off
class NotSupportFileFormat(Exception):
    def __init__(self, fmt, supports):
        super().__init__(f"File formate {fmt} is not supported. We support {supports}.")
        
class AttributeIsNoneError(Exception):
    def __init__(self, attr: str):
        super().__init__(f"{attr.capitalize()} is None.")
        
class NotEqualFrameError(Exception): ...
