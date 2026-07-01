from enum import Enum


class Flow(str, Enum):

    ORDER = "ORDER"

    SHIPPING = "SHIPPING"

    RETURN = "RETURN"


class Speaker(str, Enum):

    CUSTOMER = "CUSTOMER"

    BOT = "BOT"
