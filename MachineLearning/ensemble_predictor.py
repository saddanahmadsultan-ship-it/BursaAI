from __future__ import annotations
from statistics import mean

class EnsemblePredictor:
    def predict(self, models, vector):
        if not models: raise ValueError('No deployment models available.')
        predictions=[]
        for model in models:
            result=model.predict_one(vector)
            probability=result.probability if result.probability is not None else result.prediction
            predictions.append((model.metadata.model_id,float(probability)))
        probability=mean(p for _,p in predictions)
        return {'probability':round(probability,6),'predicted_class':1 if probability>=.5 else 0,'model_ids':[m for m,_ in predictions],'individual_probabilities':dict(predictions)}
