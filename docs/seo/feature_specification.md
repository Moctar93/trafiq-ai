# Trafiq AI — SEO Feature Specification

## 1. Purpose

This document defines the observable SEO features extracted by
Trafiq AI.

Each feature is described according to:

- feature name
- category
- data type
- description
- SEO relevance
- labeling relevance
- current implementation status

The purpose is to maintain a clear separation between:

1. observable website data
2. SEO interpretation
3. labeling rules
4. machine-learning predictions

---

# 2. Feature Categories

Trafiq AI currently organizes features into:

- On-page SEO
- Content
- Images
- Internal and external linking
- Technical SEO
- Performance
- Site architecture
- Structured data
- International SEO

---

# 3. Current Features

## 3.1 Title Features

### title_exists

Category:
On-page SEO

Type:
Boolean

Description:
Indicates whether the HTML document contains a title element.

Possible values:

- true
- false

SEO relevance:
High

Labeling relevance:
High

---

### title_length

Category:
On-page SEO

Type:
Integer

Description:
Number of characters contained in the page title.

SEO relevance:
High

Labeling relevance:
Medium

Important:
The value must be interpreted as a signal rather than as a direct
SEO verdict.

---

### title_word_count

Category:
On-page SEO

Type:
Integer

Description:
Number of words contained in the page title.

SEO relevance:
Medium

Labeling relevance:
Low to Medium

---

# 4. Meta Description Features

## meta_description_exists

Category:
On-page SEO

Type:
Boolean

Description:
Indicates whether a meta description is present.

SEO relevance:
Medium

Labeling relevance:
High

---

## meta_description_length

Category:
On-page SEO

Type:
Integer

Description:
Number of characters contained in the meta description.

SEO relevance:
Medium

Labeling relevance:
Medium

Important:
Length should not be interpreted as a guaranteed ranking factor.

---

## meta_description_word_count

Category:
On-page SEO

Type:
Integer

Description:
Number of words contained in the meta description.

SEO relevance:
Low to Medium

Labeling relevance:
Low

---

# 5. Heading Features

## h1_count

Category:
On-page SEO

Type:
Integer

Description:
Number of H1 elements detected on the page.

SEO relevance:
High

Labeling relevance:
High

---

## h2_count

Category:
On-page SEO

Type:
Integer

Description:
Number of H2 elements detected on the page.

SEO relevance:
Medium

Labeling relevance:
Medium

---

## h3_count

Category:
On-page SEO

Type:
Integer

Description:
Number of H3 elements detected on the page.

SEO relevance:
Medium

Labeling relevance:
Low to Medium

---

## h4_count

Category:
On-page SEO

Type:
Integer

Description:
Number of H4 elements detected on the page.

SEO relevance:
Low to Medium

Labeling relevance:
Low

---

## h5_count

Category:
On-page SEO

Type:
Integer

Description:
Number of H5 elements detected on the page.

SEO relevance:
Low

Labeling relevance:
Low

---

## h6_count

Category:
On-page SEO

Type:
Integer

Description:
Number of H6 elements detected on the page.

SEO relevance:
Low

Labeling relevance:
Low

---

# 6. Content Features

## word_count

Category:
Content

Type:
Integer

Description:
Number of words extracted from the page content.

SEO relevance:
Medium

Labeling relevance:
Medium

Important:
There is no universal word-count threshold that guarantees SEO quality.

This feature must therefore be interpreted together with other signals.

---

## character_count

Category:
Content

Type:
Integer

Description:
Number of characters contained in the extracted textual content.

SEO relevance:
Low to Medium

Labeling relevance:
Low

---

## unique_word_count

Category:
Content

Type:
Integer

Description:
Number of unique words detected in the extracted content.

SEO relevance:
Low to Medium

Labeling relevance:
Low to Medium

---

## unique_word_ratio

Category:
Content

Type:
Float

Description:
Ratio between unique words and total words.

Formula:

unique_word_count / word_count

SEO relevance:
Experimental

Labeling relevance:
Medium

Important:
This is a Trafiq AI experimental feature and should not be treated as
an official search-engine quality metric.

---

# 7. Image Features

## image_count

Category:
Images

Type:
Integer

Description:
Total number of image elements detected on the page.

SEO relevance:
Medium

Labeling relevance:
Medium

Important:
A page without images is not automatically considered poor.

---

## images_with_alt

Category:
Images

Type:
Integer

Description:
Number of images containing a non-empty alt attribute.

SEO relevance:
Medium

Labeling relevance:
Medium

---

## images_without_alt

Category:
Images

Type:
Integer

