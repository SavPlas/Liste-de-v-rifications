import streamlit as st

def app_generer_liste_verification(infos_generales, checklist_items):
    if "resultats_checklist" not in st.session_state:
        st.session_state["resultats_checklist"] = {}

    resultats = st.session_state["resultats_checklist"]

    for item in checklist_items:
        st.markdown(f"**{item}**")
        
        data = resultats.get(item, {})

        # Initialisation sécurisée des champs booléens
        data["n_a"] = st.checkbox("N/A", value=data.get("n_a", False), key=f"na_{item}")
        data["oui"] = st.checkbox("Oui", value=data.get("oui", False), key=f"oui_{item}")
        data["non"] = st.checkbox("Non", value=data.get("non", False), key=f"non_{item}")

        # Gestion des sous-dates associées à certains items
        dates = data.get("dates", {})

        if data["oui"]:
            label_date = st.text_input(f"Libellé date liée à '{item}' (facultatif)", value="", key=f"label_date_{item}")
            date_value = st.date_input(f"Date associée (facultative)", key=f"date_{item}")
            if label_date:
                dates[label_date] = date_value.strftime("%d-%m-%Y")

        data["dates"] = dates

        # Enregistrement dans session_state
        resultats[item] = data

        st.markdown("---")
