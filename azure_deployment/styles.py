import streamlit as st

def apply_custom_styles():
    st.markdown(
        """
        <style>
            /* Modifier le fond de l'ensemble de la page */
            body {
                background-color: #F3F3F3;
            }
                        
            /* remove default sidebar */
            # section[data-testid="stSidebar"]{
            #     display: none;
            # }

            /* Na pas afficher .st-emotion-cache-79elbk */
            .st-emotion-cache-79elbk {
                display: none;
            }

            /* Changer la police et la couleur dans les titres et le centrer*/
            h1 {
                color: #FF4B4B;
                font-family: 'Helvetica';
                padding-top: 1%;
            }

            h2, h3, h4, h5, h6 {
                color: #37474F;
                font-family: 'Helvetica';
            }

            /* Centrer le titre h1#profile_finder_chatbot */
            h1#profile_finder_chatbot {
                text-align: center;
            }

            /* Personnaliser le fond et la couleur de la barre latérale */
            .sidebar .sidebar-content {
                background-color: #F0F0F0;
                color: #333333;
            }

            /* Modifier l'apparence des boutons */
            .stButton>button {
                # padding: 10% 24%;
                # border-radius: 8%;
                # font-family: 'Helvetica';
                # font-size: 16%;
            }

            /* Réduire le margin de container */
            .st-emotion-cache-7tauuy {
                padding: 2% 10%;
            }

            .st-emotion-cache-qdbtli {
                padding: 2% 20% 5% 10%;

        </style>
        """,
        unsafe_allow_html=True,
    )