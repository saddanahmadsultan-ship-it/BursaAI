from Research import Experiment,ExperimentMode,ExperimentRegistry,ExperimentRunner,ParameterSpace,RunnerConfig
from Research.mock_evaluator import deterministic_mock_evaluator
space=ParameterSpace("EMA_RSI_ATR",{"ema_fast":[10,20,30],"ema_slow":[50,100],"rsi_period":[8,10,14,18],"atr_multiplier":[1.5,2.0]})
exp=Experiment(name="Sprint 7A.3 Demo",mode=ExperimentMode.PARALLEL,candidates=space.generate_grid_candidates(symbol="1155.KL",max_candidates=20),symbols=["1155.KL"])
reg=ExperimentRegistry("Experiments"); reg.register(exp)
stats=ExperimentRunner(reg,deterministic_mock_evaluator,RunnerConfig(max_workers=4,checkpoint_every=2,max_retries=1)).run(exp)
loaded=reg.load(exp.experiment_id); best=loaded.best_candidate()
print("STATUS:",loaded.status.value); print("STATS:",stats.to_dict()); print("BEST:",best.name,best.metrics.final_score)
