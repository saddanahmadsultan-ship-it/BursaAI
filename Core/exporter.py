"""
====================================================
BursaAI Professional Excel Export Engine
Version : 5.3 Batch 5A Institutional AI Brain
====================================================
"""

import os

from openpyxl import Workbook
from openpyxl.styles import (
    Font,
    PatternFill,
    Alignment,
    Border,
    Side
)
from openpyxl.utils import get_column_letter

from Core.config import (
    EXPORT_FILE,
    MAX_EXCEL_COLUMN_WIDTH
)


# ==================================================
# COLOURS
# ==================================================

DARK_BLUE_FILL = PatternFill(
    start_color="1F4E78",
    end_color="1F4E78",
    fill_type="solid"
)

BLUE_FILL = PatternFill(
    start_color="D9EAF7",
    end_color="D9EAF7",
    fill_type="solid"
)

GREEN_FILL = PatternFill(
    start_color="C6EFCE",
    end_color="C6EFCE",
    fill_type="solid"
)

YELLOW_FILL = PatternFill(
    start_color="FFF2CC",
    end_color="FFF2CC",
    fill_type="solid"
)

ORANGE_FILL = PatternFill(
    start_color="FCE4D6",
    end_color="FCE4D6",
    fill_type="solid"
)

RED_FILL = PatternFill(
    start_color="F4CCCC",
    end_color="F4CCCC",
    fill_type="solid"
)

GREY_FILL = PatternFill(
    start_color="E7E6E6",
    end_color="E7E6E6",
    fill_type="solid"
)

WHITE_FONT = Font(
    color="FFFFFF",
    bold=True
)

BOLD_FONT = Font(
    bold=True
)

CENTER = Alignment(
    horizontal="center",
    vertical="center"
)

LEFT = Alignment(
    horizontal="left",
    vertical="center"
)

THIN_SIDE = Side(
    style="thin",
    color="B7B7B7"
)

THIN_BORDER = Border(
    left=THIN_SIDE,
    right=THIN_SIDE,
    top=THIN_SIDE,
    bottom=THIN_SIDE
)


# ==================================================
# SAFE HELPERS
# ==================================================

def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _safe_text(value, default=""):
    if value is None:
        return default

    return str(value)


def _get_nested(item, section, key, fallback=None):
    section_data = item.get(section, {})

    if isinstance(section_data, dict):
        value = section_data.get(key)

        if value is not None:
            return value

    return fallback


def _style_header(ws, row=1):
    for cell in ws[row]:
        cell.fill = DARK_BLUE_FILL
        cell.font = WHITE_FONT
        cell.alignment = CENTER
        cell.border = THIN_BORDER


def _style_data_area(ws):
    for row in ws.iter_rows(
        min_row=2,
        max_row=ws.max_row,
        min_col=1,
        max_col=ws.max_column
    ):
        for cell in row:
            cell.border = THIN_BORDER
            cell.alignment = CENTER


def _auto_width(ws):
    for column_cells in ws.columns:
        max_length = 0

        column_letter = get_column_letter(
            column_cells[0].column
        )

        for cell in column_cells:
            value = cell.value

            if value is None:
                length = 0
            else:
                length = len(str(value))

            if length > max_length:
                max_length = length

        ws.column_dimensions[column_letter].width = min(
            max_length + 3,
            MAX_EXCEL_COLUMN_WIDTH
        )


def _apply_number_formats(ws, formats):
    for column_number, number_format in formats.items():
        for row in range(2, ws.max_row + 1):
            ws.cell(
                row=row,
                column=column_number
            ).number_format = number_format


def _colour_signal(cell, signal):
    signal = _safe_text(signal).upper()

    if signal in ("STRONG BUY", "BUY"):
        cell.fill = GREEN_FILL

    elif signal == "WATCH":
        cell.fill = YELLOW_FILL

    elif signal == "HOLD":
        cell.fill = ORANGE_FILL

    else:
        cell.fill = RED_FILL


def _colour_grade(cell, grade):
    grade = _safe_text(grade).upper()

    if grade in ("A+", "A"):
        cell.fill = GREEN_FILL

    elif grade in ("B+", "B"):
        cell.fill = YELLOW_FILL

    elif grade == "C":
        cell.fill = ORANGE_FILL

    else:
        cell.fill = RED_FILL


def _colour_position_status(cell, status):
    status = _safe_text(status).upper()

    if status == "READY":
        cell.fill = GREEN_FILL

    elif "WATCH" in status:
        cell.fill = YELLOW_FILL

    elif "HOLD" in status:
        cell.fill = ORANGE_FILL

    elif "SKIP" in status:
        cell.fill = RED_FILL

    else:
        cell.fill = GREY_FILL


