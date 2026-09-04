# Trafiq AI — SEO Knowledge Specification

## 1. Purpose

This document defines the SEO knowledge sources used to design
Trafiq AI's SEO features, validation rules, and weak supervision
labeling functions.

The primary reference is Google Search Central.

Semrush and Ahrefs are used as complementary references to identify
additional technical, on-page, crawling, indexing, performance,
internal linking, and structured-data signals.

These sources are references for feature design and rule design.

They are not treated as ground-truth labels.

---

# 2. Knowledge Sources

## 2.1 Google Search Central

Google Search Central is the primary SEO reference for Trafiq AI.

It provides guidance concerning:

- Search Essentials
- crawling
- indexing
- title links
- snippets
- meta descriptions
- images
- structured data
- canonicalization
- mobile considerations
- page experience
- Core Web Vitals

Google's documentation is used to establish the fundamental
principles behind Trafiq AI's feature design.

Reference:

https://developers.google.com/search/docs/fundamentals/seo-starter-guide

---

## 2.2 Semrush

Semrush is used as a secondary reference for technical and
on-page SEO auditing.

Relevant areas include:

- crawlability
- indexability
- HTTPS
- robots.txt
- internal linking
- redirects
- status codes
- performance
- Core Web Vitals
- structured data
- hreflang
- meta tags
- headings
- content

Semrush Site Audit provides a broad collection of technical and
on-page SEO checks.

Reference:

https://www.semrush.com/kb/31-site-audit

---

## 2.3 Ahrefs

Ahrefs is used as an additional secondary reference for technical,
on-page, and site-architecture analysis.

Relevant areas include:

- title tags
- meta descriptions
- H1
- images
- internal links
- redirects
- canonical URLs
- sitemap
- noindex
- hreflang
- structured data
- duplicate content
- crawlability
- indexability

Reference:

https://help.ahrefs.com/en/collections/87920-site-audit

---

# 3. Knowledge Hierarchy

Trafiq AI does not treat all external sources as equivalent.

The hierarchy is:

1. Google Search Central
2. Semrush
3. Ahrefs
4. Trafiq AI experimental heuristics

Google provides the primary principles.

Semrush and Ahrefs are complementary references.

Trafiq AI heuristics are experimental rules created to transform
observable SEO features into weak labels.

---

# 4. Feature Categories

Trafiq AI organizes SEO features into several categories.

## 4.1 On-page SEO

Examples:

- title
- meta description
- H1-H6
- textual content
- images
- image alt attributes
- internal links
- external links

---

## 4.2 Technical SEO

Examples:

- HTTP status
- HTTPS
- canonical
- robots directives
- robots.txt
- sitemap
- indexability
- redirects

---

## 4.3 Performance

Examples:

- response time
- HTML size
- page loading metrics
- Core Web Vitals

---

## 4.4 Site Architecture

Examples:

- internal links
- crawl depth
- orphan pages
- canonical relationships
- sitemap coverage

Some site-architecture features require crawling multiple URLs and
cannot be reliably determined from a single-page crawl.

---

## 4.5 Structured Data

Examples:

- JSON-LD
- Schema.org
- structured-data detection
- structured-data validity
- supported search features

---

## 4.6 International SEO

Examples:

- hreflang
- language attributes
- regional versions

---

# 5. Current Trafiq AI Features

The current feature set includes:

- title_exists
- title_length
- title_word_count

- meta_description_exists
- meta_description_length
- meta_description_word_count

- h1_count
- h2_count
- h3_count
- h4_count
- h5_count
- h6_count

- word_count
- character_count
- unique_word_count
- unique_word_ratio

- image_count
- images_with_alt
- images_without_alt
- empty_alt_count

- total_link_count
- internal_link_count
- external_link_count
- nofollow_link_count
- sponsored_link_count
- ugc_link_count

- response_time_ms
- redirect_count

---

# 6. Planned Feature Expansion

