from MachineLearning.evaluation_models import ClassificationMetrics
class ClassificationEvaluator:
    @staticmethod
    def evaluate(y_true,y_pred):
        a=[1 if float(v)>=.5 else 0 for v in y_true]; p=[1 if float(v)>=.5 else 0 for v in y_pred]
        if len(a)!=len(p): raise ValueError('y_true dan y_pred mesti sama panjang.')
        if not a: return ClassificationMetrics(0,0,0,0,0,0,0,0,0,0)
        tp=sum(x==1 and y==1 for x,y in zip(a,p)); tn=sum(x==0 and y==0 for x,y in zip(a,p)); fp=sum(x==0 and y==1 for x,y in zip(a,p)); fn=sum(x==1 and y==0 for x,y in zip(a,p))
        acc=(tp+tn)/len(a); prec=tp/(tp+fp) if tp+fp else 0; rec=tp/(tp+fn) if tp+fn else 0; spec=tn/(tn+fp) if tn+fp else 0; f1=2*prec*rec/(prec+rec) if prec+rec else 0
        return ClassificationMetrics(round(acc,6),round(prec,6),round(rec,6),round(f1,6),round(spec,6),round((rec+spec)/2,6),tp,tn,fp,fn)
