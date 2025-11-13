# app.py
# -*- coding: utf-8 -*-

import os
import json
import unicodedata
import re

import streamlit as st
from openai import OpenAI

from data_actes_metier.py import ACTES_METIER


# ------------------------------------------------------------
# OUTILS TEXTE (utiles pour l'analyse de secours par mots-clés)
# ------------------------------------------------------------

def normaliser_texte(texte: str) -> str:
    """Met le texte en minuscules, enlève les accents et caractères spéciaux."""
    if not texte:
        return ""
    texte = texte.lower()
    texte = unicodedata.normalize("NFD", texte).encode("ascii", "ignore").decode("utf-8")
    texte = re.sub(r"[^a-z0-9\s']", " ", texte)
    texte = re.sub(r"\s+", " ", texte).strip()
    return texte


def calculer_score(texte_norm: str, acte: dict) -> int:
    """Score = nombre de mots-clés de l'acte trouvés dans le texte normalisé."""
    score = 0
    for mot in acte.get("mots_cles", []):
        mot_norm = normaliser_texte(mot)
        if mot_norm and mot_norm in texte_norm:
            score += 1
    return score


def analyser_cr_par_mots_cles(texte_cr: str, seuil: int = 1):
    """
    Analyse simple par mots-clés (mode secours quand l'IA n'est pas disponible).
    Renvoie la liste d'actes triée par score décroissant.
    """
    texte_norm = normaliser_texte(texte_cr)
    detectes = []

    for acte in ACTES_METIER:
        score = calculer_score(texte_norm, acte)
        if score >= seuil:
            item = acte.copy()
            item["score"] = score
            item["justification"] = "Détection par mots-clés (mode secours)."
            detectes.append(item)

    # quelques petits boosts très simples
    if "mdph" in texte_norm:
        for code in ("SAN_APPUI_MDPH", "SAN_INTERMEDIATION_MDPH"):
            for acte in ACTES_METIER:
                if acte.get("code") == code and not any(a["code"] == code for a in detectes):
                    item = acte.copy()
                    item["score"] = 1
                    item["justification"] = "Ajout automatique car le CR mentionne la MDPH."
                    detectes.append(item)

    if "mobilite" in texte_norm or "permis" in texte_norm:
        for acte in ACTES_METIER:
            if acte.get("code") == "MOB_APPUI_MOBILITE" and not any(
                a["code"] == "MOB_APPUI_MOBILITE" for a in detectes
            ):
                item = acte.copy()
                item["score"] = 1
                item["justification"] = "Ajout automatique car le CR mentionne la mobilité / le permis."
                detectes.append(item)

    if "fsl" in texte_norm:
        for acte in ACTES_METIER:
            if acte.get("code") == "LOG_AIDE_FSL" and not any(
                a["code"] == "LOG_AIDE_FSL" for a in detectes
            ):
                item = acte.copy()
                item["score"] = 1
                item["justification"] = "Ajout automatique car le CR mentionne le FSL."
                detectes.append(item)

    detectes = sorted(detectes, key=lambda x: x.get("score", 0), reverse=True)
    return detectes


# ------------------------------------------------------------
# ANALYSE PAR IA (OpenAI)
# ------------------------------------------------------------

def construire_contexte_actes():
    """
    Prépare une version compacte de la liste d'actes pour l'envoyer à l'IA.
    On n'envoie que le strict nécessaire pour limiter la taille du prompt.
    """
    actes_compacts = []
    for acte in ACTES_METIER:
        actes_compacts.append(
            {
                "code": acte.get("code"),
                "thematique": acte.get("thematique"),
                "rubrique": acte.get("rubrique"),
                "intitule": acte.get("intitule"),
                "description": acte.get("description", "")[:300],  # on coupe pour rester raisonnable
            }
        )
    return actes_compacts


