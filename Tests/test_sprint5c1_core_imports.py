from pathlib import Path
import sys
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

def main():
    from Core.dynamic_risk_manager import apply_dynamic_risk_manager
    from Adapters.dynamic_risk_adapter import DynamicRiskAdapter
    assert callable(apply_dynamic_risk_manager)
    DynamicRiskAdapter(risk_function=apply_dynamic_risk_manager)
    print('SPRINT 5C.1 CORE IMPORTS OK')

if __name__ == '__main__':
    main()
