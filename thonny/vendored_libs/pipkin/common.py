class UserError(RuntimeError):
    pass


class CommunicationError(RuntimeError):
    pass


class ProtocolError(RuntimeError):
    pass


class ManagementError(ProtocolError):
    def __init__(self, msg: str, script: str, out: str, err: str):
        super().__init__(self, msg)
        self.script = script
        self.out = out
        self.err = err
