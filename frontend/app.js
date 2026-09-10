const API_BASE_URL = "http://127.0.0.1:8000";

const form = document.getElementById("analyze-form");
const urlInput = document.getElementById("url-input");
const analyzeButton = document.getElementById("analyze-button");
const buttonText = document.getElementById("button-text");
const buttonLoader = document.getElementById("button-loader");
const errorMessage = document.getElementById("error-message");

const results = document.getElementById("results");

const crawlQuality = document.getElementById("crawl-quality");
const prediction = document.getElementById("prediction");
const confidence = document.getElementById("confidence");

const probPoor = document.getElementById("prob-poor");
const probAverage = document.getElementById("prob-average");
const probGood = document.getElementById("prob-good");

const barPoor = document.getElementById("bar-poor");
const barAverage = document.getElementById("bar-average");
const barGood = document.getElementById("bar-good");

const featureCount = document.getElementById("feature-count");
const httpStatus = document.getElementById("http-status");
const responseTime = document.getElementById("response-time");
const recommendationCount = document.getElementById(
    "recommendation-count"
);

const recommendationsContainer =
    document.getElementById("recommendations");

const featuresContainer =
    document.getElementById("features");

const domainName =
    document.getElementById("domain-name");


/* =========================================================
   Utility functions
   ========================================================= */

function escapeHTML(value) {
    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


function formatNumber(value) {
    if (value === null || value === undefined) {
        return "—";
    }

    const number = Number(value);

    if (!Number.isFinite(number)) {
        return "—";
    }

    return new Intl.NumberFormat("fr-FR", {
        maximumFractionDigits: 2
    }).format(number);
}


function formatPercentage(value) {
    const number = Number(value);

    if (!Number.isFinite(number)) {
        return "—";
    }

    return `${(number * 100).toFixed(1)} %`;
}


function setLoading(isLoading) {
    if (!analyzeButton) {
        return;
    }

    analyzeButton.disabled = isLoading;

    if (buttonText) {
        buttonText.classList.toggle(
            "hidden",
            isLoading
        );
    }

    if (buttonLoader) {
        buttonLoader.classList.toggle(
            "hidden",
            !isLoading
        );
    }
}


function showError(message) {
    if (!errorMessage) {
        return;
    }

    errorMessage.textContent = message;
    errorMessage.classList.remove("hidden");
}


function hideError() {
    if (!errorMessage) {
        return;
    }

    errorMessage.textContent = "";
    errorMessage.classList.add("hidden");
}


function showResults() {
    if (!results) {
        return;
    }

    results.classList.remove("hidden");
}


function hideResults() {
    if (!results) {
        return;
    }

    results.classList.add("hidden");
}


/* =========================================================
   API
   ========================================================= */

async function checkAPI() {
    try {
        const response = await fetch(
            `${API_BASE_URL}/health`
        );

        if (!response.ok) {
            throw new Error("API indisponible");
        }

        return true;
    } catch (error) {
        return false;
    }
}


async function analyzeURL(url) {
    const response = await fetch(
        `${API_BASE_URL}/analyze`,
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                url: url,
                timeout: 15
            })
        }
    );

    let data;

    try {
        data = await response.json();
    } catch (error) {
        throw new Error(
            "La réponse de l'API n'est pas un JSON valide."
        );
    }

    if (!response.ok) {
        throw new Error(
            data?.detail ||
            data?.message ||
            "L'analyse a échoué."
        );
    }

    return data;
}


/* =========================================================
   Prediction
   ========================================================= */

function renderPrediction(data) {
    const predictedClass =
        data?.prediction || "—";

    const confidenceValue =
        Number(data?.confidence);

    if (prediction) {
        prediction.textContent =
            predictedClass;
    }

    if (confidence) {
        if (Number.isFinite(confidenceValue)) {
            confidence.textContent =
                `${Math.round(confidenceValue * 100)} %`;
        } else {
            confidence.textContent = "—";
        }
    }

    if (crawlQuality) {
        crawlQuality.textContent =
            data?.crawl_quality || "—";

        crawlQuality.className = "badge";

        const quality =
            String(
                data?.crawl_quality || ""
            ).toUpperCase();

        if (quality === "NORMAL") {
            crawlQuality.classList.add(
                "badge-success"
            );
        } else if (quality === "SUSPECT") {
            crawlQuality.classList.add(
                "badge-warning"
            );
        } else if (quality === "FAILED") {
            crawlQuality.classList.add(
                "badge-danger"
            );
        }
    }

    const probabilities =
        data?.class_probabilities || {};

    const poor =
        Number(probabilities.POOR || 0);

    const average =
        Number(probabilities.AVERAGE || 0);

    const good =
        Number(probabilities.GOOD || 0);

    if (probPoor) {
        probPoor.textContent =
            `${(poor * 100).toFixed(1)} %`;
    }

    if (probAverage) {
        probAverage.textContent =
            `${(average * 100).toFixed(1)} %`;
    }

    if (probGood) {
        probGood.textContent =
            `${(good * 100).toFixed(1)} %`;
    }

    if (barPoor) {
        barPoor.style.width =
            `${poor * 100}%`;
    }

    if (barAverage) {
        barAverage.style.width =
            `${average * 100}%`;
    }

    if (barGood) {
        barGood.style.width =
            `${good * 100}%`;
    }
}