def analyser_cr_par_ia(texte_cr: str):
    """
    Utilise un modèle d'IA pour lire le compte rendu et proposer les actes métier pertinents.
    Retourne une liste d'actes (dicts complets enrichis avec 'score' et 'justification').
    """

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY n'est pas définie dans les variables d'environnement ou les secrets Streamlit."
        )

    client = OpenAI(api_key=api_key)

    actes_compacts = construire_contexte_actes()

    # Consigne pour l'IA
    instruction = """
Tu es un assistant pour des référents RSA du Département 37.
On te donne :
1) Un compte rendu de rendez-vous (CR) écrit librement.
2) Une liste d'actes métier possibles, avec thématique, rubrique, code et intitulé.

Objectif :
- Lire le CR attentivement.
- Identifier les actes métier qui correspondent VRAIMENT à ce que le référent a fait ou prévu de faire.
- Il peut y avoir plusieurs thématiques (emploi, formation, santé, logement, budget, parentalité…).
- Ne propose pas d'actes qui ne sont pas justifiés par le CR.

Format de réponse (JSON strict) :
{
  "actes": [
    {
      "code": "<code exact de l'acte>",
      "pertinence": 0.0 à 1.0,
      "justification": "phrase courte expliquant pourquoi cet acte est pertinent"
    },
    ...
  ]
}

Règles :
- Ne renvoie QUE des actes avec une pertinence >= 0.4 environ.
- Ne crée JAMAIS de nouveaux codes : tu dois choisir parmi la liste fournie.
- Si aucun acte n'est pertinent, renvoie {"actes": []}.
"""

    payload = {
        "instruction": instruction,
        "cr": texte_cr,
        "actes": actes_compacts,
    }

    # Appel à l'API OpenAI (modèle léger pour réduire le coût, tu peux changer le nom du modèle).
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=json.dumps(payload, ensure_ascii=False),
        response_format={"type": "json_object"},
    )

    # Récupération du JSON renvoyé
    # Selon la doc, le texte se trouve dans output[0].content[0].text
    try:
        raw_text = response.output[0].content[0].text
    except Exception as e:
        raise RuntimeError(f"Impossible de lire la réponse de l'API : {e}")

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Réponse de l'API non valide (JSON) : {e}\nTexte brut : {raw_text}")

    actes_ia = data.get("actes", [])
    if not isinstance(actes_ia, list):
        raise RuntimeError("Le JSON renvoyé par l'IA ne contient pas de liste 'actes'.")

    # On re-mappe les codes vers nos objets ACTES_METIER complets
    actes_detectes = []
    index_par_code = {a.get("code"): a for a in ACTES_METIER}

    for item in actes_ia:
        code = item.get("code")
        if code in index_par_code:
            acte_base = index_par_code[code]
            copie = acte_base.copy()
            copie["score"] = float(item.get("pertinence", 0.0))
            copie["justification"] = item.get("justification", "").strip()
            actes_detectes.append(copie)

    # Tri par pertinence décroissante
    actes_detectes = sorted(actes_detectes, key=lambda x: x.get("score", 0), reverse=True)
    return actes_detectes


# ------------------------------------------------------------
# ORGANISATION DU RESULTAT
# ------------------------------------------------------------

def regrouper_par_thematique_et_rubrique(actes_detectes):
    """
    Construit une structure imbriquée :

    {
      "SANTE": {
          "APPUI": [actes...],
          "INTERMEDIATION": [actes...],
      },
      "MOBILITE": {
          ...
      }
    }
    """
    arbre = {}
    for acte in actes_detectes:
        th = acte.get("thematique", "AUTRE")
        rub = acte.get("rubrique", "AUTRE")

        arbre.setdefault(th, {})
        arbre[th].setdefault(rub, [])
        arbre[th][rub].append(acte)

    return arbre


# ------------------------------------------------------------
# INTERFACE STREAMLIT
# ------------------------------------------------------------

