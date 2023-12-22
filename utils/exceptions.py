class UnknownInsertType(Exception):
    def __init__(self, msg: str = None):
        self.msg = msg


class NotValidEmailAddressException(Exception):
    def __init__(self, msg: str = None):
        self.msg = msg