# ==================================================
# DASHBOARD SHEET
# ==================================================

def _create_dashboard_sheet(wb, results, portfolio_summary=None):
    if portfolio_summary is None:
        portfolio_summary = {}

    ws = wb.active
    ws.title = "Dashboard"

    total_stocks = len(results)

    tradeable = [
        item for item in results
        if _safe_text(
            _get_nested(
                item,
                "trade",
                "signal",
                item.get("Signal", "AVOID")
            )
        ).upper() != "AVOID"
    ]

    total_capital_used = sum(
        _safe_float(
            _get_nested(
                item,
                "position",
                "capital_used",
                item.get("CapitalUsed", 0)
            )
        )
        for item in results
    )

    total_max_loss = sum(
        _safe_float(
            _get_nested(
                item,
                "position",
                "max_loss",
                item.get("MaxLoss", 0)
            )
        )
        for item in results
    )

    total_potential_profit = sum(
        _safe_float(
            _get_nested(
                item,
                "position",
                "potential_profit",
                item.get("PotentialProfit", 0)
            )
        )
        for item in results
    )

    account_capital = 0.0

    if results:
        account_capital = _safe_float(
            _get_nested(
                results[0],
                "position",
                "account_capital",
                results[0].get(
                    "AccountCapital",
                    0
                )
            )
        )

    account_capital = _safe_float(
        portfolio_summary.get("account_capital", account_capital)
    )
    total_capital_used = _safe_float(
        portfolio_summary.get("capital_allocated", total_capital_used)
    )
    total_max_loss = _safe_float(
        portfolio_summary.get("portfolio_risk_amount", total_max_loss)
    )

    ws.merge_cells("A1:F2")
    ws["A1"] = "BursaAI Professional Dashboard v5.0"
    ws["A1"].font = Font(
        bold=True,
        size=18,
        color="FFFFFF"
    )
    ws["A1"].fill = DARK_BLUE_FILL
    ws["A1"].alignment = CENTER

    summary = [
        ("Total Saham", total_stocks),
        ("Saham Tradeable", len(tradeable)),
        ("Account Capital", account_capital),
        ("Total Capital Used", total_capital_used),
        ("Total Maximum Loss", total_max_loss),
        ("Total Potential Profit", total_potential_profit)
    ]

    start_row = 4

    for index, (label, value) in enumerate(
        summary,
        start=start_row
    ):
        ws.cell(
            row=index,
            column=1,
            value=label
        )

        ws.cell(
            row=index,
            column=2,
            value=value
        )

        ws.cell(
            row=index,
            column=1
        ).font = BOLD_FONT

        ws.cell(
            row=index,
            column=1
        ).fill = BLUE_FILL

        ws.cell(
            row=index,
            column=1
        ).border = THIN_BORDER

        ws.cell(
            row=index,
            column=2
        ).border = THIN_BORDER

    for row in range(start_row + 2, start_row + 6):
        ws.cell(
            row=row,
            column=2
        ).number_format = 'RM #,##0.00'

    top_headers = [
        "Rank",
        "Code",
        "Final Score",
        "Signal",
        "Market",
        "Lots",
        "Capital Used",
        "Max Loss",
        "Potential Profit",
        "Position Status"
    ]

    top_start_row = 12

    for column, header in enumerate(
        top_headers,
        start=1
    ):
        ws.cell(
            row=top_start_row,
            column=column,
            value=header
        )

    _style_header(
        ws,
        top_start_row
    )

    top_results = results[:5]

    for row_number, item in enumerate(
        top_results,
        start=top_start_row + 1
    ):
        identity = item.get("identity", {})
        score = item.get("score", {})
        trade = item.get("trade", {})
        market = item.get("market", {})
        position = item.get("position", {})

        values = [
            row_number - top_start_row,
            identity.get(
                "code",
                item.get("Code", "")
            ),
            score.get(
                "final",
                item.get("FinalScore", 0)
            ),
            trade.get(
                "signal",
                item.get("Signal", "AVOID")
            ),
            market.get(
                "regime",
                item.get(
                    "MarketRegime",
                    "UNKNOWN"
                )
            ),
            position.get(
                "lots",
                item.get("Lots", 0)
            ),
            position.get(
                "capital_used",
                item.get("CapitalUsed", 0)
            ),
            position.get(
                "max_loss",
                item.get("MaxLoss", 0)
            ),
            position.get(
                "potential_profit",
                item.get(
                    "PotentialProfit",
                    0
                )
            ),
            position.get(
                "status",
                item.get(
                    "PositionStatus",
                    "UNKNOWN"
                )
            )
        ]

        for column, value in enumerate(
            values,
            start=1
        ):
            ws.cell(
                row=row_number,
                column=column,
                value=value
            )

            ws.cell(
                row=row_number,
                column=column
            ).border = THIN_BORDER

            ws.cell(
                row=row_number,
                column=column
            ).alignment = CENTER

        _colour_signal(
            ws.cell(
                row=row_number,
                column=4
            ),
            values[3]
        )

        _colour_position_status(
            ws.cell(
                row=row_number,
                column=10
            ),
            values[9]
        )

    for row in range(
        top_start_row + 1,
        ws.max_row + 1
    ):
        for column in (7, 8, 9):
            ws.cell(
                row=row,
                column=column
            ).number_format = 'RM #,##0.00'

    ws.freeze_panes = "A12"
    ws.auto_filter.ref = (
        f"A{top_start_row}:"
        f"J{ws.max_row}"
    )

    _auto_width(ws)


