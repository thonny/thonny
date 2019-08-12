class AudioOut:
    ""

    def deinit():
        pass

    def pause():
        pass

    paused = None

    def play():
        pass

    playing = None

    def resume():
        pass

    def stop():
        pass


class Mixer:
    ""

    def deinit():
        pass

    def play():
        pass

    playing = None
    sample_rate = None

    def stop_voice():
        pass


class RawSample:
    ""

    def deinit():
        pass

    sample_rate = None


class WaveFile:
    ""
    bits_per_sample = None
    channel_count = None

    def deinit():
        pass

    sample_rate = None
