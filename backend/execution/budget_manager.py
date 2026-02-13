import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from decimal import Decimal

logger = logging.getLogger(__name__)

class BudgetManager:
    """
    Tracks the 'Rational Trading Desk' economy.
    Records spending on tools/data and correlates it with trading outcomes.
    """
    
    def __init__(self, log_file: str = "budget_log.json"):
        self.log_file = log_file
        self.total_spend = Decimal("0.00")
        self.purchases = []
        self._load_log()
        
    def _load_log(self):
        try:
            with open(self.log_file, "r") as f:
                data = json.load(f)
                self.total_spend = Decimal(str(data.get("total_spend", "0.00")))
                self.purchases = data.get("purchases", [])
        except FileNotFoundError:
            self.total_spend = Decimal("0.00")
            self.purchases = []
            
    def _save_log(self):
        data = {
            "total_spend": str(self.total_spend),
            "purchases": self.purchases
        }
        with open(self.log_file, "w") as f:
            json.dump(data, f, indent=2)

    def authorize_expense(self, amount: float, tool_name: str, justification: str) -> bool:
        """
        Risk Manager calls this to check if expense is allowed.
        Simple logic: Allow if < $10 total daily spend.
        """
        # Hard cap for demo
        if self.total_spend > Decimal("10.00"):
            logger.warning(f"Budget exceeded! Request for {amount} rejected.")
            return False
            
        return True

    def record_expense(self, amount: float, tool_name: str, tx_hash: str, justification: str):
        """Log a completed payment"""
        expense = {
            "timestamp": datetime.now().isoformat(),
            "tool": tool_name,
            "amount": float(amount),
            "tx_hash": tx_hash,
            "justification": justification
        }
        self.purchases.append(expense)
        self.total_spend += Decimal(str(amount))
        self._save_log()
        logger.info(f"Expense recorded: ${amount} for {tool_name}")

    def get_summary(self) -> Dict:
        return {
            "total_spend": float(self.total_spend),
            "purchase_count": len(self.purchases),
            "recent_purchases": self.purchases[-5:]
        }

# Singleton
budget_manager = BudgetManager()