# ==================================================
# RANKING SHEET
# ==================================================

def _create_ranking_sheet(wb, results):
    ws = wb.create_sheet("Ranking")

    headers = [
        "Rank",
        "Code",
        "Price",
        "Raw Score",
        "Quality Penalty",
        "Tradeable Score",
        "Institution Bonus",
        "Regime Score",
        "Regime Bonus",
        "Regime Penalty",
        "Final Score",
        "Grade",
        "Confidence",
        "Confidence Level",
        "Trend",
        "Volume",
        "Smart Money",
        "Market Regime",
        "Signal",
        "AI Rating"
    ]

    ws.append(headers)

    for rank, item in enumerate(
        results,
        start=1
    ):
        identity = item.get("identity", {})
        score = item.get("score", {})
        confidence = item.get(
            "confidence",
            {}
        )
        market = item.get("market", {})
        trade = item.get("trade", {})

        row = [
            rank,
            identity.get(
                "code",
                item.get("Code", "")
            ),
            identity.get(
                "price",
                item.get("Price", 0)
            ),
            score.get(
                "raw",
                item.get("RawScore", 0)
            ),
            score.get(
                "quality_penalty",
                item.get(
                    "QualityPenalty",
                    0
                )
            ),
            score.get(
                "tradeable",
                item.get(
                    "TradeableScore",
                    0
                )
            ),
            score.get(
                "institution_bonus",
                item.get(
                    "InstitutionBonus",
                    0
                )
            ),
            market.get(
                "regime_score",
                item.get("RegimeScore", 0)
            ),
            score.get(
                "regime_bonus",
                item.get("RegimeBonus", 0)
            ),
            score.get(
                "regime_penalty",
                item.get(
                    "RegimePenalty",
                    0
                )
            ),
            score.get(
                "final",
                item.get("FinalScore", 0)
            ),
            score.get(
                "grade",
                item.get("Grade", "D")
            ),
            confidence.get(
                "value",
                item.get("Confidence", 0)
            ),
            confidence.get(
                "level",
                item.get(
                    "ConfLevel",
                    "UNKNOWN"
                )
            ),
            market.get(
                "trend",
                item.get("Trend", "UNKNOWN")
            ),
            market.get(
                "volume",
                item.get(
                    "Volume",
                    "UNKNOWN"
                )
            ),
            market.get(
                "smart_money",
                item.get(
                    "SmartMoney",
                    "NONE"
                )
            ),
            market.get(
                "regime",
                item.get(
                    "MarketRegime",
                    "UNKNOWN"
                )
            ),
            trade.get(
                "signal",
                item.get("Signal", "AVOID")
            ),
            trade.get(
                "rating",
                item.get("Rating", "UNKNOWN")
            )
        ]

        ws.append(row)

    _style_header(ws)
    _style_data_area(ws)

    for row in range(2, ws.max_row + 1):
        _colour_grade(
            ws.cell(row=row, column=12),
            ws.cell(row=row, column=12).value
        )

        _colour_signal(
            ws.cell(row=row, column=19),
            ws.cell(row=row, column=19).value
        )

    _apply_number_formats(
        ws,
        {
            3: 'RM #,##0.00',
            13: '0.00'
        }
    )

    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions

    _auto_width(ws)


# ==================================================
# POSITION PLAN SHEET
# ==================================================

