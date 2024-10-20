import streamlit as st


def apply_custom_styles():
    st.markdown(
        """
        <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            .stAppDeployButton {
            visibility: hidden;
            }

            /* Change the font and color in the titles and center them */
            h1 {
                color: #FF4B4B;
                font-family: 'Helvetica';
                padding-top: 0%;
            }
        """,
        unsafe_allow_html=True,
    )
