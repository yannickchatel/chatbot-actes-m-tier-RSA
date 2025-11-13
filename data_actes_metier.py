# data_actes_metier.py
# -*- coding: utf-8 -*-

ACTES_METIER = [
    # =========================
    # EXEMPLES D'ACTES METIER
    # (tu pourras en ajouter autant que tu veux)
    # =========================

    {
        "code": "INFO_CONSEIL_EMPLOI",
        "intitule": "Info et conseil emploi",
        "categorie": "Accès à l'emploi",
        "type": "Info et conseil",
        "description": (
            "Le référent délivre des informations et/ou conseils concernant la recherche d'emploi. "
            "Acte métier à mobiliser également lorsque le référent est uniquement dans l’écoute."
        ),
        "mots_cles": [
            "information emploi",
            "info emploi",
            "recherche d'emploi",
            "conseil emploi",
            "parlé travail",
            "échangé sur le travail",
            "parlé de son projet professionnel",
        ],
        "commentaire_attendu": "Préciser dans le commentaire de l'offre l'information ou le conseil donné."
    },

    {
        "code": "APPUI_RECHERCHE_EMPLOI",
        "intitule": "Appui à la recherche d’emploi",
        "categorie": "Accès à l'emploi",
        "type": "Appui",
        "description": (
            "Le référent aide concrètement (fait avec) la personne accompagnée dans l'entrée et le maintien en emploi : "
            "CV, lettre de motivation, préparation d'entretien, prospection d'entreprise, inscriptions sur des sites d'emploi..."
        ),
        "mots_cles": [
            "cv",
            "curriculum vitae",
            "lettre de motivation",
            "candidature",
            "postuler",
            "prospection entreprise",
            "techniques de recherche d'emploi",
            "tre",
            "simulation entretien",
            "entretien d'embauche",
            "profil sur site emploi",
            "inscription site emploi",
        ],
        "commentaire_attendu": "Préciser le type d'appui réalisé (CV, lettre, TRE, prospection…)."
    },

    {
        "code": "APPUI_POLE_EMPLOI",
        "intitule": "Appui inscription/actualisation Pôle Emploi",
        "categorie": "Accès à l'emploi",
        "type": "Appui",
        "description": (
            "Le référent aide concrètement (fait avec) la personne accompagnée à s'inscrire ou s'actualiser "
            "à Pôle Emploi / France Travail."
        ),
        "mots_cles": [
            "inscription pole emploi",
            "inscrire à pole emploi",
            "inscription france travail",
            "actualisation pole emploi",
            "actualiser pole emploi",
            "actualiser sa situation",
            "mise à jour pole emploi",
        ],
        "commentaire_attendu": "Préciser dans le commentaire de l'offre la nature de l'aide (inscription ou actualisation)."
    },

    {
        "code": "AIDE_FINANCIERE_FSL",
        "intitule": "Aide financière FSL",
        "categorie": "Logement",
        "type": "Aide financière",
        "description": (
            "Le référent propose à la personne accompagnée et sollicite le Fonds de Solidarité Logement (FSL) "
            "pour une aide au maintien ou à l'accès au logement."
        ),
        "mots_cles": [
            "fsl",
            "fonds de solidarité logement",
            "dettes de loyer",
            "impayés de loyer",
            "impayés de charges",
            "aide au maintien dans le logement",
            "aide à l'accès au logement",
            "caution",
        ],
        "commentaire_attendu": "Préciser le type de demande FSL (accès, maintien, type de dette…)."
    },

    {
        "code": "APPUI_LOGEMENT",
        "intitule": "Appui logement",
        "categorie": "Logement",
        "type": "Appui",
        "description": (
            "Le référent aide concrètement (fait avec) la personne accompagnée dans ses démarches de logement "
            "(Demande de logement 37, Action Logement, bailleurs sociaux et privés, etc.)."
        ),
        "mots_cles": [
            "demande de logement",
            "demande de logement 37",
            "action logement",
            "bailleur social",
            "bailleur privé",
            "recherche de logement",
            "dossier logement",
        ],
        "commentaire_attendu": "Préciser les démarches réalisées (Demande logement 37, contact bailleur, etc.)."
    },

    {
        "code": "APPUI_SANTE",
        "intitule": "Appui santé",
        "categorie": "Santé",
        "type": "Appui",
        "description": (
            "Le référent aide concrètement (fait avec) la personne accompagnée dans ses démarches de santé "
            "(complémentaire santé solidaire, prise de rendez-vous, etc.)."
        ),
        "mots_cles": [
            "complémentaire santé solidaire",
            "css",
            "prise de rendez-vous médical",
            "rendez vous médecin",
            "démarches de santé",
            "dossier santé",
        ],
        "commentaire_attendu": "Préciser la nature des démarches de santé accompagnées."
    },

    # 👉 Ensuite tu pourras ajouter ici tous les autres actes du livret CD37,
    # en copiant le même format de dictionnaire Python.
]
