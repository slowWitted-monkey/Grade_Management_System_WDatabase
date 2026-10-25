from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class GradingPeriod:
    period_id: Optional[int]
    name: str
    period_order: int
    school_year: str
    semester: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