def _create_position_sheet(wb, results):
    ws = wb.create_sheet("Position Plan")

    headers = [
        "Rank",
        "Code",
        "Signal",
        "Position Status",
        "Position Rating",
        "Entry",
        "Stop Loss",
        "Target",
        "RR",
        "Account Capital",
        "Risk Percent",
        "Risk Capital",
        "Risk Per Share",
        "Shares",
        "Lots",
        "Capital Used",
        "Remaining Capital",
        "Allocation %",
        "Actual Risk %",
        "Maximum Loss",
        "Potential Profit"
    ]

    ws.append(headers)

    for rank, item in enumerate(
        results,
        start=1
    ):
        identity = item.get("identity", {})
        trade = item.get("trade", {})
        position = item.get("position", {})

        row = [
            rank,
            identity.get(
                "code",
                item.get("Code", "")
            ),
            trade.get(
                "signal",
                item.get("Signal", "AVOID")
            ),
            position.get(
                "status",
                item.get(
                    "PositionStatus",
                    "UNKNOWN"
                )
            ),
            position.get(
                "rating",
                item.get(
                    "PositionRating",
                    "NONE"
                )
            ),
            trade.get(
                "entry",
                item.get("Entry", 0)
            ),
            trade.get(
                "stop_loss",
                item.get("StopLoss", 0)
            ),
            trade.get(
                "target",
                item.get("Target", 0)
            ),
            trade.get(
                "risk_reward",
                item.get("RR", 0)
            ),
            position.get(
                "account_capital",
                item.get("AccountCapital", 0)
            ),
            position.get(
                "risk_percent",
                item.get("RiskPercent", 0)
            ),
            position.get(
                "risk_capital",
                item.get("RiskCapital", 0)
            ),
            position.get(
                "risk_per_share",
                item.get("RiskPerShare", 0)
            ),
            position.get(
                "shares",
                item.get("Shares", 0)
            ),
            position.get(
                "lots",
                item.get("Lots", 0)
            ),
            position.get(
                "capital_used",
                item.get("CapitalUsed", 0)
            ),
            position.get(
                "remaining_capital",
                item.get(
                    "RemainingCapital",
                    0
                )
            ),
            position.get(
                "allocation_percent",
                item.get("Allocation", 0)
            ),
            position.get(
                "actual_risk_percent",
                item.get(
                    "ActualRiskPercent",
                    0
                )
            ),
            position.get(
                "max_loss",
                item.get("MaxLoss", 0)
            ),
            position.get(
                "potential_profit",
                item.get(
                    "PotentialProfit",
                    0
                )
            )
        ]

        ws.append(row)

    _style_header(ws)
    _style_data_area(ws)

    for row in range(2, ws.max_row + 1):
        _colour_signal(
            ws.cell(row=row, column=3),
            ws.cell(row=row, column=3).value
        )

        _colour_position_status(
            ws.cell(row=row, column=4),
            ws.cell(row=row, column=4).value
        )

    _apply_number_formats(
        ws,
        {
            6: 'RM #,##0.00',
            7: 'RM #,##0.00',
            8: 'RM #,##0.00',
            9: '0.00',
            10: 'RM #,##0.00',
            11: '0.00%',
            12: 'RM #,##0.00',
            13: 'RM #,##0.00',
            16: 'RM #,##0.00',
            17: 'RM #,##0.00',
            18: '0.00%',
            19: '0.00%',
            20: 'RM #,##0.00',
            21: 'RM #,##0.00'
        }
    )

    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions

    _auto_width(ws)


# ==================================================
# RISK SUMMARY SHEET
# ==================================================

def _create_risk_summary_sheet(wb, results):
    ws = wb.create_sheet("Risk Summary")

    headers = [
        "Code",
        "Signal",
        "Market Regime",
        "Final Score",
        "Confidence",
        "RR",
        "Capital Used",
        "Allocation %",
        "Actual Risk %",
        "Maximum Loss",
        "Potential Profit",
        "Risk Profit Ratio",
        "Position Status"
    ]

    ws.append(headers)

    for item in results:
        identity = item.get("identity", {})
        score = item.get("score", {})
        confidence = item.get(
            "confidence",
            {}
        )
        market = item.get("market", {})
        trade = item.get("trade", {})
        position = item.get("position", {})

        max_loss = _safe_float(
            position.get(
                "max_loss",
                item.get("MaxLoss", 0)
            )
        )

        potential_profit = _safe_float(
            position.get(
                "potential_profit",
                item.get(
                    "PotentialProfit",
                    0
                )
            )
        )

        if max_loss > 0:
            risk_profit_ratio = (
                potential_profit /
                max_loss
            )
        else:
            risk_profit_ratio = 0

        row = [
            identity.get(
                "code",
                item.get("Code", "")
            ),
            trade.get(
                "signal",
                item.get("Signal", "AVOID")
            ),
            market.get(
                "regime",
                item.get(
                    "MarketRegime",
                    "UNKNOWN"
                )
            ),
            score.get(
                "final",
                item.get("FinalScore", 0)
            ),
            confidence.get(
                "value",
                item.get("Confidence", 0)
            ),
            trade.get(
                "risk_reward",
                item.get("RR", 0)
            ),
            position.get(
                "capital_used",
                item.get("CapitalUsed", 0)
            ),
            position.get(
                "allocation_percent",
                item.get("Allocation", 0)
            ),
            position.get(
                "actual_risk_percent",
                item.get(
                    "ActualRiskPercent",
                    0
                )
            ),
            max_loss,
            potential_profit,
            round(risk_profit_ratio, 2),
            position.get(
                "status",
                item.get(
                    "PositionStatus",
                    "UNKNOWN"
                )
            )
        ]

        ws.append(row)

    _style_header(ws)
    _style_data_area(ws)

    for row in range(2, ws.max_row + 1):
        _colour_signal(
            ws.cell(row=row, column=2),
            ws.cell(row=row, column=2).value
        )

        _colour_position_status(
            ws.cell(row=row, column=13),
            ws.cell(row=row, column=13).value
        )

    _apply_number_formats(
        ws,
        {
            5: '0.00',
            6: '0.00',
            7: 'RM #,##0.00',
            8: '0.00%',
            9: '0.00%',
            10: 'RM #,##0.00',
            11: 'RM #,##0.00',
            12: '0.00'
        }
    )

    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions

    _auto_width(ws)



