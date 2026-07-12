from pathlib import Path
import sys
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Adapters.dynamic_risk_adapter import DynamicRiskAdapter
from Framework.context import AnalysisContext
from Framework.event_bus import EventBus


def fake_dynamic_risk(result):
    output = dict(result)
    output['dynamic_risk'] = {
        'base_risk_percent': 1.0,
        'combined_multiplier': 0.72,
        'calculated_risk_percent': 0.72,
        'final_risk_percent': 0.72,
        'status': 'NORMAL RISK',
        'reason': 'RISK ADJUSTED BY MARKET AND TRADE QUALITY',
        'volatility': 'LOW',
        'multipliers': {'signal': 1.0, 'timing': 1.0},
    }
    output['BaseRiskPercent'] = 1.0
    output['DynamicRiskMultiplier'] = 0.72
    output['CalculatedRiskPercent'] = 0.72
    output['DynamicRiskPercent'] = 0.72
    output['DynamicRiskStatus'] = 'NORMAL RISK'
    output['DynamicRiskReason'] = 'RISK ADJUSTED BY MARKET AND TRADE QUALITY'
    output['DynamicVolatility'] = 'LOW'
    return output


def main():
    events = EventBus()
    received = []
    events.subscribe('DynamicRiskCalculated', lambda event: received.append(event))

    context = AnalysisContext(symbol='1155.KL')
    context.analysis.identity.price = 10.4
    context.analysis.trade.signal = 'STRONG BUY'
    context.analysis.trade.risk_reward = 2.0
    context.analysis.confidence = 92
    context.analysis.score.final = 88
    context.analysis.market.regime = 'BULLISH'
    context.analysis.market.smart_money = 'EARLY'
    context.analysis.timing.status = 'READY'
    context.analysis.ai.conviction_level = 'INSTITUTIONAL CONVICTION'

    adapter = DynamicRiskAdapter(
        risk_function=fake_dynamic_risk,
        event_bus=events,
    )
    result = adapter.execute(context)

    assert result.success is True
    assert context.analysis.position.risk_percent == 0.72
    assert context.analysis.extra['dynamic_risk_status'] == 'NORMAL RISK'
    assert context.analysis.extra['dynamic_risk_multiplier'] == 0.72
    assert context.analysis.extra['base_risk_percent'] == 1.0
    assert len(received) == 1
    assert received[0].payload['dynamic_risk_percent'] == 0.72

    print('=' * 72)
    print('BURSAAI v6.0 SPRINT 5C.1 TEST')
    print('=' * 72)
    print('Dynamic Risk Adapter    : OK')
    print('Position Risk Sync      : OK')
    print('Status / Reason Sync    : OK')
    print('Multiplier Sync         : OK')
    print('Event Publication       : OK')
    print('=' * 72)
    print('SPRINT 5C.1 DYNAMIC RISK ADAPTER OK')


if __name__ == '__main__':
    main()
