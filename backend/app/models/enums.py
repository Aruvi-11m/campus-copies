"""
Campus Copies ERP - Database Enum Definitions

Python Enum mappings for PostgreSQL ENUM types.
Grounding: docs/Database.md §2, docs/DatabaseRelationships.md
"""

from enum import Enum


class OrderStatusEnum(str, Enum):
    PENDING_PAYMENT = "PENDING_PAYMENT"
    PAID = "PAID"
    PRINTING = "PRINTING"
    READY_FOR_PICKUP = "READY_FOR_PICKUP"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class PaymentMethodEnum(str, Enum):
    UPI = "UPI"
    CASH = "CASH"


class PrintSideEnum(str, Enum):
    SINGLE_SIDE = "SINGLE_SIDE"
    DOUBLE_SIDE = "DOUBLE_SIDE"
    MULTI_PAGE = "MULTI_PAGE"


class ColorModeEnum(str, Enum):
    BW = "BW"
    COLOR = "COLOR"


class BindingTypeEnum(str, Enum):
    NONE = "NONE"
    SPIRAL = "SPIRAL"
    SOFT_COVER = "SOFT_COVER"
    HARD_COVER = "HARD_COVER"
    STAPLE_PINS = "STAPLE_PINS"


class FileStatusEnum(str, Enum):
    TEMPORARY = "TEMPORARY"
    ATTACHED = "ATTACHED"
    ORPHANED = "ORPHANED"
    DELETED = "DELETED"


class PickupCodeStatusEnum(str, Enum):
    ACTIVE = "ACTIVE"
    USED = "USED"
    EXPIRED = "EXPIRED"


class InventoryCategoryEnum(str, Enum):
    PAPER = "PAPER"
    INK = "INK"
    BINDING = "BINDING"


class InventorySubCategoryEnum(str, Enum):
    NONE = "NONE"
    SPIRAL = "SPIRAL"
    SOFT_COVER = "SOFT_COVER"
    HARD_COVER = "HARD_COVER"
    STAPLE_PINS = "STAPLE_PINS"


class InventoryTxnTypeEnum(str, Enum):
    RESTOCK = "RESTOCK"
    CONSUMPTION = "CONSUMPTION"
    WASTAGE = "WASTAGE"
    ADJUSTMENT = "ADJUSTMENT"


class ActorTypeEnum(str, Enum):
    STUDENT = "STUDENT"
    ADMIN = "ADMIN"
    SYSTEM = "SYSTEM"