Description:
Number of images without a usable alt attribute.

SEO relevance:
Medium

Labeling relevance:
Medium to High

---

## empty_alt_count

Category:
Images

Type:
Integer

Description:
Number of image elements containing an empty alt attribute.

SEO relevance:
Context dependent

Labeling relevance:
Low to Medium

Important:
An empty alt attribute can be intentional for decorative images.

It must not automatically be interpreted as an error.

---

# 8. Link Features

## total_link_count

Category:
Linking

Type:
Integer

Description:
Total number of links detected on the page.

SEO relevance:
Medium

Labeling relevance:
Medium

---

## internal_link_count

Category:
Internal Linking

Type:
Integer

Description:
Number of links pointing to URLs within the same domain.

SEO relevance:
High

Labeling relevance:
High

---

## external_link_count

Category:
External Linking

Type:
Integer

Description:
Number of links pointing to external domains.

SEO relevance:
Low to Medium

Labeling relevance:
Low

---

## nofollow_link_count

Category:
Linking

Type:
Integer

Description:
Number of links containing the nofollow relationship.

SEO relevance:
Context dependent

Labeling relevance:
Low

---

## sponsored_link_count

Category:
Linking

Type:
Integer

Description:
Number of links containing the sponsored relationship.

SEO relevance:
Context dependent

Labeling relevance:
Low

---

## ugc_link_count

Category:
Linking

Type:
Integer

Description:
Number of links containing the UGC relationship.

SEO relevance:
Context dependent

Labeling relevance:
Low

---

# 9. Technical and Performance Features

## response_time_ms

Category:
Performance

Type:
Float

Description:
Time required to receive the HTTP response.

SEO relevance:
Medium

Labeling relevance:
Medium

Important:
HTTP response time is not equivalent to complete page-loading
performance.

---

## redirect_count

Category:
Technical SEO

Type:
Integer

Description:
Number of redirects encountered before reaching the final page.

SEO relevance:
Medium

Labeling relevance:
Medium

---

## status_code

Category:
Technical SEO

Type:
Integer

Description:
HTTP status code returned by the requested page.

Examples:

- 200
- 301
- 302
- 404
- 500

SEO relevance:
High

Labeling relevance:
High

---

# 10. Planned Features

The following features are planned for future versions.

## Technical SEO

- canonical
- robots meta directives
- robots.txt
- sitemap
- HTTPS
- indexability
- redirect chains

## Structured Data

- JSON-LD detection
- Schema.org detection
- structured-data validation

## Performance

- Core Web Vitals
- resource analysis
- page-size analysis
- additional loading metrics

## International SEO

- language
- hreflang

## Site Architecture

- crawl depth
- orphan pages
- duplicate content
- site-wide internal linking
- sitemap coverage

---

# 11. Feature Reliability

Features are classified according to their expected usefulness.

## High

Features that provide strong and relatively direct evidence.

Examples:

- title_exists
- meta_description_exists
- h1_count
- status_code
- internal_link_count

## Medium

Features that can provide useful evidence but require context.

Examples:

- title_length
- word_count
- image_count
- response_time_ms
- redirect_count

## Low

Features that provide limited evidence by themselves.

Examples:

- title_word_count
- character_count
- external_link_count
- h5_count
- h6_count

## Experimental

Features created by Trafiq AI that require empirical validation.

Examples:

- unique_word_ratio

---

# 12. Feature Interpretation Principle

No individual feature should automatically determine the overall
quality of a webpage.

Example:

image_count = 0

does not necessarily mean:

SEO quality = POOR

Instead, the corresponding labeling function may return:

ABSTAIN

when the feature does not provide enough evidence.

---

# 13. Feature-to-Labeling Relationship

The relationship between features and labeling functions is:

Feature
    ↓
Observable signal
    ↓
Labeling function
    ↓
GOOD / AVERAGE / POOR / ABSTAIN

Example:

title_exists = false
    ↓
label_title()
    ↓
POOR

Another example:

image_count = 0
    ↓
label_images()
    ↓
ABSTAIN

---

# 14. Feature Evolution

Features may evolve as the project develops.

When a feature is modified, the following should be documented:

- reason for modification
- previous behavior
- new behavior
- impact on labeling functions
- impact on the generated dataset

Changes affecting feature extraction or labeling rules may require
regenerating part or all of the dataset.

---

# 15. Dataset Reproducibility

The feature specification is part of the dataset-generation
documentation.

A dataset observation should ultimately be traceable to:

- source URL
- crawl result
- extracted features
- labeling-function outputs
- aggregation result
- dataset version

This ensures that model training data can be inspected and reproduced.