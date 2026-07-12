"""
=========================================================
BursaAI Legacy Bridge
Version : 6.0 Sprint 4A
=========================================================

Bidirectional translator:

Legacy Core dict
        ⇄
Framework AnalysisContext / AnalysisModel
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable, Optional

from Framework.context import AnalysisContext
from Framework.domain import AnalysisModel
from Framework.exceptions import ValidationError


class LegacyBridge:
    """
    Convert legacy BursaAI dictionaries to Framework models,
    and Framework models back to legacy dictionaries.
    """

    def _safe_float(
        self,
        value: Any,
        default: float = 0.0,
    ) -> float:
        try:
            if value is None:
                return default

            if isinstance(value, str):
                cleaned = (
                    value.replace("RM", "")
                    .replace("%", "")
                    .replace(",", "")
                    .strip()
                )

                if not cleaned:
                    return default

                return float(cleaned)

            return float(value)

        except (TypeError, ValueError):
            return default

    def _safe_int(
        self,
        value: Any,
        default: int = 0,
    ) -> int:
        try:
            if value is None:
                return default

            return int(float(value))

        except (TypeError, ValueError):
            return default

    def _safe_text(
        self,
        value: Any,
        default: str = "",
    ) -> str:
        if value is None:
            return default

        return str(value)

    def _safe_list(self, value: Any) -> list:
        if value is None:
            return []

        if isinstance(value, list):
            return list(value)

        if isinstance(value, tuple):
            return list(value)

        if isinstance(value, set):
            return list(value)

        if isinstance(value, str):
            return [value] if value.strip() else []

        return [value]

    def _first(
        self,
        mapping: Dict[str, Any],
        keys: Iterable[str],
        default: Any = None,
    ) -> Any:
        if not isinstance(mapping, dict):
            return default

        for key in keys:
            if key in mapping and mapping[key] is not None:
                return mapping[key]

        return default

    def _section(
        self,
        legacy: Dict[str, Any],
        name: str,
    ) -> Dict[str, Any]:
        value = legacy.get(name, {})

        return value if isinstance(value, dict) else {}

    def legacy_to_analysis(
        self,
        legacy: Dict[str, Any],
        analysis: Optional[AnalysisModel] = None,
    ) -> AnalysisModel:
        """
        Populate AnalysisModel from mixed legacy structures.

        Supported:
        - flat aliases, e.g. FinalScore
        - nested structures, e.g. score["final"]
        """

        if not isinstance(legacy, dict):
            raise ValidationError(
                "Legacy data must be a dictionary."
            )

        model = analysis or AnalysisModel()

        identity = self._section(legacy, "identity")
        score = self._section(legacy, "score")
        confidence = self._section(legacy, "confidence")
        market = self._section(legacy, "market")
        trade = self._section(legacy, "trade")
        timing = self._section(legacy, "entry_timing")
        ai = self._section(legacy, "ai_brain")
        position = self._section(legacy, "position")
        portfolio = self._section(legacy, "portfolio")
        analysis_section = self._section(
            legacy,
            "analysis",
        )

        # Identity
        model.identity.code = self._safe_text(
            self._first(
                legacy,
                ["Code", "code", "Symbol", "symbol"],
                identity.get("code", model.identity.code),
            )
        )

        model.identity.name = self._safe_text(
            self._first(
                legacy,
                ["Name", "name"],
                identity.get("name", model.identity.name),
            )
        )

        model.identity.sector = self._safe_text(
            self._first(
                legacy,
                ["Sector", "sector"],
                identity.get("sector", model.identity.sector),
            )
        )

        model.identity.price = self._safe_float(
            self._first(
                legacy,
                ["Price", "price", "Close", "close"],
                identity.get("price", model.identity.price),
            )
        )

        # Score
        model.score.raw = self._safe_float(
            self._first(
                legacy,
                ["RawScore", "Score", "raw_score"],
                score.get("raw", model.score.raw),
            )
        )

        model.score.quality_penalty = self._safe_float(
            self._first(
                legacy,
                ["QualityPenalty"],
                score.get(
                    "quality_penalty",
                    model.score.quality_penalty,
                ),
            )
        )

        model.score.tradeable = self._safe_float(
            self._first(
                legacy,
                ["TradeableScore"],
                score.get(
                    "tradeable",
                    model.score.tradeable,
                ),
            )
        )

        model.score.institution_bonus = self._safe_float(
            self._first(
                legacy,
                ["InstitutionBonus"],
                score.get(
                    "institution_bonus",
                    model.score.institution_bonus,
                ),
            )
        )

        model.score.regime_bonus = self._safe_float(
            self._first(
                legacy,
                ["RegimeBonus"],
                score.get(
                    "regime_bonus",
                    model.score.regime_bonus,
                ),
            )
        )

        model.score.regime_penalty = self._safe_float(
            self._first(
                legacy,
                ["RegimePenalty"],
                score.get(
                    "regime_penalty",
                    model.score.regime_penalty,
                ),
            )
        )

        model.score.final = self._safe_float(
            self._first(
                legacy,
                ["FinalScore"],
                score.get("final", model.score.final),
            )
        )

        model.score.grade = self._safe_text(
            self._first(
                legacy,
                ["Grade"],
                score.get("grade", model.score.grade),
            )
        )

        # Confidence
        model.confidence = self._safe_float(
            self._first(
                legacy,
                ["Confidence"],
                confidence.get(
                    "value",
                    model.confidence,
                ),
            )
        )

        model.confidence_level = self._safe_text(
            self._first(
                legacy,
                ["ConfLevel"],
                confidence.get(
                    "level",
                    model.confidence_level,
                ),
            )
        )

        # Market
        model.market.trend = self._safe_text(
            self._first(
                legacy,
                ["Trend"],
                market.get(
                    "trend",
                    model.market.trend,
                ),
            )
        )

        model.market.momentum = self._safe_text(
            self._first(
                legacy,
                ["Momentum"],
                market.get(
                    "momentum",
                    model.market.momentum,
                ),
            )
        )

        model.market.volume = self._safe_text(
            self._first(
                legacy,
                ["Volume"],
                market.get(
                    "volume",
                    model.market.volume,
                ),
            )
        )

        model.market.smart_money = self._safe_text(
            self._first(
                legacy,
                ["SmartMoney"],
                market.get(
                    "smart_money",
                    model.market.smart_money,
                ),
            )
        )

        model.market.regime = self._safe_text(
            self._first(
                legacy,
                ["MarketRegime"],
                market.get(
                    "regime",
                    model.market.regime,
                ),
            )
        )

        model.market.regime_score = self._safe_float(
            self._first(
                legacy,
                ["RegimeScore"],
                market.get(
                    "regime_score",
                    model.market.regime_score,
                ),
            )
        )

        model.market.volatility = self._safe_text(
            self._first(
                legacy,
                ["Volatility"],
                market.get(
                    "volatility",
                    model.market.volatility,
                ),
            )
        )

        model.market.mtf_alignment_score = (
            self._safe_float(
                self._first(
                    legacy,
                    ["MTFAlignmentScore"],
                    market.get(
                        "mtf_alignment_score",
                        model.market.mtf_alignment_score,
                    ),
                )
            )
        )

        model.market.mtf_status = self._safe_text(
            self._first(
                legacy,
                ["MTFStatus"],
                market.get(
                    "mtf_status",
                    model.market.mtf_status,
                ),
            )
        )

        # Trade
        model.trade.signal = self._safe_text(
            self._first(
                legacy,
                ["Signal"],
                trade.get(
                    "signal",
                    model.trade.signal,
                ),
            )
        )

        model.trade.decision_signal = self._safe_text(
            self._first(
                legacy,
                ["DecisionSignal"],
                trade.get(
                    "decision_signal",
                    model.trade.decision_signal,
                ),
            )
        )

        model.trade.rating = self._safe_text(
            self._first(
                legacy,
                ["Rating"],
                trade.get(
                    "rating",
                    model.trade.rating,
                ),
            )
        )

        model.trade.entry = self._safe_float(
            self._first(
                legacy,
                ["Entry"],
                trade.get(
                    "entry",
                    model.trade.entry,
                ),
            )
        )

        model.trade.stop_loss = self._safe_float(
            self._first(
                legacy,
                ["StopLoss"],
                trade.get(
                    "stop_loss",
                    model.trade.stop_loss,
                ),
            )
        )

        model.trade.target = self._safe_float(
            self._first(
                legacy,
                ["Target"],
                trade.get(
                    "target",
                    model.trade.target,
                ),
            )
        )

        model.trade.risk_reward = self._safe_float(
            self._first(
                legacy,
                ["RR"],
                trade.get(
                    "risk_reward",
                    model.trade.risk_reward,
                ),
            )
        )

        # Entry Timing
        model.timing.score = self._safe_float(
            self._first(
                legacy,
                ["EntryTimingScore"],
                timing.get(
                    "score",
                    model.timing.score,
                ),
            )
        )

        model.timing.status = self._safe_text(
            self._first(
                legacy,
                ["EntryTimingStatus"],
                timing.get(
                    "status",
                    model.timing.status,
                ),
            )
        )

        model.timing.action = self._safe_text(
            self._first(
                legacy,
                ["EntryTimingAction"],
                timing.get(
                    "action",
                    model.timing.action,
                ),
            )
        )

        model.timing.entry_zone_low = (
            self._safe_float(
                self._first(
                    legacy,
                    ["EntryZoneLow"],
                    timing.get(
                        "entry_zone_low",
                        model.timing.entry_zone_low,
                    ),
                )
            )
        )

        model.timing.entry_zone_high = (
            self._safe_float(
                self._first(
                    legacy,
                    ["EntryZoneHigh"],
                    timing.get(
                        "entry_zone_high",
                        model.timing.entry_zone_high,
                    ),
                )
            )
        )

        model.timing.reasons = self._safe_list(
            self._first(
                legacy,
                ["EntryTimingReasons"],
                timing.get(
                    "reasons",
                    model.timing.reasons,
                ),
            )
        )

        model.timing.warnings = self._safe_list(
            self._first(
                legacy,
                ["EntryTimingWarnings"],
                timing.get(
                    "warnings",
                    model.timing.warnings,
                ),
            )
        )

        # AI Brain
        model.ai.conviction_score = self._safe_float(
            self._first(
                legacy,
                ["AIConviction"],
                ai.get(
                    "conviction_score",
                    model.ai.conviction_score,
                ),
            )
        )

        model.ai.conviction_level = self._safe_text(
            self._first(
                legacy,
                ["AIConvictionLevel"],
                ai.get(
                    "conviction_level",
                    model.ai.conviction_level,
                ),
            )
        )

        model.ai.signal = self._safe_text(
            self._first(
                legacy,
                ["AISignal"],
                ai.get(
                    "ai_signal",
                    ai.get(
                        "signal",
                        model.ai.signal,
                    ),
                ),
            )
        )

        model.ai.prediction_stability = (
            self._safe_float(
                self._first(
                    legacy,
                    ["AIPredictionStability"],
                    ai.get(
                        "prediction_stability",
                        model.ai.prediction_stability,
                    ),
                )
            )
        )

        model.ai.execution_quality = self._safe_float(
            self._first(
                legacy,
                ["AIExecutionQuality"],
                ai.get(
                    "execution_quality",
                    model.ai.execution_quality,
                ),
            )
        )

        reasoning = ai.get("reasoning", {})
        if not isinstance(reasoning, dict):
            reasoning = {}

        model.ai.strengths = self._safe_list(
            self._first(
                legacy,
                ["AIStrengths"],
                reasoning.get(
                    "strengths",
                    ai.get(
                        "strengths",
                        model.ai.strengths,
                    ),
                ),
            )
        )

        model.ai.weaknesses = self._safe_list(
            self._first(
                legacy,
                ["AIWeaknesses"],
                reasoning.get(
                    "weaknesses",
                    ai.get(
                        "weaknesses",
                        model.ai.weaknesses,
                    ),
                ),
            )
        )

        model.ai.summary = self._safe_text(
            self._first(
                legacy,
                ["AISummary"],
                reasoning.get(
                    "summary",
                    ai.get(
                        "summary",
                        model.ai.summary,
                    ),
                ),
            )
        )

        components = ai.get("components", {})
        contributions = ai.get("contributions", {})

        model.ai.components = (
            deepcopy(components)
            if isinstance(components, dict)
            else {}
        )

        model.ai.contributions = (
            deepcopy(contributions)
            if isinstance(contributions, dict)
            else {}
        )

        # Position
        position_fields = {
            "account_capital": (
                ["AccountCapital"],
                "account_capital",
            ),
            "risk_percent": (
                ["RiskPercent"],
                "risk_percent",
            ),
            "risk_capital": (
                ["RiskCapital"],
                "risk_capital",
            ),
            "risk_per_share": (
                ["RiskPerShare"],
                "risk_per_share",
            ),
            "capital_used": (
                ["CapitalUsed", "Capital"],
                "capital_used",
            ),
            "remaining_capital": (
                ["RemainingCapital"],
                "remaining_capital",
            ),
            "allocation_percent": (
                ["Allocation"],
                "allocation_percent",
            ),
            "actual_risk_percent": (
                ["ActualRiskPercent"],
                "actual_risk_percent",
            ),
            "max_loss": (
                ["MaxLoss"],
                "max_loss",
            ),
            "potential_profit": (
                ["PotentialProfit"],
                "potential_profit",
            ),
        }

        for attribute, (
            flat_keys,
            nested_key,
        ) in position_fields.items():
            current = getattr(
                model.position,
                attribute,
            )

            setattr(
                model.position,
                attribute,
                self._safe_float(
                    self._first(
                        legacy,
                        flat_keys,
                        position.get(
                            nested_key,
                            current,
                        ),
                    )
                ),
            )

        model.position.shares = self._safe_int(
            self._first(
                legacy,
                ["Shares"],
                position.get(
                    "shares",
                    model.position.shares,
                ),
            )
        )

        model.position.lots = self._safe_int(
            self._first(
                legacy,
                ["Lots"],
                position.get(
                    "lots",
                    model.position.lots,
                ),
            )
        )

        model.position.status = self._safe_text(
            self._first(
                legacy,
                ["PositionStatus"],
                position.get(
                    "status",
                    model.position.status,
                ),
            )
        )

        model.position.rating = self._safe_text(
            self._first(
                legacy,
                ["PositionRating"],
                position.get(
                    "rating",
                    model.position.rating,
                ),
            )
        )

        # Portfolio
        model.portfolio.eligible = bool(
            self._first(
                legacy,
                ["PortfolioEligible"],
                portfolio.get(
                    "eligible",
                    model.portfolio.eligible,
                ),
            )
        )

        model.portfolio.rank = self._first(
            legacy,
            ["PortfolioRank"],
            portfolio.get(
                "rank",
                model.portfolio.rank,
            ),
        )

        model.portfolio.status = self._safe_text(
            self._first(
                legacy,
                ["PortfolioStatus"],
                portfolio.get(
                    "status",
                    model.portfolio.status,
                ),
            )
        )

        model.portfolio.reason = self._safe_text(
            self._first(
                legacy,
                ["PortfolioReason"],
                portfolio.get(
                    "reason",
                    model.portfolio.reason,
                ),
            )
        )

        integer_fields = {
            "suggested_shares": (
                ["SuggestedShares"],
                "suggested_shares",
            ),
            "suggested_lots": (
                ["SuggestedLots"],
                "suggested_lots",
            ),
            "allocated_shares": (
                ["AllocatedShares"],
                "allocated_shares",
            ),
            "allocated_lots": (
                ["AllocatedLots"],
                "allocated_lots",
            ),
        }

        for attribute, (
            flat_keys,
            nested_key,
        ) in integer_fields.items():
            current = getattr(
                model.portfolio,
                attribute,
            )

            setattr(
                model.portfolio,
                attribute,
                self._safe_int(
                    self._first(
                        legacy,
                        flat_keys,
                        portfolio.get(
                            nested_key,
                            current,
                        ),
                    )
                ),
            )

        float_fields = {
            "suggested_capital": (
                ["SuggestedCapital"],
                "suggested_capital",
            ),
            "suggested_max_loss": (
                ["SuggestedMaxLoss"],
                "suggested_max_loss",
            ),
            "allocated_capital": (
                ["AllocatedCapital"],
                "allocated_capital",
            ),
            "allocated_max_loss": (
                ["AllocatedMaxLoss"],
                "allocated_max_loss",
            ),
            "allocated_potential_profit": (
                ["AllocatedPotentialProfit"],
                "allocated_potential_profit",
            ),
            "allocation_percent": (
                ["PortfolioAllocation"],
                "allocation_percent",
            ),
            "risk_percent": (
                ["PortfolioRiskPercent"],
                "risk_percent",
            ),
            "remaining_cash_after": (
                ["PortfolioRemainingCash"],
                "remaining_cash_after",
            ),
        }

        for attribute, (
            flat_keys,
            nested_key,
        ) in float_fields.items():
            current = getattr(
                model.portfolio,
                attribute,
            )

            setattr(
                model.portfolio,
                attribute,
                self._safe_float(
                    self._first(
                        legacy,
                        flat_keys,
                        portfolio.get(
                            nested_key,
                            current,
                        ),
                    )
                ),
            )

        # Analysis
        model.summary = self._safe_text(
            self._first(
                legacy,
                ["Summary"],
                analysis_section.get(
                    "summary",
                    model.summary,
                ),
            )
        )

        model.reasons = self._safe_list(
            self._first(
                legacy,
                ["Reason"],
                analysis_section.get(
                    "reasons",
                    model.reasons,
                ),
            )
        )

        model.warnings = self._safe_list(
            self._first(
                legacy,
                ["Warning"],
                analysis_section.get(
                    "warnings",
                    model.warnings,
                ),
            )
        )

        model.extra.setdefault(
            "legacy_unmapped",
            {},
        )

        model.normalize()

        return model

    def legacy_to_context(
        self,
        legacy: Dict[str, Any],
        context: Optional[AnalysisContext] = None,
        symbol: Optional[str] = None,
    ) -> AnalysisContext:
        if context is None:
            identity = self._section(
                legacy,
                "identity",
            )

            resolved_symbol = self._safe_text(
                symbol
                or legacy.get("Code")
                or legacy.get("code")
                or legacy.get("Symbol")
                or legacy.get("symbol")
                or identity.get("code")
                or identity.get("symbol")
            )

            if not resolved_symbol:
                raise ValidationError(
                    "A symbol is required to create AnalysisContext."
                )

            context = AnalysisContext(
                symbol=resolved_symbol
            )

        self.legacy_to_analysis(
            legacy=legacy,
            analysis=context.analysis,
        )

        context.metadata["legacy_result"] = deepcopy(
            legacy
        )

        return context

    def analysis_to_legacy(
        self,
        analysis: AnalysisModel,
    ) -> Dict[str, Any]:
        analysis.validate()

        return {
            "Code": analysis.identity.code,
            "Price": analysis.identity.price,
            "RawScore": analysis.score.raw,
            "Score": analysis.score.raw,
            "QualityPenalty": (
                analysis.score.quality_penalty
            ),
            "TradeableScore": (
                analysis.score.tradeable
            ),
            "InstitutionBonus": (
                analysis.score.institution_bonus
            ),
            "RegimeBonus": (
                analysis.score.regime_bonus
            ),
            "RegimePenalty": (
                analysis.score.regime_penalty
            ),
            "FinalScore": analysis.score.final,
            "Grade": analysis.score.grade,
            "Confidence": analysis.confidence,
            "ConfLevel": analysis.confidence_level,
            "Trend": analysis.market.trend,
            "Momentum": analysis.market.momentum,
            "Volume": analysis.market.volume,
            "SmartMoney": analysis.market.smart_money,
            "MarketRegime": analysis.market.regime,
            "RegimeScore": analysis.market.regime_score,
            "Volatility": analysis.market.volatility,
            "MTFAlignmentScore": (
                analysis.market.mtf_alignment_score
            ),
            "MTFStatus": analysis.market.mtf_status,
            "Signal": analysis.trade.signal,
            "DecisionSignal": (
                analysis.trade.decision_signal
            ),
            "Rating": analysis.trade.rating,
            "Entry": analysis.trade.entry,
            "StopLoss": analysis.trade.stop_loss,
            "Target": analysis.trade.target,
            "RR": analysis.trade.risk_reward,
            "EntryTimingScore": analysis.timing.score,
            "EntryTimingStatus": analysis.timing.status,
            "EntryTimingAction": analysis.timing.action,
            "EntryZoneLow": (
                analysis.timing.entry_zone_low
            ),
            "EntryZoneHigh": (
                analysis.timing.entry_zone_high
            ),
            "EntryTimingReasons": list(
                analysis.timing.reasons
            ),
            "EntryTimingWarnings": list(
                analysis.timing.warnings
            ),
            "AIConviction": (
                analysis.ai.conviction_score
            ),
            "AIConvictionLevel": (
                analysis.ai.conviction_level
            ),
            "AISignal": analysis.ai.signal,
            "AIPredictionStability": (
                analysis.ai.prediction_stability
            ),
            "AIExecutionQuality": (
                analysis.ai.execution_quality
            ),
            "AIStrengths": list(
                analysis.ai.strengths
            ),
            "AIWeaknesses": list(
                analysis.ai.weaknesses
            ),
            "AISummary": analysis.ai.summary,
            "AccountCapital": (
                analysis.position.account_capital
            ),
            "RiskPercent": (
                analysis.position.risk_percent
            ),
            "RiskCapital": (
                analysis.position.risk_capital
            ),
            "RiskPerShare": (
                analysis.position.risk_per_share
            ),
            "Shares": analysis.position.shares,
            "Lots": analysis.position.lots,
            "Capital": (
                analysis.position.capital_used
            ),
            "CapitalUsed": (
                analysis.position.capital_used
            ),
            "RemainingCapital": (
                analysis.position.remaining_capital
            ),
            "Allocation": (
                analysis.position.allocation_percent
            ),
            "ActualRiskPercent": (
                analysis.position.actual_risk_percent
            ),
            "MaxLoss": analysis.position.max_loss,
            "PotentialProfit": (
                analysis.position.potential_profit
            ),
            "PositionStatus": (
                analysis.position.status
            ),
            "PositionRating": (
                analysis.position.rating
            ),
            "PortfolioEligible": (
                analysis.portfolio.eligible
            ),
            "PortfolioRank": (
                analysis.portfolio.rank
            ),
            "PortfolioStatus": (
                analysis.portfolio.status
            ),
            "PortfolioReason": (
                analysis.portfolio.reason
            ),
            "SuggestedShares": (
                analysis.portfolio.suggested_shares
            ),
            "SuggestedLots": (
                analysis.portfolio.suggested_lots
            ),
            "SuggestedCapital": (
                analysis.portfolio.suggested_capital
            ),
            "SuggestedMaxLoss": (
                analysis.portfolio.suggested_max_loss
            ),
            "AllocatedShares": (
                analysis.portfolio.allocated_shares
            ),
            "AllocatedLots": (
                analysis.portfolio.allocated_lots
            ),
            "AllocatedCapital": (
                analysis.portfolio.allocated_capital
            ),
            "AllocatedMaxLoss": (
                analysis.portfolio.allocated_max_loss
            ),
            "AllocatedPotentialProfit": (
                analysis.portfolio.allocated_potential_profit
            ),
            "PortfolioAllocation": (
                analysis.portfolio.allocation_percent
            ),
            "PortfolioRiskPercent": (
                analysis.portfolio.risk_percent
            ),
            "PortfolioRemainingCash": (
                analysis.portfolio.remaining_cash_after
            ),
            "Summary": analysis.summary,
            "Reason": list(analysis.reasons),
            "Warning": list(analysis.warnings),
            "identity": {
                "code": analysis.identity.code,
                "name": analysis.identity.name,
                "sector": analysis.identity.sector,
                "price": analysis.identity.price,
            },
            "score": {
                "raw": analysis.score.raw,
                "quality_penalty": (
                    analysis.score.quality_penalty
                ),
                "tradeable": (
                    analysis.score.tradeable
                ),
                "institution_bonus": (
                    analysis.score.institution_bonus
                ),
                "regime_bonus": (
                    analysis.score.regime_bonus
                ),
                "regime_penalty": (
                    analysis.score.regime_penalty
                ),
                "final": analysis.score.final,
                "grade": analysis.score.grade,
            },
            "confidence": {
                "value": analysis.confidence,
                "level": analysis.confidence_level,
            },
            "market": {
                "trend": analysis.market.trend,
                "momentum": analysis.market.momentum,
                "volume": analysis.market.volume,
                "smart_money": (
                    analysis.market.smart_money
                ),
                "regime": analysis.market.regime,
                "regime_score": (
                    analysis.market.regime_score
                ),
                "volatility": (
                    analysis.market.volatility
                ),
                "mtf_alignment_score": (
                    analysis.market.mtf_alignment_score
                ),
                "mtf_status": (
                    analysis.market.mtf_status
                ),
            },
            "trade": {
                "signal": analysis.trade.signal,
                "decision_signal": (
                    analysis.trade.decision_signal
                ),
                "rating": analysis.trade.rating,
                "entry": analysis.trade.entry,
                "stop_loss": (
                    analysis.trade.stop_loss
                ),
                "target": analysis.trade.target,
                "risk_reward": (
                    analysis.trade.risk_reward
                ),
            },
            "entry_timing": {
                "score": analysis.timing.score,
                "status": analysis.timing.status,
                "action": analysis.timing.action,
                "entry_zone_low": (
                    analysis.timing.entry_zone_low
                ),
                "entry_zone_high": (
                    analysis.timing.entry_zone_high
                ),
                "reasons": list(
                    analysis.timing.reasons
                ),
                "warnings": list(
                    analysis.timing.warnings
                ),
            },
            "ai_brain": {
                "conviction_score": (
                    analysis.ai.conviction_score
                ),
                "conviction_level": (
                    analysis.ai.conviction_level
                ),
                "ai_signal": analysis.ai.signal,
                "prediction_stability": (
                    analysis.ai.prediction_stability
                ),
                "execution_quality": (
                    analysis.ai.execution_quality
                ),
                "components": deepcopy(
                    analysis.ai.components
                ),
                "contributions": deepcopy(
                    analysis.ai.contributions
                ),
                "reasoning": {
                    "strengths": list(
                        analysis.ai.strengths
                    ),
                    "weaknesses": list(
                        analysis.ai.weaknesses
                    ),
                    "summary": analysis.ai.summary,
                },
            },
            "position": {
                "account_capital": (
                    analysis.position.account_capital
                ),
                "risk_percent": (
                    analysis.position.risk_percent
                ),
                "risk_capital": (
                    analysis.position.risk_capital
                ),
                "risk_per_share": (
                    analysis.position.risk_per_share
                ),
                "shares": analysis.position.shares,
                "lots": analysis.position.lots,
                "capital_used": (
                    analysis.position.capital_used
                ),
                "remaining_capital": (
                    analysis.position.remaining_capital
                ),
                "allocation_percent": (
                    analysis.position.allocation_percent
                ),
                "actual_risk_percent": (
                    analysis.position.actual_risk_percent
                ),
                "max_loss": (
                    analysis.position.max_loss
                ),
                "potential_profit": (
                    analysis.position.potential_profit
                ),
                "status": analysis.position.status,
                "rating": analysis.position.rating,
            },
            "portfolio": {
                "eligible": (
                    analysis.portfolio.eligible
                ),
                "rank": analysis.portfolio.rank,
                "status": analysis.portfolio.status,
                "reason": analysis.portfolio.reason,
                "suggested_shares": (
                    analysis.portfolio.suggested_shares
                ),
                "suggested_lots": (
                    analysis.portfolio.suggested_lots
                ),
                "suggested_capital": (
                    analysis.portfolio.suggested_capital
                ),
                "suggested_max_loss": (
                    analysis.portfolio.suggested_max_loss
                ),
                "allocated_shares": (
                    analysis.portfolio.allocated_shares
                ),
                "allocated_lots": (
                    analysis.portfolio.allocated_lots
                ),
                "allocated_capital": (
                    analysis.portfolio.allocated_capital
                ),
                "allocated_max_loss": (
                    analysis.portfolio.allocated_max_loss
                ),
                "allocated_potential_profit": (
                    analysis.portfolio.allocated_potential_profit
                ),
                "allocation_percent": (
                    analysis.portfolio.allocation_percent
                ),
                "risk_percent": (
                    analysis.portfolio.risk_percent
                ),
                "remaining_cash_after": (
                    analysis.portfolio.remaining_cash_after
                ),
            },
            "analysis": {
                "summary": analysis.summary,
                "reasons": list(
                    analysis.reasons
                ),
                "warnings": list(
                    analysis.warnings
                ),
            },
        }

    def context_to_legacy(
        self,
        context: AnalysisContext,
    ) -> Dict[str, Any]:
        if not isinstance(context, AnalysisContext):
            raise ValidationError(
                "Expected AnalysisContext."
            )

        legacy = self.analysis_to_legacy(
            context.analysis
        )

        previous = context.metadata.get(
            "legacy_result",
            {},
        )

        if isinstance(previous, dict):
            merged = deepcopy(previous)
            merged.update(legacy)
            legacy = merged

        context.metadata["legacy_result"] = deepcopy(
            legacy
        )

        return legacy
