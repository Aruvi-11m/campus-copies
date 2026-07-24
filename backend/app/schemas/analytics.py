from typing import Union

from pydantic import BaseModel


class ChartDataPoint(BaseModel):
    label: str
    value: Union[int, float]