# ==================================================
# PORTFOLIO ALLOCATION SHEET
# ==================================================

def _create_portfolio_sheet(wb, results, portfolio_summary):
    ws = wb.create_sheet("Portfolio")

    ws.merge_cells("A1:F2")
    ws["A1"] = "BursaAI Portfolio Allocation Summary"
    ws["A1"].font = Font(bold=True, size=16, color="FFFFFF")
    ws["A1"].fill = DARK_BLUE_FILL
    ws["A1"].alignment = CENTER

    summary_rows = [
        ("Account Capital", portfolio_summary.get("account_capital", 0)),
        ("Deployable Capital", portfolio_summary.get("deployable_capital", 0)),
        ("Cash Reserve", portfolio_summary.get("cash_reserve", 0)),
        ("Capital Allocated", portfolio_summary.get("capital_allocated", 0)),
        ("Remaining Cash", portfolio_summary.get("remaining_cash", 0)),
        ("Portfolio Risk Amount", portfolio_summary.get("portfolio_risk_amount", 0)),
        ("Portfolio Risk %", portfolio_summary.get("portfolio_risk_pct", 0)),
        ("Maximum Portfolio Risk %", portfolio_summary.get("maximum_portfolio_risk_pct", 0)),
        ("Active Positions", portfolio_summary.get("active_positions", 0)),
        ("Maximum Active Positions", portfolio_summary.get("maximum_active_positions", 0)),
        ("Exposure %", portfolio_summary.get("exposure_pct", 0)),
        ("Cash %", portfolio_summary.get("cash_pct", 0)),
        ("Average Final Score", portfolio_summary.get("average_final_score", 0)),
        ("Average Confidence", portfolio_summary.get("average_confidence", 0)),
        ("Portfolio Status", portfolio_summary.get("status", "UNKNOWN")),
    ]

    for row_number, (label, value) in enumerate(summary_rows, start=4):
        ws.cell(row=row_number, column=1, value=label)
        ws.cell(row=row_number, column=2, value=value)
        ws.cell(row=row_number, column=1).font = BOLD_FONT
        ws.cell(row=row_number, column=1).fill = BLUE_FILL
        ws.cell(row=row_number, column=1).border = THIN_BORDER
        ws.cell(row=row_number, column=2).border = THIN_BORDER

        if label in {
            "Account Capital", "Deployable Capital", "Cash Reserve",
            "Capital Allocated", "Remaining Cash", "Portfolio Risk Amount"
        }:
            ws.cell(row=row_number, column=2).number_format = 'RM #,##0.00'
        elif "%" in label or label == "Average Confidence":
            ws.cell(row=row_number, column=2).number_format = '0.00"%"'

    header_row = 21
    headers = [
        "Portfolio Rank", "Code", "Final Score", "Confidence", "Signal",
        "Market Regime", "Suggested Shares", "Suggested Lots",
        "Suggested Capital", "Suggested Max Loss", "Allocated Shares",
        "Allocated Lots", "Allocated Capital", "Allocated Max Loss",
        "Potential Profit", "Allocation %", "Portfolio Risk %",
        "Cash After", "Portfolio Status", "Reason"
    ]

    for column, header in enumerate(headers, start=1):
        ws.cell(row=header_row, column=column, value=header)

    _style_header(ws, header_row)

    for row_number, item in enumerate(results, start=header_row + 1):
        identity = item.get("identity", {})
        score = item.get("score", {})
        confidence = item.get("confidence", {})
        trade = item.get("trade", {})
        market = item.get("market", {})
        portfolio = item.get("portfolio", {})

        row = [
            portfolio.get("rank"),
            identity.get("code", item.get("Code", "")),
            score.get("final", item.get("FinalScore", 0)),
            confidence.get("value", item.get("Confidence", 0)),
            trade.get("signal", item.get("Signal", "UNKNOWN")),
            market.get("regime", item.get("MarketRegime", "UNKNOWN")),
            portfolio.get("suggested_shares", 0),
            portfolio.get("suggested_lots", 0),
            portfolio.get("suggested_capital", 0),
            portfolio.get("suggested_max_loss", 0),
            portfolio.get("allocated_shares", 0),
            portfolio.get("allocated_lots", 0),
            portfolio.get("allocated_capital", 0),
            portfolio.get("allocated_max_loss", 0),
            portfolio.get("allocated_potential_profit", 0),
            portfolio.get("allocation_percent", 0),
            portfolio.get("risk_percent", 0),
            portfolio.get("remaining_cash_after", 0),
            portfolio.get("status", "SKIP"),
            portfolio.get("reason", ""),
        ]

        for column, value in enumerate(row, start=1):
            cell = ws.cell(row=row_number, column=column, value=value)
            cell.border = THIN_BORDER
            cell.alignment = CENTER

        _colour_signal(ws.cell(row=row_number, column=5), row[4])

        status_cell = ws.cell(row=row_number, column=19)
        status = _safe_text(row[18]).upper()
        if status == "ALLOCATED":
            status_cell.fill = GREEN_FILL
        elif status == "REDUCED":
            status_cell.fill = YELLOW_FILL
        elif status == "NO CAPITAL":
            status_cell.fill = ORANGE_FILL
        else:
            status_cell.fill = RED_FILL

    for row_number in range(header_row + 1, ws.max_row + 1):
        for column in (9, 10, 13, 14, 15, 18):
            ws.cell(row=row_number, column=column).number_format = 'RM #,##0.00'
        for column in (16, 17):
            ws.cell(row=row_number, column=column).number_format = '0.00"%"'

    ws.freeze_panes = f"A{header_row + 1}"
    ws.auto_filter.ref = f"A{header_row}:T{ws.max_row}"
    _auto_width(ws)




