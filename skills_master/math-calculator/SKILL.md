---
name: math-calculator
description: Calculate numbers, costs, budgets, and estimates. Use when user asks to "calculate", "work out", "estimate the cost", "how much is", "what percentage", "how long will it take", or any quantitative analysis.
user-invocable: true
---

# Math & Calculation — Quantified Answers

Use this skill when the user needs quantitative answers — calculations, estimates, cost breakdowns, percentages, time/distance estimates, or data analysis.

## When to Use

- "Calculate how much..."
- "Work out the cost of..."
- "What percentage is..."
- "How long will it take..."
- "Estimate the total..."
- "Compare the cost of..."
- "How much deposit do I need?"
- "What's the compound interest?"
- "What's the ROI?"

## Calculation Types

### Financial Calculations

```python
# Compound interest / investment growth
def compound_growth(principal: float, rate: float, years: int, 
                    monthly_contribution: float = 0) -> dict:
    """Calculate investment growth over time."""
    balance = principal
    yearly_values = []
    
    for year in range(years):
        yearly_values.append({
            "year": year + 1,
            "start_balance": round(balance, 2),
            "interest": round(balance * rate, 2),
            "contribution": round(monthly_contribution * 12, 2),
            "end_balance": round(balance * (1 + rate) + monthly_contribution * 12, 2)
        })
        balance = balance * (1 + rate) + monthly_contribution * 12
    
    return {
        "final_value": round(balance, 2),
        "total_contributions": round(principal + monthly_contribution * 12 * years, 2),
        "total_interest": round(balance - principal - monthly_contribution * 12 * years, 2),
        "yearly_breakdown": yearly_values
    }

# Loan / mortgage repayment
def loan_repayment(principal: float, annual_rate: float, years: int) -> dict:
    """Calculate monthly loan repayment using amortisation formula."""
    monthly_rate = annual_rate / 12
    num_payments = years * 12
    
    if monthly_rate == 0:
        monthly_payment = principal / num_payments
    else:
        monthly_payment = principal * (monthly_rate * (1 + monthly_rate)**num_payments) / \
                          ((1 + monthly_rate)**num_payments - 1)
    
    total_paid = monthly_payment * num_payments
    total_interest = total_paid - principal
    
    return {
        "monthly_repayment": round(monthly_payment, 2),
        "total_paid": round(total_paid, 2),
        "total_interest": round(total_interest, 2),
        "effective_annual_rate": round((monthly_payment * 12 / principal - 1) * 100, 2)
    }

# Budget allocation (50/30/20 rule)
def budget_allocation(monthly_income: float) -> dict:
    """50/30/20 budget breakdown."""
    return {
        "needs_50": round(monthly_income * 0.50, 2),
        "wants_30": round(monthly_income * 0.30, 2),
        "savings_debt_20": round(monthly_income * 0.20, 2),
        "total": monthly_income
    }
```

### Time & Duration Calculations

```python
import datetime

def time_until(target_date: str, from_date: str = None) -> dict:
    """Calculate time remaining until a date."""
    target = datetime.date.fromisoformat(target_date)
    start = datetime.date.fromisoformat(from_date) if from_date else datetime.date.today()
    
    delta = target - start
    weeks = delta.days // 7
    remaining_days = delta.days % 7
    
    return {
        "days": delta.days,
        "weeks": weeks,
        "months": round(delta.days / 30.44, 1),
        "years": round(delta.days / 365.25, 2),
        "formatted": f"{weeks} weeks, {remaining_days} days",
        "urgency": "high" if delta.days <= 7 else "medium" if delta.days <= 30 else "normal"
    }

def estimate_duration(task_type: str, complexity: str, 
                     has_experience: bool = False) -> dict:
    """Estimate task duration."""
    
    base_hours = {
        "research": {"simple": 1, "moderate": 3, "complex": 8},
        "writing": {"simple": 0.5, "moderate": 2, "complex": 5},
        "coding": {"simple": 1, "moderate": 4, "complex": 16},
        "review": {"simple": 0.5, "moderate": 1, "complex": 3},
        "meeting": {"simple": 0.5, "moderate": 1, "complex": 2}
    }
    
    base = base_hours.get(task_type, {}).get(complexity, 2)
    
    if has_experience:
        base *= 0.7  # 30% faster with experience
    
    return {
        "estimate_hours": round(base, 1),
        "with_buffer": round(base * 1.3, 1),  # 30% buffer for planning
        "formatted": f"{round(base * 1.3)} hours" if base < 8 else f"{round(base * 1.3 / 8, 1)} days"
    }
```

