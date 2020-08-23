
class FrameProvider(object):
    def prepare(self) -> None:
        pass

    def provide_first(self) -> list:
        return []

    def provide_next(self, previous_frame: list) -> list:
        return []

    def complete(self) -> None:
        pass
