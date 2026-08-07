# Trafiq AI — Dataset Specification

## 1. Overview

The Trafiq AI dataset is designed to transform raw website data into structured features that can be used by Machine Learning models.

The dataset is not intended to represent a simple collection of SEO metrics.

Its purpose is to provide a structured representation of a website's:

- technical health;
- HTML structure;
- content characteristics;
- internal linking;
- image optimization;
- performance-related signals;
- security configuration;
- semantic characteristics;
- and other measurable website properties.

The dataset will progressively evolve as more websites are analyzed and additional validated outcomes become available.

---

## 2. Machine Learning Objective

Trafiq AI will use the dataset to support several Machine Learning tasks.

### 2.1 SEO Quality Prediction

A regression model will estimate a website quality indicator from its measurable characteristics.

Input:

    Website features

Output:

    Predicted SEO quality

This model is intended to identify statistical relationships between website characteristics and overall SEO quality.

The initial target will be treated as a methodology-based baseline rather than an absolute representation of SEO performance.

---

### 2.2 Issue Priority Classification

A classification model may be used to estimate the priority of detected SEO issues.

Possible classes:

- LOW
- MEDIUM
- HIGH
- CRITICAL

The initial labels may combine deterministic rules and human validation.

As Trafiq AI collects real-world feedback and outcomes, the labeling strategy will progressively evolve.

---

### 2.3 Growth Opportunity Prediction

A future model will estimate the potential opportunity associated with website improvements.

The output will not represent a guaranteed traffic increase.

Instead, Trafiq AI will use an opportunity score and, when sufficient data becomes available, an associated confidence estimate.

Example:

    Opportunity Score: 82
    Confidence: 76%

This distinction is important because SEO outcomes are influenced by many external factors.

---

### 2.4 Website Segmentation

Unsupervised Machine Learning techniques may be used to identify groups of websites with similar characteristics.

Potential segments may include:

- e-commerce;
- local businesses;
- corporate websites;
- blogs;
- content-focused websites.

The clustering algorithm itself will not initially know these business categories.

They will be interpreted after the clustering process using the characteristics of each cluster.

---

# 3. Dataset Architecture

The data pipeline will progressively transform raw website information into Machine Learning-ready data.

```text
Website URL
    |
    v
Web Crawler
    |
    v
Raw HTML / HTTP Data
    |
    v
Data Cleaning
    |
    v
Feature Extraction
    |
    v
Feature Engineering
    |
    v
Processed Dataset
    |
    +--------------------+
    |                    |
    v                    v
Labeled Dataset      Unsupervised Dataset
    |                    |
    v                    v
Supervised ML        Clustering