# ==================================================
# ENTRY TIMING SHEET
# ==================================================

def _create_entry_timing_sheet(wb, results):
    ws = wb.create_sheet("Entry Timing")

    headers = [
        "Rank",
        "Code",
        "Signal",
        "Final Score",
        "Confidence",
        "Market Regime",
        "Timing Score",
        "Timing Status",
        "Timing Action",
        "Entry Zone Low",
        "Entry Zone High",
        "Position Status",
        "Portfolio Status",
        "Timing Reasons",
        "Timing Warnings"
    ]

    ws.append(headers)

    for rank, item in enumerate(results, start=1):
        timing = item.get("entry_timing", {})

        row = [
            rank,
            item.get("Code", ""),
            item.get("Signal", "UNKNOWN"),
            item.get("FinalScore", 0),
            item.get("Confidence", 0),
            item.get("MarketRegime", "UNKNOWN"),
            timing.get("score", item.get("EntryTimingScore", 0)),
            timing.get("status", item.get("EntryTimingStatus", "UNKNOWN")),
            timing.get("action", item.get("EntryTimingAction", "NO ACTION")),
            timing.get("entry_zone_low", item.get("EntryZoneLow", 0)),
            timing.get("entry_zone_high", item.get("EntryZoneHigh", 0)),
            item.get("PositionStatus", "UNKNOWN"),
            item.get("PortfolioStatus", "SKIP"),
            ", ".join(
                str(value)
                for value in timing.get(
                    "reasons",
                    item.get("EntryTimingReasons", [])
                )
            ),
            ", ".join(
                str(value)
                for value in timing.get(
                    "warnings",
                    item.get("EntryTimingWarnings", [])
                )
            )
        ]

        ws.append(row)

    _style_header(ws)
    _style_data_area(ws)

    for row in range(2, ws.max_row + 1):
        status = _safe_text(
            ws.cell(row=row, column=8).value
        ).upper()

        status_cell = ws.cell(row=row, column=8)

        if status == "READY":
            status_cell.fill = GREEN_FILL
        elif status == "EARLY":
            status_cell.fill = YELLOW_FILL
        elif status == "WAIT":
            status_cell.fill = ORANGE_FILL
        else:
            status_cell.fill = RED_FILL

        _colour_signal(
            ws.cell(row=row, column=3),
            ws.cell(row=row, column=3).value
        )

    _apply_number_formats(
        ws,
        {
            5: '0.00',
            7: '0.00',
            10: 'RM #,##0.00',
            11: 'RM #,##0.00'
        }
    )

    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions

    _auto_width(ws)


