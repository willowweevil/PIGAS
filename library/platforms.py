from enum import Enum, auto


class Platform(Enum):
    """
    An enumeration to represent different operating system platforms.

    Attributes
    ----------
    LINUX : Platform
        Represents the Linux operating system.
    WINDOWS : Platform
        Represents the Windows operating system.
    MACOS : Platform
        Represents the macOS operating system.
    """
    LINUX = auto()
    WINDOWS = auto()
    MACOS = auto()