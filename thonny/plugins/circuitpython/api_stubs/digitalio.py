class DigitalInOut:
    ""

    def deinit():
        pass

    direction = None
    drive_mode = None
    pull = None

    def switch_to_input():
        pass

    def switch_to_output():
        pass

    value = None


class Direction:
    ""
    INPUT = None
    OUTPUT = None


class DriveMode:
    ""
    OPEN_DRAIN = None
    PUSH_PULL = None


class Pull:
    ""
    DOWN = None
    UP = None
