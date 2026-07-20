# FairLens AI – Product Requirements Document (PRD)

## Project Scope
FairLens AI is a web application for responsible AI analysis.

Primary capabilities:
- Dataset upload and management
- Data profiling
- Machine learning model training
- Fairness evaluation
- Bias mitigation
- Explainability
- AI-powered insights
- Report generation

The application is intended for researchers, students, data scientists, and organizations evaluating fairness in AI systems.
**Any feature outside this scope requires explicit approval.**

## Dashboard Pages
- **Authentication:** Login, Register, Profile.
- **Dashboard:** Total datasets, active models, bias score, fairness score, accuracy, recent analyses, risk level, latest reports.
- **Dataset Manager:** Upload, preview, rename, delete, version history, search, filter.
- **Data Quality:** Missing values, duplicates, correlation matrix, outlier analysis, class imbalance, feature importance, distribution plots.
- **Bias Analysis:** Demographic Parity, Equal Opportunity, Equalized Odds, Predictive Parity, Calibration, Statistical Parity Difference, Disparate Impact, FPR Difference, FNR Difference.
- **Model Training:** Logistic Regression, Random Forest, Decision Tree, Gradient Boosting, XGBoost, LightGBM, SVM, Neural Network. Metrics: Accuracy, Precision, Recall, F1, ROC AUC, Confusion Matrix.
- **Explainability:** SHAP, LIME, Feature Importance, Partial Dependence.
- **Bias Mitigation:** Reweighing, Optimized Preprocessing, Adversarial Debiasing, Threshold Optimization, Reject Option Classification.
- **Reports:** PDF, DOCX, CSV, Excel. Include charts, recommendations, executive summary.
- **Admin Panel:** Users, Models, Uploaded datasets, Activity logs, System metrics.

## AI Assistant Boundaries
- **MUST DO:** Explain fairness metrics, summarize datasets, interpret charts, recommend mitigation, answer Responsible AI questions.
- **MUST NOT DO:** Automatically retrain models, alter datasets, or make structural changes without explicit user action.

## Non-Goals (MVP)
The following features MUST NOT be implemented before Phase 4:
- Kubernetes deployment
- Multi-tenancy
- Distributed ML training
- GPU acceleration
- Model registry
- Kafka/Event Streaming
- Microservices
- Mobile application
- Multi-language support
- Real-time collaborative editing
Focus on delivering a production-quality MVP first.
