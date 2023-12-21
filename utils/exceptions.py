class UnknownInsertType(Exception):
    def __init__(self, msg: str):
        self.msg = msg


class NotValidEmailAddressException(Exception):
    def __init__(self, msg: str):
        self.msg = msg
