from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class Client:
    name: str
    credits: float = 0.0
    sales: List[Dict] = field(default_factory=list)
    credit_history: List[Dict] = field(default_factory=list)
