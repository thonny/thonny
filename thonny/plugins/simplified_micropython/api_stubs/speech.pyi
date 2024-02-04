"""
See http://microbit-micropython.readthedocs.io/en/latest/speech.html
for details
"""

def translate(words: str) ->None:
    """
    Given English words in the string words, return a string
    containing a best guess at the appropriate phonemes to pronounce.
    The output is generated from this text to phoneme translation table.
    This function should be used to generate a first approximation of phonemes
    that can be further hand-edited to improve accuracy, inflection and emphasis.
    """

def pronounce(phonemes: str, pitch: int=64, speed: int=72,
              mouth: int=128, throat: int=128)->None:
    """
    Pronounce the phonemes in the string phonemes. See below for details of how
    to use phonemes to finely control the output of the speech synthesiser.
    Override the optional pitch, speed, mouth and throat settings to change
    the timbre (quality) of the voice.
    """

def say(words: str, pitch: int=64, speed: int=72,
              mouth: int=128, throat: int=128)->None:
    """
    Say the English words in the string words. The result is semi-accurate
    for English.
    Override the optional pitch, speed, mouth and throat settings to change
    the timbre (quality) of the voice. This is a short-hand equivalent of:
    speech.pronounce(speech.translate(words))
    """

def sing(phonemes: str, pitch: int=64, speed: int=72,
              mouth: int=128, throat: int=128)->None:
    """
    Sing the phonemes contained in the string phonemes. Changing the pitch
    and duration of the note is described below. Override the optional pitch,
    speed, mouth and throat settings to change the timbre (quality) of the voice.
    """
