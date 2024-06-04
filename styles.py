import streamlit as st

def apply_custom_styles():
    st.markdown("""
        <style>
            /* Modifier le fond de l'ensemble de la page */
                
            body {
                background-color: #FAFAFA;
            }
                
            /* remove default sidebar  */
            section[data-testid="stSidebar"]{
            display: none;
                
            }

            /* Changer la police et la couleur dans les titres */
            h1 {
                color: #FF4B4B;
                font-family: 'Helvetica';
            }

            h2, h3, h4, h5, h6 {
                color: #37474F;
                font-family: 'Helvetica';
            }

            /* Personnaliser le fond et la couleur de la barre latérale */
            .sidebar .sidebar-content {
                background-color: #F0F0F0;
                color: #333333;
            }

            /* Modifier l'apparence des boutons */
            .stButton>button {
                padding: 10px 24px;
                border-radius: 8px;
                font-family: 'Helvetica';
                font-size: 16px;

            }

            /* Autres styles personnalisés */
            /* Ajoutez ici d'autres styles selon vos préférences */

        </style>
        """, unsafe_allow_html=True)