### Percentage & Ratio Calculations

```python
def percentage_calculations(numerator: float, denominator: float) -> dict:
    """All percentage-related calculations."""
    if denominator == 0:
        return {"error": "Cannot divide by zero"}
    
    pct = (numerator / denominator) * 100
    return {
        "percentage": round(pct, 2),
        "formatted": f"{round(pct, 1)}%",
        "decimal": round(pct / 100, 4),
        "inverse": round((denominator - numerator) / denominator * 100, 2),
        "difference": round(pct - 100, 2)  # difference from 100%
    }

def proportion_of_budget(amount: float, budget: float) -> dict:
    """What % of budget is this amount?"""
    pct = (amount / budget) * 100
    return {
        "percentage": round(pct, 1),
        "remaining": round(budget - amount, 2),
        "remaining_pct": round(100 - pct, 1),
        "within_budget": amount <= budget,
        "warning": "Over budget by " + f"${round(amount - budget, 2)}" if amount > budget else "OK"
    }
```

### Unit Conversions

```python
conversions = {
    # Distance
    "km_to_miles": lambda km: round(km * 0.621371, 2),
    "miles_to_km": lambda miles: round(miles * 1.60934, 2),
    "m_to_ft": lambda m: round(m * 3.28084, 2),
    
    # Weight
    "kg_to_lb": lambda kg: round(kg * 2.20462, 2),
    "lb_to_kg": lambda lb: round(lb * 0.453592, 2),
    
    # Temperature
    "c_to_f": lambda c: round(c * 9/5 + 32, 1),
    "f_to_c": lambda f: round((f - 32) * 5/9, 1),
    
    # Data
    "bytes_to_mb": lambda b: round(b / 1024 / 1024, 2),
    "gb_to_bytes": lambda gb: int(gb * 1024 * 1024 * 1024),
    
    # Time
    "hours_to_days": lambda h: round(h / 8, 1),  # working days
    "minutes_to_hours": lambda m: round(m / 60, 2)
}
```

## Calculation Output Format

```markdown
## Calculation: [Topic]

**Question:** [What was asked]

### Answer
**$[result]** or **[result]** (depending on type)

### Breakdown
- [Component 1]: $[value]
- [Component 2]: $[value]
- Total: $[sum]

### Method
[1 line explaining how the calculation was done]

### Assumptions
- [Assumption 1 — if any]
- [Assumption 2]

### Sensitivity
- If [variable] changes by ±10%: result changes by ±$[amount]
- Best case: $[best]
- Worst case: $[worst]

### Quick Check
[Back-of-envelope estimate to verify reasonability]
```

## Common Calculation Traps

```python
traps = {
    "nominal_vs_real": "6% return vs real return of 4% (after inflation) — very different",
    "missing_periods": "10% over 1 year ≠ 10% over 5 years (use compound)",
    "average_vs_total": "Average cost of $50 doesn't mean total is $50",
    "hidden_fees": "Always check for: setup fees, exit fees, stamp duty, GST",
    "pro_rata": "First month prorated? Start mid-month = partial week",
    "tax_inclusive": "GST-inclusive prices vs ex-GST — multiply/divide by 1.1",
    "deposit_calculation": "Deposit is % of purchase price, not loan amount",
    "interest_on_interest": "Simple interest ≠ compound interest — always clarify"
}
```

## Australian-Specific Calculations

```python
australian_calcs = {
    "gst": {
        "add_gst": lambda amount: round(amount * 1.10, 2),
        "remove_gst": lambda amount: round(amount / 1.10, 2),
        "gst_component": lambda amount: round(amount - amount / 1.10, 2)
    },
    "hecs": {
        "repayment_rate": lambda income: {
            "0-51800": 0.0,
            "51801-63500": 0.01,
            "63501-72400": 0.02,
            "72401-84700": 0.025,
            "84701-97700": 0.03,
            "97701-110600": 0.035,
            "110601-99999999": 0.04
        }
    },
    "super_contribution": {
        "2024_25": 0.115,  # 11.5%
        "2025_26": 0.12,   # 12%
        "sacrifice": lambda salary, pct: round(salary * pct, 2)
    },
    "ATO_deduction": {
        "19c_km": 0.85,  # 2025 rate (lower value)
        "cents_km": lambda km: round(km * 0.85, 2),
        "log_book": lambda fuel: round(fuel * 0.13, 2)
    }
}
```

## Sources

- ATO deduction rates — ato.gov.au
- Mortgage calculators — moneysmart.gov.au
- Compound interest — investor.gov.au