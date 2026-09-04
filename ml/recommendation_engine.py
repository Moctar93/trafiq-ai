from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import json
import math

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Recommendation:
    """One explainable SEO recommendation."""

    category: str
    severity: str
    feature: str
    observed_value: Any
    threshold: Any
    title: str
    recommendation: str
    explanation: str


def _is_missing(value: Any) -> bool:
    """Return True for NaN/None values."""
    if value is None:
        return True

    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False


def _as_float(value: Any, default: float | None = None) -> float | None:
    """Safely convert a value to float."""
    if _is_missing(value):
        return default

    try:
        result = float(value)

        if not math.isfinite(result):
            return default

        return result
    except (TypeError, ValueError):
        return default


def _as_bool(value: Any, default: bool = False) -> bool:
    """Safely interpret common boolean representations."""
    if _is_missing(value):
        return default

    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)):
        return bool(value)

    text = str(value).strip().lower()

    if text in {"true", "1", "yes", "y", "oui"}:
        return True

    if text in {"false", "0", "no", "n", "non"}:
        return False

    return default


def _add(
    recommendations: list[Recommendation],
    *,
    category: str,
    severity: str,
    feature: str,
    observed_value: Any,
    threshold: Any,
    title: str,
    recommendation: str,
    explanation: str,
) -> None:
    """Append a recommendation."""
    recommendations.append(
        Recommendation(
            category=category,
            severity=severity,
            feature=feature,
            observed_value=observed_value,
            threshold=threshold,
            title=title,
            recommendation=recommendation,
            explanation=explanation,
        )
    )