# ==================================================
# DYNAMIC RISK SHEET
# ==================================================

def _create_dynamic_risk_sheet(wb, results):
    ws = wb.create_sheet("Dynamic Risk")

    headers = [
        "Rank", "Code", "Signal", "Timing", "Market Regime",
        "Volatility", "Final Score", "Confidence", "RR",
        "Base Risk %", "Signal Mult", "Timing Mult", "Regime Mult",
        "Volatility Mult", "Confidence Mult", "Score Mult", "RR Mult",
        "Smart Money Mult", "Combined Mult", "Calculated Risk %",
        "Final Risk %", "Risk Status", "Risk Reason", "Position Status",
        "Portfolio Status"
    ]
    ws.append(headers)

    for rank, item in enumerate(results, start=1):
        dynamic = item.get("dynamic_risk", {})
        multipliers = dynamic.get("multipliers", {})
        row = [
            rank,
            item.get("Code", ""),
            item.get("Signal", "UNKNOWN"),
            item.get("EntryTimingStatus", "UNKNOWN"),
            item.get("MarketRegime", "UNKNOWN"),
            dynamic.get("volatility", "UNKNOWN"),
            item.get("FinalScore", 0),
            item.get("Confidence", 0),
            item.get("RR", 0),
            dynamic.get("base_risk_percent", 0),
            multipliers.get("signal", 0),
            multipliers.get("timing", 0),
            multipliers.get("regime", 0),
            multipliers.get("volatility", 0),
            multipliers.get("confidence", 0),
            multipliers.get("score", 0),
            multipliers.get("risk_reward", 0),
            multipliers.get("smart_money", 0),
            dynamic.get("combined_multiplier", 0),
            dynamic.get("calculated_risk_percent", 0),
            dynamic.get("final_risk_percent", 0),
            dynamic.get("status", "UNKNOWN"),
            dynamic.get("reason", ""),
            item.get("PositionStatus", "UNKNOWN"),
            item.get("PortfolioStatus", "SKIP"),
        ]
        ws.append(row)

    _style_header(ws)
    _style_data_area(ws)

    for row in range(2, ws.max_row + 1):
        status = _safe_text(ws.cell(row=row, column=22).value).upper()
        cell = ws.cell(row=row, column=22)
        if status == "NORMAL RISK":
            cell.fill = GREEN_FILL
        elif status == "REDUCED RISK":
            cell.fill = YELLOW_FILL
        elif status == "MINIMUM RISK":
            cell.fill = ORANGE_FILL
        else:
            cell.fill = RED_FILL

    _apply_number_formats(
        ws,
        {
            7: '0.00', 8: '0.00', 9: '0.00',
            10: '0.00"%"', 11: '0.0000', 12: '0.0000',
            13: '0.0000', 14: '0.0000', 15: '0.0000',
            16: '0.0000', 17: '0.0000', 18: '0.0000',
            19: '0.000000', 20: '0.00"%"', 21: '0.00"%"'
        }
    )

    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    _auto_width(ws)



# ==================================================
# INSTITUTIONAL AI BRAIN SHEET
# ==================================================

def _create_ai_brain_sheet(wb, results):
    ws = wb.create_sheet("AI Brain")
    headers = [
        "Rank", "Code", "Current Signal", "AI Signal",
        "AI Conviction", "Conviction Level",
        "Prediction Stability", "Execution Quality",
        "Trend", "Momentum", "Volume", "Smart Money",
        "Market Regime", "Multi Timeframe", "Entry Timing",
        "Trade Quality", "AI Summary", "Strengths", "Weaknesses"
    ]
    ws.append(headers)
    for rank, item in enumerate(results, start=1):
        brain = item.get("ai_brain", {})
        components = brain.get("components", {})
        reasoning = brain.get("reasoning", {})
        ws.append([
            rank, item.get("Code", ""), item.get("Signal", "UNKNOWN"),
            brain.get("ai_signal", "UNKNOWN"),
            brain.get("conviction_score", 0), brain.get("conviction_level", "UNKNOWN"),
            brain.get("prediction_stability", 0), brain.get("execution_quality", 0),
            components.get("trend", 0), components.get("momentum", 0),
            components.get("volume", 0), components.get("smart_money", 0),
            components.get("market_regime", 0), components.get("multi_timeframe", 0),
            components.get("entry_timing", 0), components.get("trade_quality", 0),
            reasoning.get("summary", ""),
            " | ".join(reasoning.get("strengths", [])),
            " | ".join(reasoning.get("weaknesses", [])),
        ])
    _style_header(ws)
    _style_data_area(ws)
    for row in range(2, ws.max_row + 1):
        _colour_signal(ws.cell(row=row, column=4), ws.cell(row=row, column=4).value)
        for column in range(5, 17):
            ws.cell(row=row, column=column).number_format = '0.00'
        for column in (17, 18, 19):
            ws.cell(row=row, column=column).alignment = LEFT
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    _auto_width(ws)