/* =========================================================
   Statistics
   ========================================================= */

function renderStats(data) {
    if (featureCount) {
        featureCount.textContent =
            formatNumber(
                data?.feature_count
            );
    }

    if (httpStatus) {
        httpStatus.textContent =
            formatNumber(
                data?.status_code
            );
    }

    if (responseTime) {
        const time =
            Number(
                data?.response_time_ms
            );

        if (Number.isFinite(time)) {
            responseTime.textContent =
                time.toFixed(1);
        } else {
            responseTime.textContent =
                "—";
        }
    }

    if (recommendationCount) {
        recommendationCount.textContent =
            formatNumber(
                data?.recommendation_count
            );
    }

    if (domainName) {
        domainName.textContent =
            data?.domain || "—";
    }
}


/* =========================================================
   Recommendations
   ========================================================= */

function renderRecommendations(data) {
    if (!recommendationsContainer) {
        return;
    }

    const recommendations =
        Array.isArray(
            data?.recommendations
        )
            ? data.recommendations
            : [];

    if (!recommendations.length) {
        recommendationsContainer.innerHTML = `
            <div class="recommendation-empty">
                <strong>Aucune recommandation détectée</strong>
                <span>
                    Le moteur de recommandations n'a identifié
                    aucune action prioritaire pour cette page.
                </span>
            </div>
        `;

        return;
    }

    const severityOrder = {
        HIGH: 0,
        MEDIUM: 1,
        LOW: 2
    };

    const sortedRecommendations =
        [...recommendations].sort(
            (a, b) => {
                const severityA =
                    severityOrder[
                        String(
                            a?.severity || "LOW"
                        ).toUpperCase()
                    ] ?? 99;

                const severityB =
                    severityOrder[
                        String(
                            b?.severity || "LOW"
                        ).toUpperCase()
                    ] ?? 99;

                return severityA - severityB;
            }
        );

    recommendationsContainer.innerHTML =
        sortedRecommendations
            .map(
                (item, index) => {
                    const severity =
                        String(
                            item?.severity ||
                            "LOW"
                        ).toUpperCase();

                    const severityClass =
                        severity.toLowerCase();

                    const title =
                        item?.title ||
                        "Recommandation";

                    const explanation =
                        item?.explanation ||
                        "";

                    const recommendation =
                        item?.recommendation ||
                        "";

                    const feature =
                        item?.feature ||
                        "";

                    return `
                        <article
                            class="
                                recommendation-item
                                severity-${escapeHTML(
                                    severityClass
                                )}
                            "
                        >
                            <div class="recommendation-number">
                                ${index + 1}
                            </div>

                            <div class="recommendation-body">

                                <div class="recommendation-heading">
                                    <h4>
                                        ${escapeHTML(title)}
                                    </h4>

                                    <span
                                        class="
                                            recommendation-severity
                                            severity-${escapeHTML(
                                                severityClass
                                            )}
                                        "
                                    >
                                        ${escapeHTML(severity)}
                                    </span>
                                </div>

                                ${
                                    explanation
                                        ? `
                                            <p class="recommendation-explanation">
                                                ${escapeHTML(
                                                    explanation
                                                )}
                                            </p>
                                        `
                                        : ""
                                }

                                ${
                                    recommendation
                                        ? `
                                            <p class="recommendation-action">
                                                ${escapeHTML(
                                                    recommendation
                                                )}
                                            </p>
                                        `
                                        : ""
                                }

                                ${
                                    feature
                                        ? `
                                            <div class="recommendation-feature">
                                                <span>
                                                    Feature
                                                </span>
                                                <code>
                                                    ${escapeHTML(
                                                        feature
                                                    )}
                                                </code>
                                            </div>
                                        `
                                        : ""
                                }

                            </div>
                        </article>
                    `;
                }
            )
            .join("");
}


/* =========================================================
   SEO Features
   ========================================================= */

