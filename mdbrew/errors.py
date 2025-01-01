class NotSupportFileFormat(Exception):
    def __init__(self, fmt, supports):
        super().__init__(f"File formate {fmt} is not supported. We support {supports}.")
