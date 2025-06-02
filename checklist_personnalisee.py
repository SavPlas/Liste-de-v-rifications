import streamlit as st
import datetime

def get_initial_item_state():
    return {
        "oui": False,
        "non": False,
        "signe_lpeth": False,
        "envoye_regie": False,
        "envoye_cfwb": False,
        "doc_envoye_cfwb": False,
        "document_a_completer": False,
        "doc_envoye_assu": False,
        "doc_a_envoyer": False,
        "n_a": False,
        "dates": {}
    }

def app_generer_liste_verification():
    st.header("1. Informations Générales du Voyage")

    if "infos_generales" not in st.session_state:
        st.session_state.infos_generales = {
            "Intitulé du voyage": "",
            "Code régie": "",
            "Professeur-organisateur": ""
        }

    st.session_state.infos_generales["Intitulé du voyage"] = st.text_input("Intitulé du voyage", value=st.session_state.infos_generales["Intitulé du voyage"])
    st.session_state.infos_generales["Code régie"] = st.text_input("Code régie", value=st.session_state.infos_generales["Code régie"])
    st.session_state.infos_generales["Professeur-organisateur"] = st.text_input("Professeur-organisateur", value=st.session_state.infos_generales["Professeur-organisateur"])

    checklist_items = [
        "F1",
        "Demande d'activité scolaire",
        "Demande de résa TRAIN",
        "CEC 5",
        "CEC6bis",
        "Accord CFWB",
        "Office des étrangers : des étudiants de nationalité non-européenne ?",
        "Assurance provinciale"
    ]

    if "resultats_checklist" not in st.session_state:
        st.session_state.resultats_checklist = {
            item: get_initial_item_state() for item in checklist_items
        }

    st.header("2. Statut des Éléments de la Checklist")

    for item in checklist_items:
        st.subheader(item)
        data = st.session_state.resultats_checklist[item]

        col1, col2, col3 = st.columns(3)
        with col1:
            data["n_a"] = st.checkbox("N/A", value=data["n_a"], key=f"na_{item}")
        if not data["n_a"]:
            with col2:
                data["oui"] = st.checkbox("Oui", value=data["oui"], key=f"oui_{item}")
            with col3:
                data["non"] = st.checkbox("Non", value=data["non"], key=f"non_{item}")

            if data["oui"]:
                if "signe_lpeth" in data:
                    data["signe_lpeth"] = st.checkbox("Signé LPETH", value=data["signe_lpeth"], key=f"signe_{item}")
                    if data["signe_lpeth"]:
                        date_lpeth = st.date_input("Date signature LPETH", key=f"date_lpeth_{item}")
                        data["dates"]["Signé direction LPETH"] = date_lpeth.strftime("%d-%m-%Y")

                if "envoye_regie" in data:
                    data["envoye_regie"] = st.checkbox("Envoyé Régie", value=data["envoye_regie"], key=f"regie_{item}")
                    if data["envoye_regie"]:
                        date_regie = st.date_input("Date envoi Régie", key=f"date_regie_{item}")
                        data["dates"]["Envoyé à la Régie"] = date_regie.strftime("%d-%m-%Y")

                if "envoye_cfwb" in data:
                    data["envoye_cfwb"] = st.checkbox("Envoyé CFWB", value=data["envoye_cfwb"], key=f"cfwb_{item}")
                    if data["envoye_cfwb"]:
                        date_cfwb = st.date_input("Date envoi CFWB", key=f"date_cfwb_{item}")
                        data["dates"]["Envoyé à la CFWB"] = date_cfwb.strftime("%d-%m-%Y")

                if "doc_envoye_cfwb" in data:
                    data["doc_envoye_cfwb"] = st.checkbox("Document envoyé à la CFWB", value=data["doc_envoye_cfwb"], key=f"doccfwb_{item}")
                    if data["doc_envoye_cfwb"]:
                        date_doc_cfwb = st.date_input("Date document CFWB", key=f"datedoccfwb_{item}")
                        data["dates"]["Document envoyé à la CFWB"] = date_doc_cfwb.strftime("%d-%m-%Y")

                if "doc_envoye_assu" in data:
                    data["doc_envoye_assu"] = st.checkbox("Document envoyé au service assurances", value=data["doc_envoye_assu"], key=f"docassu_{item}")
                    if data["doc_envoye_assu"]:
                        date_doc_assu = st.date_input("Date document assurance", key=f"datedocassu_{item}")
                        data["dates"]["Document envoyé au service assurances"] = date_doc_assu.strftime("%d-%m-%Y")

                if "document_a_completer" in data:
                    data["document_a_completer"] = st.checkbox("Document à compléter", value=data["document_a_completer"], key=f"acompleter_{item}")

                if "doc_a_envoyer" in data:
                    data["doc_a_envoyer"] = st.checkbox("Document à envoyer", value=data["doc_a_envoyer"], key=f"aenvoyer_{item}")

    st.session_state.resultats_checklist.update({
        item: st.session_state.resultats_checklist[item] for item in checklist_items
    })