function renderFeatureSummary(data) {
    if (!featuresContainer) {
        return;
    }

    const features =
        data?.features;

    if (
        !features ||
        typeof features !== "object"
    ) {
        featuresContainer.innerHTML = `
            <div class="feature-empty">
                <strong>
                    ${escapeHTML(
                        String(
                            data?.feature_count ??
                            0
                        )
                    )} features analysées
                </strong>

                <span>
                    Le moteur SEO a extrait les
                    caractéristiques nécessaires
                    à la prédiction.
                </span>
            </div>
        `;

        return;
    }

    /*
     * Les 40 features utilisées par le modèle.
     * Elles sont regroupées ici uniquement pour
     * améliorer la lisibilité dans l'interface.
     */
    const groups = {
        "Technical SEO": [
            "title_exists",
            "title_length",
            "title_word_count",
            "meta_description_exists",
            "meta_description_length",
            "meta_description_word_count",
            "canonical_exists",
            "robots_meta_exists",
            "viewport_exists",
            "lang_exists"
        ],

        "Content": [
            "h1_count",
            "h2_count",
            "h3_count",
            "h4_count",
            "h5_count",
            "h6_count",
            "heading_total_count",
            "word_count",
            "character_count",
            "unique_word_count",
            "unique_word_ratio"
        ],

        "Images": [
            "image_count",
            "images_with_alt",
            "images_without_alt",
            "images_missing_alt_attribute",
            "empty_alt_count",
            "alt_coverage_ratio"
        ],

        "Links": [
            "total_link_count",
            "internal_link_count",
            "external_link_count",
            "nofollow_link_count",
            "sponsored_link_count",
            "ugc_link_count",
            "internal_link_ratio",
            "external_unique_domain_count"
        ],

        "Structured Data & Conversion": [
            "jsonld_count",
            "schema_org_count",
            "cta_count",
            "phone_count",
            "email_count"
        ]
    };


    const featureLabels = {
        title_exists:
            "Title présent",

        title_length:
            "Longueur du title",

        title_word_count:
            "Mots du title",

        meta_description_exists:
            "Meta description présente",

        meta_description_length:
            "Longueur de la meta description",

        meta_description_word_count:
            "Mots de la meta description",

        h1_count:
            "Nombre de H1",

        h2_count:
            "Nombre de H2",

        h3_count:
            "Nombre de H3",

        h4_count:
            "Nombre de H4",

        h5_count:
            "Nombre de H5",

        h6_count:
            "Nombre de H6",

        heading_total_count:
            "Total des headings",

        word_count:
            "Nombre de mots",

        character_count:
            "Nombre de caractères",

        unique_word_count:
            "Mots uniques",

        unique_word_ratio:
            "Ratio de mots uniques",

        image_count:
            "Nombre d'images",

        images_with_alt:
            "Images avec ALT",

        images_without_alt:
            "Images sans ALT",

        images_missing_alt_attribute:
            "Images sans attribut ALT",

        empty_alt_count:
            "ALT vides",

        alt_coverage_ratio:
            "Couverture ALT",

        total_link_count:
            "Total des liens",

        internal_link_count:
            "Liens internes",

        external_link_count:
            "Liens externes",

        nofollow_link_count:
            "Liens nofollow",

        sponsored_link_count:
            "Liens sponsored",

        ugc_link_count:
            "Liens UGC",

        internal_link_ratio:
            "Ratio de liens internes",

        external_unique_domain_count:
            "Domaines externes uniques",

        canonical_exists:
            "Canonical présente",

        robots_meta_exists:
            "Meta robots présente",

        viewport_exists:
            "Viewport présent",

        lang_exists:
            "Langue HTML présente",

        jsonld_count:
            "Blocs JSON-LD",

        schema_org_count:
            "Éléments Schema.org",

        cta_count:
            "CTA détectés",

        phone_count:
            "Téléphones détectés",

        email_count:
            "Emails détectés"
    };


    function formatFeatureValue(
        feature,
        value
    ) {
        if (
            value === null ||
            value === undefined
        ) {
            return "—";
        }

        if (
            typeof value === "boolean"
        ) {
            return value
                ? "Oui"
                : "Non";
        }

        if (
            feature ===
                "alt_coverage_ratio" ||
            feature ===
                "internal_link_ratio" ||
            feature ===
                "unique_word_ratio"
        ) {
            return formatPercentage(
                value
            );
        }

        if (
            typeof value === "number"
        ) {
            return formatNumber(
                value
            );
        }

        return String(value);
    }


    function featureIcon(value) {
        if (
            typeof value !== "boolean"
        ) {
            return "";
        }

        return value
            ? "✓"
            : "—";
    }


    let html = "";


    Object.entries(groups).forEach(
        ([groupName, featureNames]) => {
            const availableFeatures =
                featureNames.filter(
                    feature =>
                        Object.prototype.hasOwnProperty.call(
                            features,
                            feature
                        )
                );

            if (
                !availableFeatures.length
            ) {
                return;
            }


            html += `
                <section class="feature-group">

                    <div class="feature-group-header">

                        <div>
                            <span class="feature-group-title">
                                ${escapeHTML(
                                    groupName
                                )}
                            </span>
                        </div>

                        <span class="feature-group-count">
                            ${availableFeatures.length}
                        </span>

                    </div>

                    <div class="feature-group-grid">
            `;


            availableFeatures.forEach(
                feature => {
                    const value =
                        features[feature];

                    const label =
                        featureLabels[feature] ||
                        feature;

                    const formattedValue =
                        formatFeatureValue(
                            feature,
                            value
                        );

                    const icon =
                        featureIcon(value);


                    html += `
                        <div class="feature-item">

                            <div class="feature-item-main">

                                <div class="feature-item-label">
                                    ${escapeHTML(
                                        label
                                    )}
                                </div>

                                <div class="feature-item-value">

                                    ${
                                        icon
                                            ? `
                                                <span
                                                    class="
                                                        feature-status
                                                        ${
                                                            value
                                                                ? "is-positive"
                                                                : "is-neutral"
                                                        }
                                                    "
                                                >
                                                    ${icon}
                                                </span>
                                            `
                                            : ""
                                    }

                                    <span>
                                        ${escapeHTML(
                                            formattedValue
                                        )}
                                    </span>

                                </div>

                            </div>

                            <code class="feature-item-key">
                                ${escapeHTML(
                                    feature
                                )}
                            </code>

                        </div>
                    `;
                }
            );


            html += `
                    </div>
                </section>
            `;
        }
    );


    /*
     * Vérification simple :
     * l'API annonce normalement 40 features.
     */
    const actualFeatureCount =
        Object.keys(features).length;


    if (!html) {
        html = `
            <div class="feature-empty">
                <strong>
                    Aucune feature disponible
                </strong>
            </div>
        `;
    }


    featuresContainer.innerHTML =
        html;


    /*
     * Petit indicateur facultatif dans la console
     * pour vérifier que les 40 features sont bien reçues.
     */
    console.debug(
        `Trafiq AI : ${actualFeatureCount} features reçues.`
    );
}


