from sklearn.metrics import average_precision_score, make_scorer, precision_score, recall_score, f1_score, accuracy_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_validate


def score_classification(name, model_or_class, X, y, model_params=None, cv=5):
    if callable(model_or_class):
        model = model_or_class(**(model_params or {}))
    else:
        model = model_or_class

    scoring = {
        'accuracy': 'accuracy',
        'precision': make_scorer(precision_score, zero_division=0),
        'recall': make_scorer(recall_score, zero_division=0),
        'f1': make_scorer(f1_score, zero_division=0),
        'roc_auc': make_scorer(roc_auc_score), 
        'pr_auc': make_scorer(average_precision_score) 
    }


    results_cv = cross_validate(
        model,
        X,
        y,
        cv=StratifiedKFold(n_splits=cv, shuffle=True, random_state=42),
        scoring=scoring,
        return_train_score=True
    )

    
    print(f"📊 Model: {name}")
    print(f"→ Accuracy      | Train: {results_cv['train_accuracy'].mean():.3f} | Test: {results_cv['test_accuracy'].mean():.3f}")
    print(f"→ Precision     | Train: {results_cv['train_precision'].mean():.3f} | Test: {results_cv['test_precision'].mean():.3f}")
    print(f"→ Recall        | Train: {results_cv['train_recall'].mean():.3f} | Test: {results_cv['test_recall'].mean():.3f}")
    print(f"→ F1-score      | Train: {results_cv['train_f1'].mean():.3f} | Test: {results_cv['test_f1'].mean():.3f}")
    print(f"→ ROC-AUC-score | Train: {results_cv['train_roc_auc'].mean():.3f} | Test: {results_cv['test_roc_auc'].mean():.3f}")
    print(f"→ PR-AUC-score  | Train: {results_cv['train_pr_auc'].mean():.3f} | Test: {results_cv['test_pr_auc'].mean():.3f}")


    print(f"→ Train Time: {(results_cv['fit_time'].mean() * 1000):.2f} ms")
    print(f"→ Predict Time: {(results_cv['score_time'].mean() * 1000):.2f} ms")

    return {
        "Model": name,
        "Train": {
            "Accuracy":  round(results_cv["train_accuracy"].mean(), 3),
            "Precision": round(results_cv["train_precision"].mean(), 3),
            "Recall":    round(results_cv["train_recall"].mean(), 3),
            "F1":        round(results_cv["train_f1"].mean(), 3),
            "ROC-AUC":   round(results_cv["train_roc_auc"].mean(), 3),
            "PR-AUC":    round(results_cv["train_pr_auc"].mean(), 3),
        },
        "Test": {
            "Accuracy":  round(results_cv["test_accuracy"].mean(), 3),
            "Precision": round(results_cv["test_precision"].mean(), 3),
            "Recall":    round(results_cv["test_recall"].mean(), 3),
            "F1":        round(results_cv["test_f1"].mean(), 3),
            "ROC-AUC":   round(results_cv["test_roc_auc"].mean(), 3),
            "PR-AUC":    round(results_cv["test_pr_auc"].mean(), 3),
        },
        "Times (ms)": {
            "Train":   round(results_cv["fit_time"].mean() * 1000, 2),
            "Predict": round(results_cv["score_time"].mean() * 1000, 2),
        }
    }