def main():
    st.set_page_config(
        page_title="Assistant actes métier RSA - CD37 (IA)",
        layout="wide"
    )

    st.title("🤖 Assistant actes métier RSA – CD37 (version IA)")
    st.write(
        """
        Cet outil aide les **référents RSA** à retrouver les actes métier à partir du compte rendu
        du rendez-vous (CR).

        - Il utilise en priorité une **IA** pour analyser le texte libre.  
        - En cas d’indisponibilité de l’IA (clé manquante, erreur), il bascule en **mode secours par mots-clés**.
        """
    )

    # --------- Barre latérale ----------
    st.sidebar.header("⚙️ Paramètres")

    seuil_mots_cles = st.sidebar.slider(
        "Seuil minimum de mots-clés (mode secours uniquement)",
        min_value=1,
        max_value=5,
        value=1,
        help=(
            "Ce seuil n'est utilisé qu'en cas de bascule sur l'analyse par mots-clés."
        ),
    )

    st.sidebar.info(
        "⚠️ Le CR ne doit pas contenir de noms, adresses ou autres données identifiantes.\n"
        "L’analyse se fait uniquement sur le contenu métier."
    )

    # --------- Zone de saisie du CR ----------
    st.subheader("✍️ Compte rendu de rendez-vous")

    texte_cr = st.text_area(
        "Collez ici le compte rendu (CR) :",
        height=260,
        placeholder=(
            "Exemple : Nous avons évoqué la demande MDPH, les difficultés de mobilité pour se rendre en formation, "
            "un projet de permis B, et une orientation vers la PMI pour le plus jeune enfant..."
        ),
    )

    lancer_analyse = st.button("🔍 Analyser le compte rendu")

    if lancer_analyse:
        if not texte_cr.strip():
            st.warning("Merci de coller un compte rendu avant de lancer l'analyse.")
            return

        mode = "ia"
        actes_detectes = []

        # Tentative IA
        try:
            st.info("Analyse du compte rendu par l’IA en cours…")
            actes_detectes = analyser_cr_par_ia(texte_cr)
            if not actes_detectes:
                st.warning(
                    "L’IA n’a pas trouvé d’actes métier clairement justifiés par ce CR.\n"
                    "Bascule sur le mode secours par mots-clés."
                )
                mode = "mots_cles"
                actes_detectes = analyser_cr_par_mots_cles(texte_cr, seuil=seuil_mots_cles)
        except Exception as e:
            st.error(f"Erreur lors de l'appel à l'IA : {e}")
            st.info("Bascule en mode secours (analyse par mots-clés).")
            mode = "mots_cles"
            actes_detectes = analyser_cr_par_mots_cles(texte_cr, seuil=seuil_mots_cles)

        if not actes_detectes:
            st.info(
                "Aucun acte métier n'a été détecté.\n\n"
                "- Vérifiez que le CR décrit bien les actions du référent\n"
                "- En mode secours, essayez éventuellement de baisser le seuil."
            )
            return

        # Regroupement par thématique / rubrique
        arbre = regrouper_par_thematique_et_rubrique(actes_detectes)

        # --------- Résumé des thématiques ----------
        st.subheader("📚 Thématiques détectées dans le CR")
        liste_thematiques = list(arbre.keys())
        st.write(", ".join(liste_thematiques))

        if mode == "ia":
            st.success("Analyse réalisée par l’IA (avec renvoi d’un score de pertinence et une justification).")
        else:
            st.warning("Analyse réalisée en mode secours par Mots-clés (sans IA).")

        st.markdown("---")
        st.subheader("📌 Détail par thématique, rubrique et acte métier")

        # --------- Affichage détaillé ----------
        for thematique, rubriques in arbre.items():
            st.markdown(f"## 🧩 {thematique}")

            for rubrique, actes in rubriques.items():
                st.markdown(f"### 🔹 {rubrique}")

                for acte in actes:
                    score = acte.get("score", 0)
                    st.markdown(f"**• {acte['intitule']}**  *(score/pertinence : {score:.2f})*")

                    with st.expander("📝 Description de l'acte"):
                        st.write(acte.get("description", ""))

                    justification = acte.get("justification")
                    if justification:
                        with st.expander("💡 Pourquoi cet acte ?"):
                            st.write(justification)

                    with st.expander("📎 Commentaire attendu dans Parcours RSA"):
                        st.write(acte.get("commentaire_attendu", ""))

                st.markdown("---")

        # --------- Vue tableau ----------
        import pandas as pd

        df = pd.DataFrame(
            [
                {
                    "Thématique": a.get("thematique", ""),
                    "Rubrique": a.get("rubrique", ""),
                    "Acte": a.get("intitule", ""),
                    "Code": a.get("code", ""),
                    "Score / Pertinence": a.get("score", 0),
                    "Pourquoi (si IA)": a.get("justification", ""),
                }
                for a in actes_detectes
            ]
        )

        st.subheader("📊 Vue tableau des actes détectés")
        st.dataframe(df, use_container_width=True)


if __name__ == "__main__":
    main()
