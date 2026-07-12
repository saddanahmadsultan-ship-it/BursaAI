from Research import Experiment,ExperimentRegistry,ParameterSpace
space=ParameterSpace('EMA_RSI_ATR',{'ema_fast':[10,20],'ema_slow':[50,100],'rsi_period':[8,14],'atr_multiplier':[1.5,2.0]})
e=Experiment(name='Sprint 7A.2 Demo',candidates=space.generate_grid_candidates(symbol='1155.KL'),symbols=['1155.KL'])
r=ExperimentRegistry('Experiments');r.register(e)
print('REGISTERED:',e.experiment_id);print('TOTAL:',e.total_candidates);print('MANIFEST: Experiments/registry_manifest.json')
