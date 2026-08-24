from crawler.collector import SEOCollector


CALIBRATION_URLS = {
    # ==========================================================
    # SITES QUE MOCTAR A DEJA MODIFIES
    # Classe réelle inconnue
    # ==========================================================
    "known_edited": [
        "https://essence-resilience.coach/",
        "https://jespomi.com/",
        "https://trafiq.fr/",
        "https://nkongsambapeguanto.ltd/",
        "https://depannage-rideaux-metalliques.fr/",
        "https://cabinet-3c.com/",
        "https://if-ca.fr/",
    ],

    # ==========================================================
    # CANDIDATS PAUVRES
    # Groupe expérimental, pas ground truth
    # ==========================================================
    "poor_candidate": [
        "https://ada13.org/",
        "https://toulemondencuisine.wordpress.com/",
        "https://jeanleptitplombier.com/",
        "https://a-un-clic-de-vous.fr/site-vitrine/trelaze/49800",
        "https://arret-net.fr/",
    ],

    # ==========================================================
    # CANDIDATS INTERMEDIAIRES
    # ==========================================================
    "intermediate_candidate": [
        "https://lageneraledetheatre.com/",
        "https://l-artisanat-a-la-francaise.fr/",
    ],

    # ==========================================================
    # CANDIDAT RICHE
    # ==========================================================
    "rich_candidate": [
        "https://abondance.com/",
    ],

    # ==========================================================
    # CAS TECHNIQUE / ATYPIQUE
    # ==========================================================
    "special_case": [
        "https://ucetranger.org/",
    ],

    # ==========================================================
    # E-COMMERCE RICHE
    # Ces sites servent à diversifier les architectures
    # e-commerce. Ils ne sont PAS automatiquement GOOD.
    # ==========================================================
    "ecommerce_rich_candidate": [
        "https://www.decathlon.fr/",
        "https://www.leroymerlin.fr/",
        "https://www.cdiscount.com/",
        "https://www.laredoute.fr/",
        "https://www.castorama.fr/",
        "https://www.veepee.fr/",
        "https://www.maisonsdumonde.com/",
        "https://www.showroomprive.com/",
        "https://www.gammvert.fr/",
    ],

    # ==========================================================
    # CONTENU / INFORMATION
    # ==========================================================
    "content_rich_candidate": [
        "https://www.service-public.fr/",
        "https://www.france24.com/fr/",
        "https://www.lemonde.fr/",
    ],

    # ==========================================================
    # GROS E-COMMERCE DEJA TESTES MAIS QUI PEUVENT REPONDRE 403
    # On les conserve pour documenter leur comportement.
    # ==========================================================
    "independent_rich": [
        "https://www.fnac.com/",
        "https://www.manomano.fr/",
    ],

    # ==========================================================
    # DOCUMENTATION
    # ==========================================================
    "documentation": [
        "https://developers.google.com/",
    ],
}


def main():
    collector = SEOCollector()

    print(
        "\n=== TRAFIQ AI — EXTENDED CALIBRATION COLLECTION ==="
    )

    global_summary = {
        "total": 0,
        "success": 0,
        "failed": 0,
        "duplicates": 0,
        "stored": 0,
    }

    for group, urls in CALIBRATION_URLS.items():

        print(
            f"\n=== GROUP: {group} ==="
        )

        summary = collector.collect(
            urls,
            calibration_group=group,
        )

        for key in global_summary:
            global_summary[key] += summary[key]

    print(
        "\n=== GLOBAL COLLECTION SUMMARY ==="
    )

    for key, value in global_summary.items():
        print(
            f"{key}: {value}"
        )


if __name__ == "__main__":
    main()