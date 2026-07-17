from __future__ import annotations

class ResearchMLPromotionIntegrator:
    def __init__(self, prediction_service): self.service=prediction_service
    def evaluate(self, ranked_strategy, pareto=None, rule_promotion=None):
        strategy=ranked_strategy.to_dict() if hasattr(ranked_strategy,'to_dict') else dict(ranked_strategy); breakdown=strategy.get('breakdown',{}) or {}; metrics=strategy.get('metrics',{}) or {}; pareto=pareto or {}; rule_promotion=rule_promotion or {}
        raw={'overall_score':breakdown.get('overall_score',0),'performance_score':breakdown.get('performance_score',0),'risk_score':breakdown.get('risk_score',0),'consistency_score':breakdown.get('consistency_score',0),'robustness_score':breakdown.get('robustness_score',0),'confidence_score':breakdown.get('confidence_score',0),'cagr':metrics.get('cagr',0),'sharpe_ratio':metrics.get('sharpe_ratio',0),'sortino_ratio':metrics.get('sortino_ratio',0),'max_drawdown':metrics.get('max_drawdown',0),'volatility':metrics.get('volatility',0),'profit_factor':metrics.get('profit_factor',0),'recovery_factor':metrics.get('recovery_factor',0),'win_rate':metrics.get('win_rate',0),'total_trades':metrics.get('total_trades',0),'pareto_front':pareto.get('front',rule_promotion.get('pareto_front',99)),'crowding_distance':pareto.get('crowding_distance',0)}
        result=self.service.predict(strategy.get('candidate_id','UNKNOWN'),raw,{'rule_action':rule_promotion.get('action',strategy.get('recommendation','')),'tier':rule_promotion.get('approved_tier',strategy.get('tier',''))})
        payload=result.to_dict(); payload['final_action']=result.decision; payload['rule_action']=rule_promotion.get('action',strategy.get('recommendation','')); return payload
