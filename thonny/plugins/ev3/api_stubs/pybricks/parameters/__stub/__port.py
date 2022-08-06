from enum import Enum


class Port(Enum):
    """
    Port on the programmable brick or hub.

    Note:
        Motor Ports: A, B, C, D
        Sensor Ports: S1, S2, S3, S4
    """
    A = 'A'
    B = 'B'
    C = 'C'
    D = 'D'
    S1 = 'S1'
    S2 = 'S2'
    S3 = 'S3'
    S4 = 'S4'
