"""
Portfolio Validation Module.

Compares calculated portfolio positions (from transaction history) against
actual broker statement data to verify accuracy of calculations.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import pandas as pd
from .position import Position
from src.adapters.actual_portfolio_adapter import ActualPortfolioAdapter


class DiscrepancyType(Enum):
    """Types of validation discrepancies."""
    QUANTITY_MISMATCH = "quantity_mismatch"
    COST_BASIS_MISMATCH = "cost_basis_mismatch"
    MISSING_IN_CALCULATED = "missing_in_calculated"
    MISSING_IN_ACTUAL = "missing_in_actual"
    CURRENCY_MISMATCH = "currency_mismatch"


@dataclass
class PositionDiscrepancy:
    """
    Represents a discrepancy between calculated and actual position.

    Attributes:
        symbol: Security symbol
        security_name: Security name
        discrepancy_type: Type of mismatch
        calculated_value: Value from calculated portfolio
        actual_value: Value from broker statement
        difference: Absolute difference
        difference_pct: Percentage difference
        severity: 'critical', 'high', 'medium', 'low'
        details: Additional context about the discrepancy
    """
    symbol: str
    security_name: str
    discrepancy_type: DiscrepancyType
    calculated_value: Optional[float]
    actual_value: Optional[float]
    difference: Optional[float]
    difference_pct: Optional[float]
    severity: str
    details: str = ""


@dataclass
class ValidationResult:
    """
    Complete validation results comparing calculated vs actual portfolio.

    Attributes:
        total_positions_calculated: Count of calculated positions
        total_positions_actual: Count of actual broker positions
        matched_positions: Count of positions that match
        discrepancies: List of all discrepancies found
        passed: Whether validation passed (all within tolerance)
        summary: Human-readable summary message
    """
    total_positions_calculated: int
    total_positions_actual: int
    matched_positions: int
    discrepancies: List[PositionDiscrepancy] = field(default_factory=list)
    passed: bool = True
    summary: str = ""

    @property
    def critical_discrepancies(self) -> List[PositionDiscrepancy]:
        """Get only critical severity discrepancies."""
        return [d for d in self.discrepancies if d.severity == 'critical']

    @property
    def has_critical_issues(self) -> bool:
        """Check if there are any critical issues."""
        return len(self.critical_discrepancies) > 0

    def to_dict(self) -> dict:
        """Convert to dictionary for display/export."""
        return {
            'total_positions_calculated': self.total_positions_calculated,
            'total_positions_actual': self.total_positions_actual,
            'matched_positions': self.matched_positions,
            'discrepancy_count': len(self.discrepancies),
            'critical_count': len(self.critical_discrepancies),
            'passed': self.passed,
            'summary': self.summary,
            'discrepancies': [
                {
                    'symbol': d.symbol,
                    'security_name': d.security_name,
                    'type': d.discrepancy_type.value,
                    'calculated': d.calculated_value,
                    'actual': d.actual_value,
                    'difference': d.difference,
                    'difference_pct': d.difference_pct,
                    'severity': d.severity,
                    'details': d.details
                }
                for d in self.discrepancies
            ]
        }


class PortfolioValidator:
    """
    Validates calculated portfolio against actual broker positions.

    Performs:
    - Position matching by symbol
    - Quantity validation with rounding tolerance
    - Cost basis comparison
    - Missing position detection
    - Detailed discrepancy reporting
    """

    def __init__(
        self,
        quantity_tolerance: float = 0.01,
        cost_basis_tolerance_abs: float = 1.0,
        cost_basis_tolerance_pct: float = 0.1
    ):
        """
        Initialize validator with tolerance settings.

        Args:
            quantity_tolerance: Maximum allowed difference in shares (default 0.01)
            cost_basis_tolerance_abs: Maximum absolute difference in cost basis (default ₪1)
            cost_basis_tolerance_pct: Maximum percentage difference in cost basis (default 0.1%)
        """
        self.quantity_tolerance = quantity_tolerance
        self.cost_basis_tolerance_abs = cost_basis_tolerance_abs
        self.cost_basis_tolerance_pct = cost_basis_tolerance_pct

    def validate(
        self,
        calculated_positions: List[Position],
        actual_portfolio_path: str
    ) -> ValidationResult:
        """
        Validate calculated positions against actual broker data.

        Args:
            calculated_positions: List of positions calculated from transactions
            actual_portfolio_path: Path to IBI actual portfolio Excel file

        Returns:
            ValidationResult with complete comparison details
        """
        # Load actual positions from broker file
        actual_positions = self._load_actual_positions(actual_portfolio_path)

        # Create lookup dictionaries by symbol
        calc_by_symbol = {p.security_symbol: p for p in calculated_positions}
        actual_by_symbol = {p['symbol_clean']: p for p in actual_positions}

        # Track results
        discrepancies = []
        matched_count = 0

        # 1. Check all calculated positions against actual
        for symbol, calc_pos in calc_by_symbol.items():
            if symbol in actual_by_symbol:
                # Position exists in both - compare values
                actual_pos = actual_by_symbol[symbol]
                position_discrepancies = self._compare_position(calc_pos, actual_pos)

                if position_discrepancies:
                    discrepancies.extend(position_discrepancies)
                else:
                    matched_count += 1
            else:
                # Position in calculated but not in actual
                discrepancies.append(PositionDiscrepancy(
                    symbol=symbol,
                    security_name=calc_pos.security_name,
                    discrepancy_type=DiscrepancyType.MISSING_IN_ACTUAL,
                    calculated_value=calc_pos.quantity,
                    actual_value=None,
                    difference=calc_pos.quantity,
                    difference_pct=None,
                    severity='high',
                    details=f"Position exists in calculated portfolio ({calc_pos.quantity:.2f} shares) but not found in broker statement"
                ))

        # 2. Check for positions in actual but not calculated
        for symbol, actual_pos in actual_by_symbol.items():
            if symbol not in calc_by_symbol:
                discrepancies.append(PositionDiscrepancy(
                    symbol=symbol,
                    security_name=actual_pos['security_name'],
                    discrepancy_type=DiscrepancyType.MISSING_IN_CALCULATED,
                    calculated_value=None,
                    actual_value=actual_pos['quantity'],
                    difference=actual_pos['quantity'],
                    difference_pct=None,
                    severity='high',
                    details=f"Position exists in broker statement ({actual_pos['quantity']:.2f} shares) but not in calculated portfolio"
                ))

        # Build result
        passed = len(discrepancies) == 0 or all(d.severity in ['low', 'medium'] for d in discrepancies)

        result = ValidationResult(
            total_positions_calculated=len(calculated_positions),
            total_positions_actual=len(actual_positions),
            matched_positions=matched_count,
            discrepancies=discrepancies,
            passed=passed
        )

        # Generate summary
        result.summary = self._generate_summary(result)

        return result

    def _load_actual_positions(self, file_path: str) -> List[Dict]:
        """
        Load actual positions from IBI broker file.

        Args:
            file_path: Path to IBI current portfolio Excel file

        Returns:
            List of position dictionaries
        """
        adapter = ActualPortfolioAdapter(file_path=file_path)
        positions = adapter.load_positions()
        return positions

    def _compare_position(
        self,
        calculated: Position,
        actual: Dict
    ) -> List[PositionDiscrepancy]:
        """
        Compare calculated position against actual broker data.

        Args:
            calculated: Calculated position from transactions
            actual: Actual position from broker (dict)

        Returns:
            List of discrepancies found (empty if all matches)
        """
        discrepancies = []
        symbol = calculated.security_symbol
        name = calculated.security_name

        # 1. Compare quantities
        calc_qty = calculated.quantity
        actual_qty = actual['quantity']
        qty_diff = abs(calc_qty - actual_qty)

        if qty_diff > self.quantity_tolerance:
            qty_diff_pct = (qty_diff / actual_qty * 100) if actual_qty != 0 else None

            # Determine severity based on difference
            if qty_diff > 10:
                severity = 'critical'
            elif qty_diff > 1:
                severity = 'high'
            elif qty_diff > 0.1:
                severity = 'medium'
            else:
                severity = 'low'

            discrepancies.append(PositionDiscrepancy(
                symbol=symbol,
                security_name=name,
                discrepancy_type=DiscrepancyType.QUANTITY_MISMATCH,
                calculated_value=calc_qty,
                actual_value=actual_qty,
                difference=qty_diff,
                difference_pct=qty_diff_pct,
                severity=severity,
                details=f"Quantity mismatch: calculated {calc_qty:.2f}, actual {actual_qty:.2f}, diff {qty_diff:.2f} shares"
            ))

        # 2. Compare cost basis
        calc_cost = calculated.total_invested
        actual_cost = actual.get('cost_basis', 0)
        cost_diff = abs(calc_cost - actual_cost)
        cost_diff_pct = (cost_diff / actual_cost * 100) if actual_cost != 0 else None

        # Check both absolute and percentage tolerance
        cost_exceeds_abs = cost_diff > self.cost_basis_tolerance_abs
        cost_exceeds_pct = cost_diff_pct is not None and cost_diff_pct > self.cost_basis_tolerance_pct

        if cost_exceeds_abs and cost_exceeds_pct:
            # Determine severity
            if cost_diff > 1000 or (cost_diff_pct and cost_diff_pct > 10):
                severity = 'critical'
            elif cost_diff > 100 or (cost_diff_pct and cost_diff_pct > 5):
                severity = 'high'
            elif cost_diff > 10 or (cost_diff_pct and cost_diff_pct > 1):
                severity = 'medium'
            else:
                severity = 'low'

            currency = calculated.currency
            discrepancies.append(PositionDiscrepancy(
                symbol=symbol,
                security_name=name,
                discrepancy_type=DiscrepancyType.COST_BASIS_MISMATCH,
                calculated_value=calc_cost,
                actual_value=actual_cost,
                difference=cost_diff,
                difference_pct=cost_diff_pct,
                severity=severity,
                details=f"Cost basis mismatch: calculated {currency}{calc_cost:,.2f}, actual {currency}{actual_cost:,.2f}, diff {currency}{cost_diff:,.2f}"
            ))

        # 3. Compare currency (should always match)
        calc_currency = calculated.currency
        actual_currency = actual.get('currency', '₪')

        if calc_currency != actual_currency:
            discrepancies.append(PositionDiscrepancy(
                symbol=symbol,
                security_name=name,
                discrepancy_type=DiscrepancyType.CURRENCY_MISMATCH,
                calculated_value=None,
                actual_value=None,
                difference=None,
                difference_pct=None,
                severity='high',
                details=f"Currency mismatch: calculated {calc_currency}, actual {actual_currency}"
            ))

        return discrepancies

    def _generate_summary(self, result: ValidationResult) -> str:
        """
        Generate human-readable summary of validation results.

        Args:
            result: ValidationResult object

        Returns:
            Summary message string
        """
        if result.passed and len(result.discrepancies) == 0:
            return (f"✅ Validation PASSED: All {result.matched_positions} positions match perfectly. "
                   f"Calculated portfolio is accurate!")

        if result.passed:
            return (f"✅ Validation PASSED with minor issues: {result.matched_positions} positions matched, "
                   f"{len(result.discrepancies)} minor discrepancies (within acceptable tolerance).")

        critical_count = len(result.critical_discrepancies)
        if critical_count > 0:
            return (f"❌ Validation FAILED: {critical_count} critical issues found. "
                   f"{result.matched_positions}/{result.total_positions_actual} positions matched. "
                   f"Review discrepancies for details.")

        return (f"⚠️ Validation WARNING: {result.matched_positions}/{result.total_positions_actual} positions matched, "
               f"{len(result.discrepancies)} issues found (no critical). Review recommended.")

    def generate_report(self, result: ValidationResult) -> str:
        """
        Generate detailed text report of validation results.

        Args:
            result: ValidationResult object

        Returns:
            Formatted text report
        """
        lines = []
        lines.append("=" * 80)
        lines.append("PORTFOLIO VALIDATION REPORT")
        lines.append("=" * 80)
        lines.append("")

        # Summary section
        lines.append("SUMMARY")
        lines.append("-" * 80)
        lines.append(f"Status: {'✅ PASSED' if result.passed else '❌ FAILED'}")
        lines.append(f"Total Calculated Positions: {result.total_positions_calculated}")
        lines.append(f"Total Actual Positions: {result.total_positions_actual}")
        lines.append(f"Matched Positions: {result.matched_positions}")
        lines.append(f"Discrepancies Found: {len(result.discrepancies)}")
        lines.append(f"  - Critical: {len([d for d in result.discrepancies if d.severity == 'critical'])}")
        lines.append(f"  - High: {len([d for d in result.discrepancies if d.severity == 'high'])}")
        lines.append(f"  - Medium: {len([d for d in result.discrepancies if d.severity == 'medium'])}")
        lines.append(f"  - Low: {len([d for d in result.discrepancies if d.severity == 'low'])}")
        lines.append("")
        lines.append(result.summary)
        lines.append("")

        # Discrepancies section
        if result.discrepancies:
            lines.append("DISCREPANCIES")
            lines.append("-" * 80)

            # Group by severity
            for severity in ['critical', 'high', 'medium', 'low']:
                severity_discreps = [d for d in result.discrepancies if d.severity == severity]
                if severity_discreps:
                    lines.append("")
                    lines.append(f"{severity.upper()} ({len(severity_discreps)}):")
                    lines.append("")

                    for d in severity_discreps:
                        lines.append(f"  [{d.discrepancy_type.value}] {d.security_name} ({d.symbol})")
                        lines.append(f"    {d.details}")
                        lines.append("")
        else:
            lines.append("No discrepancies found. All positions match perfectly!")

        lines.append("=" * 80)

        return "\n".join(lines)

    def export_discrepancies_csv(self, result: ValidationResult, output_path: str):
        """
        Export discrepancies to CSV file for further analysis.

        Args:
            result: ValidationResult object
            output_path: Path to save CSV file
        """
        if not result.discrepancies:
            # Create empty CSV with headers
            df = pd.DataFrame(columns=[
                'symbol', 'security_name', 'type', 'calculated', 'actual',
                'difference', 'difference_pct', 'severity', 'details'
            ])
        else:
            data = []
            for d in result.discrepancies:
                data.append({
                    'symbol': d.symbol,
                    'security_name': d.security_name,
                    'type': d.discrepancy_type.value,
                    'calculated': d.calculated_value,
                    'actual': d.actual_value,
                    'difference': d.difference,
                    'difference_pct': d.difference_pct,
                    'severity': d.severity,
                    'details': d.details
                })
            df = pd.DataFrame(data)

        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        return output_path
