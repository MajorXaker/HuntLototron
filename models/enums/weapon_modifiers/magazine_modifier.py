from enum import StrEnum


class MagazineEnum(StrEnum):
    NO_DESIGNATED = "no_designated"  # just regular magazine
    EXTENDED = "extended"
    SWIFT = "swift"  # fast reloader
    CHAIN = "chain"  # the one and only caldwell chain revolver