The following features are planned for future iterations.

## Technical

- canonical
- robots meta directives
- robots.txt
- sitemap
- HTTPS
- indexability
- redirect analysis

## Structured Data

- JSON-LD detection
- Schema.org detection
- structured-data validation

## Performance

- Core Web Vitals
- page resource analysis
- additional performance signals

## Internationalization

- language
- hreflang

## Site Architecture

- crawl depth
- orphan pages
- duplicate content
- site-wide internal linking
- sitemap coverage

---

# 7. Feature Design Principles

A feature is an observable signal.

A feature must not automatically be interpreted as a complete SEO
verdict.

For example:

A page containing zero images should not automatically be classified
as POOR.

Instead:

image_count = 0

may produce:

ABSTAIN

because the absence of images alone does not provide enough evidence
to determine the overall SEO quality of a page.

---

# 8. Weak Supervision

Trafiq AI uses multiple labeling functions to transform observable
SEO features into weak labels.

Each labeling function may return:

- GOOD
- AVERAGE
- POOR
- ABSTAIN

The individual outputs are preserved.

Example:

TITLE      -> POOR
META       -> POOR
HEADINGS   -> AVERAGE
CONTENT    -> POOR
IMAGES     -> ABSTAIN
LINKS      -> POOR

These outputs are then passed to the aggregator.

---

# 9. Aggregation

The aggregator combines the outputs of the labeling functions.

ABSTAIN votes are ignored when calculating the active consensus.

Example:

POOR       -> 4 votes
AVERAGE    -> 1 vote
ABSTAIN    -> 1 vote

Active votes:

5

Final label:

POOR

Consensus:

4 / 5 = 0.80

The current confidence value represents labeling-function agreement.

It is not a calibrated probability that the page is objectively
poor for SEO.

---

# 10. Ambiguous Cases

When multiple classes receive the same highest number of votes,
the aggregator must not arbitrarily select a class.

Example:

GOOD -> 2
POOR -> 2

The result is:

ABSTAIN

with:

ambiguous = True

Such observations may be sent to human review rather than being
automatically included in the training dataset.

---

# 11. Human Review

Weak supervision does not replace human validation.

Low-confidence or ambiguous observations should be separated from
high-confidence observations.

The future dataset pipeline will distinguish between:

- automatically accepted labels
- observations requiring human review
- rejected or unusable observations

Human-reviewed observations can later be used to evaluate the quality
of the weak-labeling strategy.

---

# 12. Knowledge Sources vs Training Labels

External SEO documentation is not directly converted into training
labels.

The process is:

SEO documentation
        |
        v
SEO principles
        |
        v
Feature design
        |
        v
Labeling functions
        |
        v
Weak labels
        |
        v
Aggregation
        |
        v
Human validation
        |
        v
Training dataset

This separation prevents Trafiq AI from simply reproducing the scoring
system of another SEO platform.

---

# 13. Experimental Nature of Trafiq AI Rules

Trafiq AI labeling rules are experimental heuristics.

For example, a title-length rule should not be described as an official
Google ranking rule.

The system should distinguish between:

1. documented SEO principles
2. observable features
3. Trafiq AI heuristics
4. machine-learning predictions

This distinction is important for transparency and reproducibility.

---

# 14. Design Objective

The objective is not to reproduce the SEO scoring system of Google,
Semrush, or Ahrefs.

The objective is to build an explainable SEO analysis pipeline that:

- collects observable signals
- applies documented SEO knowledge
- generates weak labels
- measures agreement
- identifies ambiguous observations
- supports human validation
- produces a reproducible machine-learning dataset
- eventually trains an SEO classification model

---

# 15. Future Evolution

The knowledge specification will evolve as new features,
experiments, validation results, and external documentation are
reviewed.

Changes to labeling rules should be documented and versioned.

A change to a labeling function may affect the generated dataset and
should therefore be treated as a dataset-generation change.