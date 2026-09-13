# 🚀 Trafiq AI

### Intelligent SEO Analysis Platform Powered by Machine Learning

Trafiq AI is an end-to-end Machine Learning project that analyzes a website from a URL, extracts structured SEO signals, predicts the overall SEO quality of the page, and generates actionable recommendations.

The project combines web crawling, feature engineering, supervised Machine Learning, error analysis, rule-based recommendations, REST API development, and a lightweight frontend.

---

## 🎯 Project Goal

The goal of Trafiq AI is to transform a raw website URL into an understandable SEO diagnosis.

Instead of only checking isolated SEO rules, the project explores whether a Machine Learning model can learn from multiple SEO signals and classify a page into three quality categories:

- `POOR`
- `AVERAGE`
- `GOOD`

The prediction is then combined with a recommendation engine that translates detected SEO weaknesses into concrete actions.

---

# 🏗️ Architecture

```text
                         ┌──────────────────┐
                         │    Website URL   │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │     Crawler      │
                         │  HTTP / HTML     │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ Feature          │
                         │ Extraction       │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ 40 SEO Features  │
                         └────────┬─────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
           ┌─────────────────┐        ┌──────────────────┐
           │ Random Forest   │        │ Recommendation   │
           │ Classifier      │        │ Engine           │
           └────────┬────────┘        └────────┬─────────┘
                    │                          │
                    └─────────────┬────────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │    FastAPI       │
                         │    REST API      │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │    Frontend      │
                         │  SEO Dashboard   │
                         └──────────────────┘
🔄 How Trafiq AI Works
1. Website Crawling

The crawler receives a URL and retrieves the website HTML.

It records technical information such as:

HTTP status
response time
HTML size
crawl quality
crawl identifier
page identifier
content hash

The crawler also detects suspicious captures and classifies crawl quality as:

NORMAL
SUSPECT
FAILED
2. SEO Feature Extraction

The HTML document is transformed into structured numerical and boolean features.

Trafiq AI currently extracts 40 SEO features.

Content
title existence
title length
title word count
meta description existence
meta description length
meta description word count
H1 count
H2 count
H3 count
H4 count
H5 count
H6 count
total heading count
word count
character count
unique word count
unique word ratio
Images
image count
images with ALT
images without ALT
images missing the ALT attribute
empty ALT count
ALT coverage ratio
Links
total links
internal links
external links
nofollow links
sponsored links
UGC links
internal link ratio
unique external domains
Technical SEO
canonical
robots meta
viewport
language
JSON-LD
Schema.org
Conversion signals
CTA count
phone count
email count

These features form the input vector used by the Machine Learning pipeline.

📊 Human-Reviewed Dataset

The current supervised dataset contains:

15 human-reviewed pages
40 SEO features
3 target classes
3 annotators

The final labels are based on human consensus.

Consensus distribution
Label	Pages
POOR	5
AVERAGE	6
GOOD	4

The dataset also stores the strength of the consensus and whether annotators disagreed.

This is important because the current dataset is intentionally small and contains disagreement between human reviewers.

🤖 Machine Learning

Trafiq AI currently uses Scikit-learn for the Machine Learning pipeline.

The main baseline models are:

Logistic Regression
Random Forest

The target variable is:

POOR
AVERAGE
GOOD

The models use the 40 SEO features as input.

Human labels and other review metadata are not used as model features.

🧪 Model Evaluation

Because the dataset is currently very small, the models are evaluated using stratified cross-validation.

Logistic Regression
Accuracy:            26.7%
Macro-F1:            23.6%
Balanced Accuracy:   27.8%
Random Forest
Accuracy:            26.7%
Macro-F1:            27.4%
Balanced Accuracy:   26.1%

These results should be interpreted carefully.

The current dataset contains only 15 labeled pages, so these metrics are not sufficient to claim production-level model performance.

The current models should therefore be considered experimental baselines.

The main objective at this stage is to validate the complete Machine Learning pipeline and identify what needs to improve in the dataset and modeling strategy.

🔍 Error Analysis

Model evaluation is complemented by error analysis.

For the current Random Forest baseline:

Correct predictions: 4 / 15
Errors:              11 / 15

The largest error pattern is:

POOR → AVERAGE

This analysis highlights an important limitation of the current system: the model does not yet have enough training data to reliably learn the boundary between neighboring SEO quality classes.

The analysis also shows that human consensus alone does not solve the problem.

Increasing the size and quality of the labeled dataset is therefore a higher priority than aggressive hyperparameter tuning.

📈 Feature Analysis

The project also analyzes which SEO features contribute most to the Random Forest decisions.

Among the features with higher observed importance are:

images with ALT
internal link count
meta description word count
image count
internal link ratio
meta description length
total link count
ALT coverage ratio
heading count
external unique domains

These results are exploratory because the dataset is currently very small.

💡 Recommendation Engine

The Machine Learning prediction and recommendation engine are deliberately separated.

The model answers:

What is the predicted SEO quality?

The recommendation engine answers:

What should be improved?

Recommendations are generated from detected SEO signals and assigned:

a category
a severity
an actionable message

Severity levels:

HIGH
MEDIUM
LOW

Example:

MEDIUM
Improve image ALT coverage

LOW
Reduce title length

This separation makes the system easier to understand, test, and evolve.

🌐 REST API

Trafiq AI exposes the analysis pipeline through a FastAPI REST API.

Health check
GET /health

Example response:

{
  "status": "ok",
  "service": "trafiq-ai"
}
Analyze a URL
POST /analyze

Request:

{
  "url": "https://www.example.com/",
  "timeout": 15
}

The response contains information such as:

crawl status
crawl quality
SEO features
predicted class
class probabilities
recommendations
technical metadata
Interactive API documentation

FastAPI also provides interactive API documentation through:

/docs
🖥️ Frontend

Trafiq AI includes a lightweight frontend designed for demonstration purposes.

The interface allows users to:

Enter a website URL.
Launch an SEO analysis.
View the predicted quality class.
View class probabilities.
See crawl and HTTP information.
Browse the extracted SEO features.
Review prioritized recommendations.

The frontend communicates with the FastAPI backend through the REST API.

🧰 Technical Stack
Backend
Python
FastAPI
Uvicorn
Pydantic
Web Crawling & Extraction
Requests
BeautifulSoup
Machine Learning
Scikit-learn
Logistic Regression
Random Forest
Data Processing
Pandas
NumPy
Frontend
HTML
CSS
JavaScript
Model Persistence
Joblib
📁 Project Structure
trafiq-ai/
│
├── api/
│   ├── __init__.py
│   └── app.py
│
├── crawler/
│   ├── __init__.py
│   ├── crawler.py
│   ├── extractor.py
│   ├── pipeline.py
│   ├── schemas.py
│   ├── storage.py
│   └── tests/
│
├── ml/
│   ├── feature_config.py
│   ├── analyze_url.py
│   ├── baseline_train_v3.py
│   ├── build_training_dataset_v3.py
│   ├── error_analysis_v3.py
│   ├── feature_analysis_v3.py
│   ├── predict_v3.py
│   └── recommendation_engine.py
│
├── data/
│   ├── models/
│   ├── processed/
│   └── reviewed/
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   ├── app.js
│   └── logo-trafiq.jpeg
│
├── docs/
│
├── requirements.txt
└── README.md
🚀 Installation

Clone the repository:

git clone https://github.com/Moctar93/trafiq-ai.git
cd trafiq-ai

Create a virtual environment:

python -m venv venv
Windows
venv\Scripts\activate
Linux / macOS
source venv/bin/activate

Install dependencies:

pip install -r requirements.txt
▶️ Running the API

From the project root:

python -m api.app

The API will be available at:

http://127.0.0.1:8000

Interactive documentation:

http://127.0.0.1:8000/docs
🔎 Running an Analysis

The analysis pipeline can also be executed directly:

python -m ml.analyze_url https://www.example.com/

The system will:

URL
 ↓
Crawler
 ↓
HTML extraction
 ↓
40 SEO features
 ↓
Random Forest
 ↓
Prediction
 ↓
Recommendations
🧪 Testing

The project contains tests for the crawler and extraction pipeline.

Example:

python -m pytest
⚠️ Current Limitations

Trafiq AI is currently a Machine Learning prototype and technical demonstration.

The main limitations are:

Small dataset

The supervised dataset currently contains only 15 human-reviewed pages.

This makes model evaluation statistically unstable.

Crawl limitations

Some websites may:

block automated requests
return HTTP errors
use anti-bot mechanisms
rely heavily on JavaScript rendering
restrict access to their HTML content
Model confidence

The probability displayed by the Random Forest is not a calibrated probability of prediction correctness.

For example, a prediction with a maximum probability of 82% should not be interpreted as:

"The model is 82% accurate."

It represents the model's estimated class probability for that individual prediction.

🔮 Future Improvements
Data
Increase the number of human-reviewed websites.
Improve annotation guidelines.
Collect multiple page types and website categories.
Reduce class imbalance.
Investigate label calibration and inter-annotator agreement.
Machine Learning
Benchmark additional models once the dataset is large enough.
Hyperparameter optimization.
Probability calibration.
Better validation strategies.
Explainability with SHAP or similar XAI techniques.
Crawling
Better handling of JavaScript-rendered websites.
Rate limiting.
Retry strategies.
More robust anti-bot handling.
Multi-page website crawling.
Product
Website history.
Comparative audits.
SEO report export.
Competitive analysis.
Monitoring over time.
🎓 Project Learning Objectives

Through Trafiq AI, the project demonstrates the ability to build an end-to-end Machine Learning system involving:

data collection
data cleaning
feature engineering
dataset construction
human annotation
supervised learning
model evaluation
error analysis
inference
recommendation generation
REST API development
frontend integration

The project also emphasizes an important engineering principle:

A Machine Learning system is not only a model. It is the complete pipeline around the model.

📜 License

MIT License
