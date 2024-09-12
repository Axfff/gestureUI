class Event:
    def gatherAttrs(self):
        return ",".join("{}={}"
                        .format(k, getattr(self, k))
                        for k in self.__dict__.keys())

    def __repr__(self):
        return "<{}: {}>".format(self.__class__.__name__, self.gatherAttrs())


class TapStart(Event):
    def __init__(self, position):
        self.position = position


class Tap(Event):
    def __init__(self, position, tapTime):
        self.position = position
        self.tapTime = tapTime


class TapEnd(Event):
    def __init__(self, position, tapTime):
        self.position = position
        self.tapTime = tapTime


class TapTimeOut(Event):
    def __init__(self, position):
        self.position = position


class PressWaiting(Event):
    def __init__(self, position, progress):
        self.position = position
        self.progress = progress


class PressStart(Event):
    def __init__(self, position):
        self.position = position


class Press(Event):
    def __init__(self, position, pressTime):
        self.position = position
        self.pressTime = pressTime


class PressEnd(Event):
    def __init__(self, position, pressTime):
        self.position = position
        self.pressTime = pressTime


class DraggingStart(Event):
    def __init__(self, absolutePos, relativePos):
        self.absolutePos = absolutePos
        self.relativePos = relativePos


class Dragging(Event):
    def __init__(self, absolutePos, relativePos):
        self.absolutePos = absolutePos
        self.relativePos = relativePos


class DraggingEnd(Event):
    def __init__(self, absolutePos, relativePos):
        self.absolutePos = absolutePos
        self.relativePos = relativePos


class CursorPosition(Event):
    def __init__(self, position):
        self.position = position


class SuspendingStart(Event):
    def __init__(self, position):
        self.position = position


class Suspending(Event):
    def __init__(self, position):
        self.position = position


class SuspendingEnd(Event):
    def __init__(self, position):
        self.position = position


class HoldingStart(Event):
    pass


class Holding(Event):
    def __init__(self, progress, holdingTime):
        self.progress = progress
        self.holdingTime = holdingTime


class HoldingFinish(Event):
    pass


class HoldingFinish_infinite(Event):
    def __init__(self, HoldingTime):
        self.HoldingTime = HoldingTime


class HoldingCancel(Event):
    pass


class Add(Event):
    pass


class Reduce(Event):
    pass


class FixedLengthNumInput_event(Event):
    def __init__(self, numInput: list):
        self.numInput = numInput


if __name__ == '__main__':
    a = Holding(1, 1)
    print([a])
