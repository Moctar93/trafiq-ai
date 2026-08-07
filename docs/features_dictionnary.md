# Trafiq AI — Feature Dictionary

## 1. Purpose

This document defines the features extracted from websites and used by the Trafiq AI Machine Learning pipeline.

Each feature must have:

- a unique name;
- a clearly defined data type;
- a measurable source;
- an extraction method;
- a documented interpretation;
- a known missing-value behavior;
- and a clear Machine Learning purpose.

The feature dictionary is a living document and will evolve as the dataset grows and the results of Exploratory Data Analysis (EDA) become available.

---

# 2. Feature Naming Convention

Feature names use `snake_case`.

Examples:

```text
title_length
h1_count
image_alt_ratio
internal_link_count
response_time_ms