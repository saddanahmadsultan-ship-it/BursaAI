from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from MachineLearning.simple_models import MeanThresholdClassifier
from MachineLearning.sklearn_models import SklearnClassifierModel
class MLModelFactory:
    @staticmethod
    def build_default_models(random_state=42):
        return {
          'mean_threshold':MeanThresholdClassifier('Mean Threshold Baseline'),
          'logistic_regression':SklearnClassifierModel(LogisticRegression(max_iter=1000,class_weight='balanced',random_state=random_state),'Logistic Regression'),
          'decision_tree':SklearnClassifierModel(DecisionTreeClassifier(max_depth=5,min_samples_leaf=2,class_weight='balanced',random_state=random_state),'Decision Tree'),
          'random_forest':SklearnClassifierModel(RandomForestClassifier(n_estimators=20,max_depth=6,min_samples_leaf=2,class_weight='balanced',random_state=random_state,n_jobs=1),'Random Forest')}
