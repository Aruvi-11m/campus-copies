"""
Campus Copies ERP - Pricing Engine Service

Calculates print job pricing, enforces color/orientation constraints, and provides bankers rounding.
Grounding: docs/BusinessRules.md §4, docs/BackendSpecification.md §8
"""

from decimal import Decimal, ROUND_HALF_EVEN
from typing import Dict, Optional, Tuple
from sqlalchemy.orm import Session

from app.core.errors import ValidationError
from app.models.enums import BindingTypeEnum, ColorModeEnum, PrintSideEnum
from app.models.pricing_setting import PricingSetting
from app.repositories.order_repository import OrderRepository


class PricingService:
    def __init__(self, db: Session):
        self.db = db
        self.order_repo = OrderRepository(db)

    @staticmethod
    def bankers_round(value: float) -> float:
        """Rounds float/decimal to 2 decimal places using Bankers' Rounding (ROUND_HALF_EVEN)."""
        d = Decimal(str(value))
        rounded = d.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)
        return float(rounded)

    def calculate_price(
        self,
        print_side: PrintSideEnum,
        color_mode: ColorModeEnum,
        binding_type: BindingTypeEnum,
        copies: int,
        page_count: int,
        custom_pricing: Optional[PricingSetting] = None,
    ) -> Tuple[float, float, float]:
        """
        Calculates per-page price, binding price, and total price.
        Formula: Total = (page_count * per_page_price * copies) + binding_price
        Returns (per_page_price, binding_price, total_price)
        """
        # Validate copies limit (1..100)
        if copies < 1 or copies > 100:
            raise ValidationError("Copies count must be between 1 and 100")

        if page_count < 1:
            raise ValidationError("Page count must be at least 1")

        # Validate Color Rule: Color mode requires SINGLE_SIDE
        if color_mode == ColorModeEnum.COLOR and print_side != PrintSideEnum.SINGLE_SIDE:
            raise ValidationError("Color printing is only supported for Single Side orientation")

        # Load active pricing rates
        pricing = custom_pricing or self.order_repo.get_current_pricing_settings()

        # Determine per-page rate
        if color_mode == ColorModeEnum.COLOR:
            per_page_rate = float(pricing.color_single_side)
        else:
            if print_side == PrintSideEnum.SINGLE_SIDE:
                per_page_rate = float(pricing.bw_single_side)
            elif print_side == PrintSideEnum.DOUBLE_SIDE:
                per_page_rate = float(pricing.bw_double_side)
            elif print_side == PrintSideEnum.MULTI_PAGE:
                per_page_rate = float(pricing.bw_multi_page)
            else:
                per_page_rate = float(pricing.bw_single_side)

        # Determine binding rate
        if binding_type == BindingTypeEnum.NONE:
            binding_rate = 0.00
        elif binding_type == BindingTypeEnum.SPIRAL:
            binding_rate = float(pricing.spiral_binding_price)
        elif binding_type == BindingTypeEnum.SOFT_COVER:
            binding_rate = float(pricing.soft_binding_price)
        elif binding_type == BindingTypeEnum.HARD_COVER:
            binding_rate = float(pricing.hard_binding_price)
        elif binding_type == BindingTypeEnum.STAPLE_PINS:
            binding_rate = float(pricing.stapling_price)
        else:
            binding_rate = 0.00

        # Calculate totals
        raw_print_cost = page_count * per_page_rate * copies
        raw_total = raw_print_cost + binding_rate

        per_page_price = self.bankers_round(per_page_rate)
        binding_price = self.bankers_round(binding_rate)
        total_price = self.bankers_round(raw_total)

        return per_page_price, binding_price, total_price