def generate_recommendations(
    features: dict[str, Any],
) -> list[Recommendation]:
    """
    Generate deterministic, explainable SEO recommendations.

    This V1 engine intentionally uses explicit rules rather than ML or GPT.
    The rules are designed for transparency and easy demonstration.
    """

    recommendations: list[Recommendation] = []

    # ------------------------------------------------------------------
    # META / TECHNICAL SEO
    # ------------------------------------------------------------------

    if not _as_bool(features.get("title_exists")):
        _add(
            recommendations,
            category="technical_seo",
            severity="HIGH",
            feature="title_exists",
            observed_value=False,
            threshold=True,
            title="Ajouter une balise title",
            recommendation=(
                "Ajouter une balise <title> unique, descriptive et "
                "pertinente pour la page."
            ),
            explanation=(
                "La page ne possède pas de balise title détectée."
            ),
        )
    else:
        title_length = _as_float(features.get("title_length"))

        if title_length is not None and title_length < 30:
            _add(
                recommendations,
                category="technical_seo",
                severity="MEDIUM",
                feature="title_length",
                observed_value=title_length,
                threshold=">= 30",
                title="Enrichir le title",
                recommendation=(
                    "Rendre le title plus descriptif en intégrant "
                    "l'intention ou le sujet principal de la page."
                ),
                explanation=(
                    f"Le title contient environ {title_length:.0f} "
                    "caractères, ce qui est court pour décrire "
                    "précisément la page."
                ),
            )

        if title_length is not None and title_length > 65:
            _add(
                recommendations,
                category="technical_seo",
                severity="LOW",
                feature="title_length",
                observed_value=title_length,
                threshold="<= 65",
                title="Raccourcir le title",
                recommendation=(
                    "Réduire le title pour conserver l'information "
                    "essentielle dans un intitulé plus concis."
                ),
                explanation=(
                    f"Le title contient environ {title_length:.0f} "
                    "caractères et peut être trop long."
                ),
            )

    if not _as_bool(features.get("meta_description_exists")):
        _add(
            recommendations,
            category="technical_seo",
            severity="HIGH",
            feature="meta_description_exists",
            observed_value=False,
            threshold=True,
            title="Ajouter une meta description",
            recommendation=(
                "Ajouter une meta description unique résumant le contenu "
                "et la valeur de la page."
            ),
            explanation=(
                "Aucune meta description n'a été détectée."
            ),
        )
    else:
        meta_length = _as_float(
            features.get("meta_description_length")
        )

        if meta_length is not None and meta_length < 70:
            _add(
                recommendations,
                category="technical_seo",
                severity="MEDIUM",
                feature="meta_description_length",
                observed_value=meta_length,
                threshold=">= 70",
                title="Enrichir la meta description",
                recommendation=(
                    "Développer la meta description pour mieux présenter "
                    "le contenu et la proposition de valeur."
                ),
                explanation=(
                    f"La meta description contient environ "
                    f"{meta_length:.0f} caractères."
                ),
            )

    if not _as_bool(features.get("canonical_exists")):
        _add(
            recommendations,
            category="technical_seo",
            severity="MEDIUM",
            feature="canonical_exists",
            observed_value=False,
            threshold=True,
            title="Déclarer une URL canonique",
            recommendation=(
                "Ajouter une balise canonical cohérente lorsque la page "
                "peut être accessible via plusieurs URLs."
            ),
            explanation=(
                "Aucune URL canonique n'a été détectée."
            ),
        )

    if not _as_bool(features.get("robots_meta_exists")):
        _add(
            recommendations,
            category="technical_seo",
            severity="LOW",
            feature="robots_meta_exists",
            observed_value=False,
            threshold=True,
            title="Vérifier la directive robots",
            recommendation=(
                "Vérifier les directives robots et s'assurer qu'elles "
                "n'empêchent pas l'indexation attendue."
            ),
            explanation=(
                "Aucune balise meta robots n'a été détectée."
            ),
        )

    if not _as_bool(features.get("lang_exists")):
        _add(
            recommendations,
            category="technical_seo",
            severity="LOW",
            feature="lang_exists",
            observed_value=False,
            threshold=True,
            title="Déclarer la langue du document",
            recommendation=(
                "Ajouter l'attribut lang sur l'élément <html>."
            ),
            explanation=(
                "La langue du document n'a pas été détectée."
            ),
        )

    # ------------------------------------------------------------------
    # CONTENT
    # ------------------------------------------------------------------

    word_count = _as_float(features.get("word_count"))

    if word_count is not None and word_count < 500:
        _add(
            recommendations,
            category="content",
            severity="MEDIUM",
            feature="word_count",
            observed_value=word_count,
            threshold=">= 500",
            title="Enrichir le contenu",
            recommendation=(
                "Enrichir les pages stratégiques avec du contenu utile, "
                "spécifique à l'intention de recherche et non redondant."
            ),
            explanation=(
                f"La page contient environ {word_count:.0f} mots. "
                "Le volume seul ne détermine pas la qualité SEO, mais "
                "un contenu très court peut limiter la capacité à couvrir "
                "le sujet."
            ),
        )

    heading_total = _as_float(features.get("heading_total_count"))

    if heading_total is not None and word_count is not None:
        if word_count >= 500 and heading_total < 3:
            _add(
                recommendations,
                category="content",
                severity="LOW",
                feature="heading_total_count",
                observed_value=heading_total,
                threshold=">= 3",
                title="Structurer davantage le contenu",
                recommendation=(
                    "Ajouter des intertitres pertinents pour organiser "
                    "les sections importantes de la page."
                ),
                explanation=(
                    "Le contenu est relativement développé mais contient "
                    "peu de titres de section."
                ),
            )

    h1_count = _as_float(features.get("h1_count"))

    if h1_count is not None and h1_count == 0:
        _add(
            recommendations,
            category="content",
            severity="HIGH",
            feature="h1_count",
            observed_value=h1_count,
            threshold=">= 1",
            title="Ajouter un H1",
            recommendation=(
                "Ajouter un titre H1 clair correspondant au sujet principal "
                "de la page."
            ),
            explanation="Aucun H1 n'a été détecté."
        )

    if h1_count is not None and h1_count > 1:
        _add(
            recommendations,
            category="content",
            severity="LOW",
            feature="h1_count",
            observed_value=h1_count,
            threshold="= 1",
            title="Rationaliser les H1",
            recommendation=(
                "Vérifier la hiérarchie éditoriale et conserver un H1 "
                "principal clairement identifiable."
            ),
            explanation=(
                f"{h1_count:.0f} balises H1 ont été détectées."
            ),
        )

    # ------------------------------------------------------------------
    # IMAGES
    # ------------------------------------------------------------------

    image_count = _as_float(features.get("image_count"))
    alt_coverage = _as_float(features.get("alt_coverage_ratio"))

    if image_count is not None and image_count > 0:
        if alt_coverage is not None and alt_coverage < 0.70:
            _add(
                recommendations,
                category="images",
                severity="MEDIUM",
                feature="alt_coverage_ratio",
                observed_value=round(alt_coverage, 3),
                threshold=">= 0.70",
                title="Améliorer les attributs ALT",
                recommendation=(
                    "Ajouter des attributs ALT descriptifs aux images "
                    "pertinentes et éviter les ALT vides lorsqu'ils "
                    "ne sont pas justifiés."
                ),
                explanation=(
                    f"La couverture ALT est d'environ "
                    f"{alt_coverage:.1%}."
                ),
            )

        images_without_alt = _as_float(
            features.get("images_without_alt")
        )

        if images_without_alt is not None and images_without_alt > 0:
            _add(
                recommendations,
                category="images",
                severity="MEDIUM",
                feature="images_without_alt",
                observed_value=images_without_alt,
                threshold="= 0",
                title="Corriger les images sans ALT",
                recommendation=(
                    "Identifier les images importantes sans attribut ALT "
                    "et leur ajouter un texte alternatif pertinent."
                ),
                explanation=(
                    f"{images_without_alt:.0f} image(s) sans ALT "
                    "ont été détectées."
                ),
            )

    # ------------------------------------------------------------------
    # INTERNAL LINKING
    # ------------------------------------------------------------------

    internal_ratio = _as_float(
        features.get("internal_link_ratio")
    )

    if internal_ratio is not None and internal_ratio < 0.70:
        _add(
            recommendations,
            category="internal_linking",
            severity="MEDIUM",
            feature="internal_link_ratio",
            observed_value=round(internal_ratio, 3),
            threshold=">= 0.70",
            title="Renforcer le maillage interne",
            recommendation=(
                "Ajouter des liens internes contextuels entre les pages "
                "importantes et les contenus complémentaires."
            ),
            explanation=(
                f"Le ratio de liens internes est d'environ "
                f"{internal_ratio:.1%}."
            ),
        )

    internal_links = _as_float(
        features.get("internal_link_count")
    )

    if internal_links is not None and internal_links < 10:
        _add(
            recommendations,
            category="internal_linking",
            severity="LOW",
            feature="internal_link_count",
            observed_value=internal_links,
            threshold=">= 10",
            title="Augmenter les liens internes",
            recommendation=(
                "Ajouter davantage de liens internes vers les pages "
                "stratégiques, lorsque cela apporte une valeur "
                "navigationnelle ou sémantique."
            ),
            explanation=(
                f"{internal_links:.0f} liens internes ont été détectés."
            ),
        )

    # ------------------------------------------------------------------
    # EXTERNAL LINKING / AUTHORITY
    # ------------------------------------------------------------------

    external_domains = _as_float(
        features.get("external_unique_domain_count")
    )

    if external_domains is not None and external_domains < 3:
        _add(
            recommendations,
            category="authority",
            severity="LOW",
            feature="external_unique_domain_count",
            observed_value=external_domains,
            threshold=">= 3",
            title="Développer l'écosystème externe",
            recommendation=(
                "Évaluer les opportunités de visibilité externe et de "
                "liens provenant de domaines pertinents et crédibles."
            ),
            explanation=(
                f"Seulement {external_domains:.0f} domaine(s) externe(s) "
                "unique(s) ont été détectés dans les liens de la page."
            ),
        )

    # ------------------------------------------------------------------
    # BUSINESS / CONVERSION SIGNALS
    # ------------------------------------------------------------------

    cta_count = _as_float(features.get("cta_count"))

    if cta_count is not None and cta_count == 0:
        _add(
            recommendations,
            category="conversion",
            severity="MEDIUM",
            feature="cta_count",
            observed_value=cta_count,
            threshold=">= 1",
            title="Ajouter un appel à l'action",
            recommendation=(
                "Ajouter un CTA clair et visible adapté à l'objectif "
                "de la page."
            ),
            explanation=(
                "Aucun appel à l'action détectable n'a été identifié."
            ),
        )

    phone_count = _as_float(features.get("phone_count"))
    email_count = _as_float(features.get("email_count"))

    if (
        phone_count is not None
        and email_count is not None
        and phone_count == 0
        and email_count == 0
    ):
        _add(
            recommendations,
            category="conversion",
            severity="LOW",
            feature="phone_count,email_count",
            observed_value={
                "phone_count": phone_count,
                "email_count": email_count,
            },
            threshold="phone >= 1 OR email >= 1",
            title="Faciliter le contact",
            recommendation=(
                "Rendre au moins un moyen de contact identifiable sur "
                "les pages où cela est pertinent."
            ),
            explanation=(
                "Aucun numéro de téléphone ni adresse email détectable "
                "n'a été trouvé."
            ),
        )

    # ------------------------------------------------------------------
    # LINK HYGIENE
    # ------------------------------------------------------------------

    nofollow_count = _as_float(
        features.get("nofollow_link_count")
    )
    external_link_count = _as_float(
        features.get("external_link_count")
    )

    if (
        nofollow_count is not None
        and external_link_count is not None
        and external_link_count > 0
        and nofollow_count > external_link_count * 0.8
    ):
        _add(
            recommendations,
            category="links",
            severity="LOW",
            feature="nofollow_link_count",
            observed_value=nofollow_count,
            threshold="context-dependent",
            title="Vérifier les liens nofollow",
            recommendation=(
                "Auditer les liens externes nofollow afin de vérifier "
                "qu'ils correspondent réellement à la stratégie de "
                "liens du site."
            ),
            explanation=(
                "Une part importante des liens semble être marquée "
                "nofollow. Ce signal nécessite une vérification "
                "contextuelle plutôt qu'une correction automatique."
            ),
        )

    return recommendations


