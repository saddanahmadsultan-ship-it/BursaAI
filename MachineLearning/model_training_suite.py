from dataclasses import dataclass
from pathlib import Path
from statistics import mean,pstdev
from sklearn.model_selection import StratifiedKFold, train_test_split
from MachineLearning.evaluator import ClassificationEvaluator
from MachineLearning.evaluation_models import ModelEvaluationResult
from MachineLearning.model_factory import MLModelFactory
from MachineLearning.model_registry import MLModelRegistry
from MachineLearning.sklearn_models import SklearnClassifierModel
from MachineLearning.sklearn_registry import SklearnModelRegistry
from MachineLearning.model_selection import ModelSelector
@dataclass
class ModelTrainingSuiteConfig:
    train_ratio: float=.70; validation_ratio: float=.15; cross_validation_folds: int=4; random_state: int=42
class ModelTrainingSuite:
    def __init__(self,output_dir,config=None): self.output_dir=Path(output_dir); self.output_dir.mkdir(parents=True,exist_ok=True); self.config=config or ModelTrainingSuiteConfig(); self.evaluator=ClassificationEvaluator(); self.selector=ModelSelector()
    def run(self,dataset):
        X, y = dataset.as_matrix()
        Xtr, Xtemp, ytr, ytemp = train_test_split(
            X,
            y,
            test_size=(1.0 - self.config.train_ratio),
            stratify=y,
            random_state=self.config.random_state,
        )
        relative_test = (1.0 - self.config.train_ratio - self.config.validation_ratio) / (1.0 - self.config.train_ratio)
        minority_temp = min(sum(value >= 0.5 for value in ytemp), sum(value < 0.5 for value in ytemp))
        if minority_temp >= 2:
            Xv, Xt, yv, yt = train_test_split(
                Xtemp,
                ytemp,
                test_size=relative_test,
                stratify=ytemp,
                random_state=self.config.random_state,
            )
        else:
            # Small research batches cannot always support two stratified holdouts.
            # Reuse the holdout for validation and test until more experiments exist.
            Xv, yv = list(Xtemp), list(ytemp)
            Xt, yt = list(Xtemp), list(ytemp)
        results=[]
        breg=MLModelRegistry(self.output_dir); sreg=SklearnModelRegistry(self.output_dir)
        for key,model in MLModelFactory.build_default_models(self.config.random_state).items():
            model.metadata.feature_names=dataset.feature_names; model.fit(Xtr,ytr)
            tm=self.evaluator.evaluate(ytr,[x.prediction for x in model.predict(Xtr)]); vm=self.evaluator.evaluate(yv,[x.prediction for x in model.predict(Xv)]); xm=self.evaluator.evaluate(yt,[x.prediction for x in model.predict(Xt)])
            cv=self._cv(key,Xtr,ytr); cvm=mean(cv) if cv else 0; cvs=pstdev(cv) if len(cv)>1 else 0; gap=abs(tm.accuracy-xm.accuracy); stab=max(0,min(1,cvm-cvs)); model.metadata.metrics={'train_accuracy':tm.accuracy,'validation_accuracy':vm.accuracy,'test_accuracy':xm.accuracy,'test_f1':xm.f1_score,'cv_mean':cvm,'cv_std':cvs,'generalization_gap':gap}
            path=sreg.save(model) if isinstance(model,SklearnClassifierModel) else breg.save(model)
            results.append(ModelEvaluationResult(model.metadata.model_name,model.__class__.__name__,tm,vm,xm,round(gap,6),round(cvm,6),round(cvs,6),round(stab,6),0.0,str(path)))
        ranked=self.selector.rank(results); return {'ranked_results':ranked,'best_model':ranked[0] if ranked else None}
    def _cv(self,key,X,y):
        pos=sum(v>=.5 for v in y); neg=len(y)-pos; folds=min(self.config.cross_validation_folds,pos,neg)
        if folds<2:return []
        out=[]; sp=StratifiedKFold(n_splits=folds,shuffle=True,random_state=self.config.random_state)
        for tr,te in sp.split(X,y):
            m=MLModelFactory.build_default_models(self.config.random_state)[key]; Xtr=[X[i] for i in tr]; ytr=[y[i] for i in tr]; Xte=[X[i] for i in te]; yte=[y[i] for i in te]; m.fit(Xtr,ytr); out.append(self.evaluator.evaluate(yte,[p.prediction for p in m.predict(Xte)]).balanced_accuracy)
        return out
