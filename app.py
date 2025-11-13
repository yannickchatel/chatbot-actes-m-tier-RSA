import streamlit as st
import unicodedata
import re

from data_actes_metier import ACTES_METIER


def normaliser_texte(texte: str) -> str:
    texte = texte.lower()
    texte = unicodedata.normalize("NFD", texte).encode("ascii", "ignore").decode("utf-8")
    texte = re.sub(r"[^a-z0-9\s']", " ", texte)
    texte = re.sub(r"\s+", " ", texte).strip()
    return texte


def calculer_score(texte_norm: str, acte: dict) -> int:
    score = 0
    for mot in acte.get("mots_cles", []):
        mot_norm = normaliser_texte(mot)
        if mot_norm and mot_norm in texte_norm:
            score += 1
    return score


def analyser_cr(texte_cr: str, seuil: int = 1):
    texte_norm = normaliser_texte(texte_cr)
    detectes = []

    for acte in ACTES_METIER:
        score = calculer_score(texte_norm, acte)
        if score >= seuil:
            item = acte.copy()
            item["score"] = score
            detectes.append(item)

    # tri global par score pour info
    detectes = sorted(detectes, key=lambda x: x["score"], reverse=True)
    return detectes


def regrouper_par_thematique_et_rubrique(actes_detectes):
    """
    Retourne une structure imbriquée :
    {
      "ACCES A L’EMPLOI": {
          "INFO ET CONSEIL": [actes...],
          "APPUI": [actes...],
          ...
      },
      "LOGEMENT": {
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


def main():
    st.set_page_config(page_title="Chatbot actes métier RSA - CD37", layout="wide")
    st.title("🤖 Assistant actes métier RSA (CD37)")

    st.write(
        "Collez votre compte rendu (CR). L’outil détecte les *thématiques*, "
        "les *rubriques* (Info et conseil, Orientation vers, Appui, etc.) "
        "et les *actes métier* correspondants."
    )

    seuil = st.sidebar.slider(
        "Seuil minimum de mots-clés par acte",
        1, 5, 1,
        help="Plus le seuil est élevé, plus il faut de mots-clés pour proposer un acte."
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

        actes_detectes = analyser_cr(texte_cr, seuil=seuil)

        if not actes_detectes:
            st.info("Aucun acte métier détecté. Essayez de baisser le seuil ou d’enrichir les mots-clés.")
            return

        # Regroupement thématique → rubrique
        arbre = regrouper_par_thematique_et_rubrique(actes_detectes)

        # Résumé des thématiques trouvées
        st.subheader("📚 Thématiques détectées")
        st.write(", ".join(arbre.keys()))

        st.markdown("---")
        st.subheader("📌 Détail par thématique / rubrique / acte")

        for thematique, rubriques in arbre.items():
            st.markdown(f"## 🧩 {thematique}")

            for rubrique, actes in rubriques.items():
                st.markdown(f"### 🔹 {rubrique}")

                for acte in actes:
                    st.markdown(f"**• {acte['intitule']}**  (score : {acte['score']})")
                    with st.expander("Description"):
                        st.write(acte["description"])
                    with st.expander("Commentaire attendu"):
                        st.write(acte["commentaire_attendu"])

            st.markdown("---")

        st.info(
            "Vous pouvez maintenant sélectionner, dans Parcours RSA, les thématiques, rubriques et actes "
            "correspondant à ce qui est ressorti de ce CR."
        )


if __name__ == "__main__":
    main()