def recommendations_to_dataframe(
    recommendations: list[Recommendation],
) -> pd.DataFrame:
    """Convert recommendations to a DataFrame."""
    columns = [
        "category",
        "severity",
        "feature",
        "observed_value",
        "threshold",
        "title",
        "recommendation",
        "explanation",
    ]

    rows = [asdict(item) for item in recommendations]

    return pd.DataFrame(rows, columns=columns)


def recommendations_to_dicts(
    recommendations: list[Recommendation],
) -> list[dict[str, Any]]:
    """Convert recommendations to JSON-serializable dictionaries."""
    return [asdict(item) for item in recommendations]


def load_features_from_csv_row(
    csv_path: str | Path,
    row_index: int = 0,
) -> dict[str, Any]:
    """Load one row from a training/feature CSV."""
    path = Path(csv_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Fichier introuvable : {path}"
        )

    df = pd.read_csv(path)

    if df.empty:
        raise ValueError(
            f"Le fichier est vide : {path}"
        )

    if row_index < 0 or row_index >= len(df):
        raise IndexError(
            f"row_index={row_index} invalide pour {len(df)} ligne(s)."
        )

    return df.iloc[row_index].to_dict()


def save_recommendations_json(
    recommendations: list[Recommendation],
    output_path: str | Path,
) -> None:
    """Save recommendations to a JSON file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "recommendation_count": len(recommendations),
        "recommendations": recommendations_to_dicts(
            recommendations
        ),
    }

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            payload,
            file,
            indent=2,
            ensure_ascii=False,
        )


def main() -> None:
    print("=" * 70)
    print("RECOMMENDATION ENGINE V1")
    print("=" * 70)

    dataset_path = (
        BASE_DIR
        / "data"
        / "processed"
        / "seo_training_dataset_v3.csv"
    )

    output_csv = (
        BASE_DIR
        / "data"
        / "models"
        / "recommendations_v1_demo.csv"
    )

    output_json = (
        BASE_DIR
        / "data"
        / "models"
        / "recommendations_v1_demo.json"
    )

    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Dataset introuvable : {dataset_path}"
        )

    df = pd.read_csv(dataset_path)

    if df.empty:
        raise ValueError("Le dataset est vide.")

    print(f"\nDataset : {dataset_path}")
    print(f"Pages disponibles : {len(df)}")

    # Demo all reviewed pages.
    all_recommendations: list[dict[str, Any]] = []

    for index, row in df.iterrows():
        features = row.to_dict()
        recommendations = generate_recommendations(
            features
        )

        for recommendation in recommendations:
            item = asdict(recommendation)
            item["url"] = features.get("url")
            item["domain"] = features.get("domain")
            item["consensus_label"] = features.get(
                "consensus_label"
            )
            all_recommendations.append(item)

    result_df = pd.DataFrame(all_recommendations)

    if result_df.empty:
        print("\nAucune recommandation déclenchée.")
    else:
        # Put identifying columns first.
        preferred_order = [
            "url",
            "domain",
            "consensus_label",
            "category",
            "severity",
            "feature",
            "observed_value",
            "threshold",
            "title",
            "recommendation",
            "explanation",
        ]

        result_df = result_df[
            [
                column
                for column in preferred_order
                if column in result_df.columns
            ]
        ]

        result_df.to_csv(
            output_csv,
            index=False,
            encoding="utf-8",
        )

        result_df.to_json(
            output_json,
            orient="records",
            force_ascii=False,
            indent=2,
        )

        print(
            f"\nRecommandations générées : "
            f"{len(result_df)}"
        )

        print("\nPar sévérité :")
        print(
            result_df["severity"]
            .value_counts()
            .to_string()
        )

        print("\nPar catégorie :")
        print(
            result_df["category"]
            .value_counts()
            .to_string()
        )

        print("\nExemples :")
        print(
            result_df.head(15).to_string(index=False)
        )

    print(f"\nCSV : {output_csv}")
    print(f"JSON : {output_json}")

    print("\n" + "=" * 70)
    print("RECOMMENDATION ENGINE V1 TERMINÉ")
    print("=" * 70)


if __name__ == "__main__":
    main()
