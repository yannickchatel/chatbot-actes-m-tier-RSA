# app.py
# -*- coding: utf-8 -*-

import streamlit as st
import unicodedata
import re

from data_actes_metier import ACTES_METIER


# ------------------------------------------------------------
# OUTILS TEXTE
# ------------------------------------------------------------

def normaliser_texte(texte: str) -> str:
    """
    Met le texte en minuscules, enlève les accents et les caractères spéciaux,
    pour faciliter la détection des mots-clés.
    """
    if not texte:
        return ""
    texte = texte.lower()
    texte = unicodedata.normalize("NFD", texte).encode("ascii", "ignore").decode("utf-8")
    texte = re.sub(r"[^a-z0-9\s']", " ", texte)
    texte = re.sub(r"\s+", " ", texte).strip()
    return texte


def calculer_score(texte_norm: str, acte: dict) -> int:
    """
    Score = nombre de mots-clés de l'acte trouvés dans le texte normalisé.
    """
    score = 0
    for mot in acte.get("mots_cles", []):
        mot_norm = normaliser_texte(mot)
        if mot_norm and mot_norm in texte_norm:
            score += 1
    return score


# ------------------------------------------------------------
# ANALYSE DU COMPTE RENDU
# ------------------------------------------------------------

def analyser_cr(texte_cr: str, seuil: int = 1):
    """
    Analyse le compte rendu :
    - calcule un score par acte métier en fonction des mots-clés
    - applique quelques règles de renfort (MDPH, mobilité…)
    - renvoie la liste des actes détectés triés par score décroissant
    """
    texte_norm = normaliser_texte(texte_cr)
    detectes = []

    # 1) Analyse standard par mots-clés
    for acte in ACTES_METIER:
        score = calculer_score(texte_norm, acte)
        if score >= seuil:
            item = acte.copy()
            item["score"] = score
            detectes.append(item)

    # 2) Petites règles de renfort (au cas où les mots-clés ne suffisent pas)

    # SANTÉ / MDPH : si "mdph" apparaît, on s'assure de proposer les actes MDPH
    if "mdph"


if __name__ == "__main__":
    main()
