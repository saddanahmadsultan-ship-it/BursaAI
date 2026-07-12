from __future__ import annotations
from copy import deepcopy
from typing import Callable, Dict, Optional
from Adapters.base_adapter import BaseAdapter
from Framework.context import AnalysisContext
from Framework.event_bus import EventBus
from Framework.exceptions import ValidationError
from Framework.metadata import EngineMetadata
from Framework.service_container import ServiceContainer

class DynamicRiskAdapter(BaseAdapter):
    METADATA = EngineMetadata(name='Dynamic Risk Adapter', version='6.0', priority=150, category='risk', dependencies=['Decision Adapter'])

    def __init__(self, risk_function: Optional[Callable[[Dict], Dict]] = None, services: Optional[ServiceContainer] = None, event_bus: Optional[EventBus] = None):
        super().__init__(metadata=self.METADATA)
        if risk_function is None:
            from Core.dynamic_risk_manager import apply_dynamic_risk_manager
            risk_function = apply_dynamic_risk_manager
        self.risk_function = risk_function
        self.services = services
        if event_bus is not None:
            self.event_bus = event_bus
        elif services is not None and services.contains('event_bus'):
            self.event_bus = services.resolve('event_bus')
        else:
            self.event_bus = None

    def run_legacy(self, context: AnalysisContext):
        output = self.risk_function(self.bridge.context_to_legacy(context))
        if output is None:
            raise ValidationError('Dynamic Risk Manager returned None.')
        if not isinstance(output, dict):
            raise ValidationError('Dynamic Risk output must be a dictionary.')
        return output

    def sync_to_context(self, context, legacy_output) -> None:
        output = deepcopy(legacy_output)
        dynamic = output.get('dynamic_risk', {})
        if not isinstance(dynamic, dict):
            dynamic = {}
        context.metadata['dynamic_risk_data'] = output
        context.analysis.extra['dynamic_risk'] = deepcopy(dynamic)
        context.analysis.position.risk_percent = self.bridge._safe_float(output.get('DynamicRiskPercent', dynamic.get('final_risk_percent', 0)))
        context.analysis.extra['dynamic_risk_status'] = str(output.get('DynamicRiskStatus', dynamic.get('status', 'UNKNOWN')))
        context.analysis.extra['dynamic_risk_reason'] = str(output.get('DynamicRiskReason', dynamic.get('reason', '')))
        context.analysis.extra['dynamic_risk_multiplier'] = self.bridge._safe_float(output.get('DynamicRiskMultiplier', dynamic.get('combined_multiplier', 0)))
        context.analysis.extra['base_risk_percent'] = self.bridge._safe_float(output.get('BaseRiskPercent', dynamic.get('base_risk_percent', 0)))
        context.analysis.extra['calculated_risk_percent'] = self.bridge._safe_float(output.get('CalculatedRiskPercent', dynamic.get('calculated_risk_percent', 0)))
        context.analysis.extra['dynamic_volatility'] = str(output.get('DynamicVolatility', dynamic.get('volatility', 'UNKNOWN')))
        context.analysis.extra['dynamic_risk_multipliers'] = deepcopy(dynamic.get('multipliers', {}))
        if self.event_bus is not None:
            self.event_bus.publish('DynamicRiskCalculated', payload={
                'symbol': context.symbol,
                'base_risk_percent': context.analysis.extra['base_risk_percent'],
                'calculated_risk_percent': context.analysis.extra['calculated_risk_percent'],
                'dynamic_risk_percent': context.analysis.position.risk_percent,
                'status': context.analysis.extra['dynamic_risk_status'],
                'reason': context.analysis.extra['dynamic_risk_reason'],
                'multiplier': context.analysis.extra['dynamic_risk_multiplier'],
                'volatility': context.analysis.extra['dynamic_volatility'],
            }, source=self.name)
