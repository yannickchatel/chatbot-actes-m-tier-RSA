# app.py
# -*- coding: utf-8 -*-

import streamlit as st
import unicodedata
import re

from data_actes_metier import ACTES_METIER


def normaliser_texte(texte: str) -> str:
    """Met le texte en minuscules, enlève les accents et les caractères spéciaux."""
    texte = texte.lower()
    texte = unicodedata.normalize("NFD", texte).encode("ascii", "ignore").decode("utf-8")
    texte = re.sub(r"[^a-z0-9\s']", " ", texte)
    texte = re.sub(r"\s+", " ", texte).strip()
    return texte


def calculer_score(texte_norm: str, acte: dict) -> int:
    """Score = nombre de mots-clés de l'acte trouvés dans le texte."""
    score = 0
    for mot in acte.get("mots_cles", []):
        mot_norm = normaliser_texte(mot)
        if mot_norm and mot_norm in texte_norm:
            score += 1
    return score


def analyser_cr(texte_cr: str):
    """Retourne la liste des actes métiers détectés dans le CR."""
    texte_norm = normaliser_texte(texte_cr)
    resultats = []

    for acte in ACTES_METIER:
        score = calculer_score(texte_norm, acte)
        if score > 0:
            item = acte.copy()
            item["score"] = score
            resultats.append(item)

    # trier par score décroissant
    resultats = sorted(resultats, key=lambda x: x["score"], reverse=True)
    return resultats


def main():
    st.set_page_config(page_title="Chatbot actes métier RSA - CD37", layout="wide")

    st.title("🤖 Assistant actes métier RSA (CD37)")
    st.write(
        "Collez votre compte rendu (CR) de rendez-vous ci-dessous. "
        "L’outil analysera le texte et proposera les actes métier les plus pertinents "
        "à partir d’un premier référentiel (exemples)."
    )

    texte_cr = st.text_area(
        "✍️ Compte rendu de rendez-vous",
        height=250,
        placeholder="Collez ici votre CR…"
    )

    if st.button("Analyser le CR"):
        if not texte_cr.strip():
            st.warning("Merci de coller un compte rendu avant de lancer l'analyse.")
            return

        resultats = analyser_cr(texte_cr)

        if not resultats:
            st.info("Aucun acte métier détecté avec la configuration actuelle.")
            return

        st.subheader("📌 Actes métier détectés")

        for acte in resultats:
            st.markdown("---")
            st.markdown(f"### ✅ {acte['intitule']}")
            st.write(f"**Catégorie :** {acte['categorie']}")
            st.write(f"**Type :** {acte['type']}")
            st.write(f"**Score détecté :** {acte['score']}")

            with st.expander("📝 Description"):
                st.write(acte["description"])

            with st.expander("📎 Ce qu'il faut préciser dans le commentaire"):
                st.write(acte["commentaire_attendu"])

        st.markdown("---")
        st.info(
            "Vous pouvez copier-coller le nom des actes ci-dessus pour les saisir dans Parcours RSA.\n"
            "Ce n'est qu'une première base : le référentiel peut être étoffé avec tous les actes du livret CD37."
        )


if __name__ == "__main__":
    main()
