from enum import Enum


class OrderStatus(str, Enum):
    NEW = "NEW"
    PENDING = "PENDING"
    PREPARING = "PREPARING"
    ON_THE_WAY = "ON_THE_WAY"
    DONE = "DONE"
    DELETED = "DELETED"
    RESTAURANT_CANCELLED = "RESTAURANT_CANCELLED"
    CUSTOMER_CANCELLED = "CUSTOMER_CANCELLED"

    def __str__(self):
        return '%s' % self.value
