import streamlit as st

def upload_file():
    st.subheader("Téléversement de Fichier")
    st.markdown("""
        #### Instructions pour le téléversement de fichiers
        - **Formats de fichier acceptés :** PDF, TXT, CSV
        - Assurez-vous que le fichier ne dépasse pas la taille maximale autorisée.
        - Pour les fichiers CSV, veillez à ce qu'ils soient correctement formatés.
    """)
    # uploaded_file = st.file_uploader("", &#8203;``【oaicite:0】``&#8203;