/* =========================================================
   Complete result rendering
   ========================================================= */

function renderResults(data) {
    renderPrediction(data);
    renderStats(data);
    renderRecommendations(data);
    renderFeatureSummary(data);

    showResults();
}


/* =========================================================
   Form
   ========================================================= */

if (form) {
    form.addEventListener(
        "submit",
        async event => {
            event.preventDefault();

            hideError();

            const url =
                urlInput?.value.trim();

            if (!url) {
                showError(
                    "Veuillez saisir une URL."
                );

                return;
            }


            setLoading(true);


            try {
                const data =
                    await analyzeURL(url);

                if (
                    !data ||
                    typeof data !== "object"
                ) {
                    throw new Error(
                        "Réponse invalide de l'API."
                    );
                }


                /*
                 * Une analyse FAILED peut être renvoyée
                 * avec un HTTP 200 par l'API.
                 */
                if (
                    data.success === false
                ) {
                    throw new Error(
                        data.message ||
                        (
                            Array.isArray(
                                data.errors
                            )
                                ? data.errors.join(
                                    " "
                                )
                                : "L'analyse n'a pas pu être effectuée."
                        )
                    );
                }


                renderResults(data);


                /*
                 * Après une analyse, on remonte
                 * automatiquement vers les résultats.
                 */
                if (results) {
                    results.scrollIntoView({
                        behavior: "smooth",
                        block: "start"
                    });
                }

            } catch (error) {
                console.error(
                    "Trafiq AI analysis error:",
                    error
                );

                showError(
                    error?.message ||
                    "Une erreur est survenue pendant l'analyse."
                );

            } finally {
                setLoading(false);
            }
        }
    );
}


/* =========================================================
   Initial API status
   ========================================================= */

async function initialize() {
    const apiAvailable =
        await checkAPI();

    const status =
        document.querySelector(
            ".status"
        );

    const statusDot =
        document.querySelector(
            ".status-dot"
        );


    if (status && statusDot) {
        if (apiAvailable) {
            statusDot.classList.add(
                "online"
            );

            status.innerHTML = `
                <span class="status-dot online"></span>
                API disponible
            `;
        } else {
            statusDot.classList.remove(
                "online"
            );

            status.innerHTML = `
                <span class="status-dot offline"></span>
                API indisponible
            `;
        }
    }
}


initialize();