# ==================================================
# RAW DATA SHEET
# ==================================================

def _create_raw_data_sheet(wb, results):
    ws = wb.create_sheet("Raw Data")

    headers = [
        "Rank",
        "Code",
        "Price",
        "RawScore",
        "QualityPenalty",
        "TradeableScore",
        "InstitutionBonus",
        "RegimeScore",
        "RegimeBonus",
        "RegimePenalty",
        "FinalScore",
        "Grade",
        "Confidence",
        "ConfLevel",
        "Trend",
        "Volume",
        "SmartMoney",
        "MarketRegime",
        "Signal",
        "DecisionSignal",
        "Rating",
        "Entry",
        "StopLoss",
        "Target",
        "RR",
        "RSI",
        "AccountCapital",
        "RiskPercent",
        "RiskCapital",
        "RiskPerShare",
        "Shares",
        "Lots",
        "CapitalUsed",
        "RemainingCapital",
        "Allocation",
        "ActualRiskPercent",
        "MaxLoss",
        "PotentialProfit",
        "PositionStatus",
        "PositionRating",
        "Validation",
        "ValidationReason",
        "Summary"
    ]

    ws.append(headers)

    for rank, item in enumerate(
        results,
        start=1
    ):
        row = [
            rank,
            item.get("Code"),
            item.get("Price"),
            item.get("RawScore"),
            item.get("QualityPenalty"),
            item.get("TradeableScore"),
            item.get("InstitutionBonus"),
            item.get("RegimeScore"),
            item.get("RegimeBonus"),
            item.get("RegimePenalty"),
            item.get("FinalScore"),
            item.get("Grade"),
            item.get("Confidence"),
            item.get("ConfLevel"),
            item.get("Trend"),
            item.get("Volume"),
            item.get("SmartMoney"),
            item.get("MarketRegime"),
            item.get("Signal"),
            item.get("DecisionSignal"),
            item.get("Rating"),
            item.get("Entry"),
            item.get("StopLoss"),
            item.get("Target"),
            item.get("RR"),
            item.get("RSI"),
            item.get("AccountCapital"),
            item.get("RiskPercent"),
            item.get("RiskCapital"),
            item.get("RiskPerShare"),
            item.get("Shares"),
            item.get("Lots"),
            item.get("CapitalUsed"),
            item.get("RemainingCapital"),
            item.get("Allocation"),
            item.get("ActualRiskPercent"),
            item.get("MaxLoss"),
            item.get("PotentialProfit"),
            item.get("PositionStatus"),
            item.get("PositionRating"),
            item.get("Validation"),
            item.get("ValidationReason"),
            item.get("Summary")
        ]

        ws.append(row)

    _style_header(ws)
    _style_data_area(ws)

    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions

    _auto_width(ws)


# ==================================================
# MAIN EXPORT FUNCTION
# ==================================================

def export_excel(results, portfolio_summary=None):
    if not results:
        print("Tiada data untuk dieksport.")
        return

    if portfolio_summary is None:
        portfolio_summary = {}

    os.makedirs(
        "output",
        exist_ok=True
    )

    workbook = Workbook()

    _create_dashboard_sheet(
        workbook,
        results,
        portfolio_summary
    )

    _create_ranking_sheet(
        workbook,
        results
    )

    _create_position_sheet(
        workbook,
        results
    )

    _create_risk_summary_sheet(
        workbook,
        results
    )

    _create_portfolio_sheet(
        workbook,
        results,
        portfolio_summary
    )

    _create_entry_timing_sheet(
        workbook,
        results
    )

    _create_dynamic_risk_sheet(
        workbook,
        results
    )

    _create_ai_brain_sheet(
        workbook,
        results
    )

    _create_raw_data_sheet(
        workbook,
        results
    )

    filepath = os.path.join(
        "output",
        EXPORT_FILE
    )

    workbook.save(filepath)

    print("\n[OK] Report profesional berjaya disimpan.")
    print(f"[FILE] {filepath}")
    print(
        "[SHEETS] Dashboard, Ranking, Position Plan, "
        "Risk Summary, Portfolio, Entry Timing, Dynamic Risk, AI Brain, Raw Data"
    )