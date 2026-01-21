from dataclasses import dataclass
from typing import List, Dict

@dataclass
class SaleItem:
    name: str
    price: float
    quantity: int = 1
    line_total: float = 0.0

@dataclass
class Sale:
    id: int
    items: List[Dict]
    total: float
    paid: bool
    paid_amount: float
    date: str
    cancelled: bool = False
