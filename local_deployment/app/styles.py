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

            /* Change the background of the entire page */
            body {
                background-color: #F3F3F3;
            }

            /* Do not display the Sidebar collapse button */            
            .sidebar-toggle {
                display: none;
            }

            /* Do not display .st-emotion-cache-79elbk */
            .st-emotion-cache-79elbk {
                display: none;
            }

            /* Change the font and color in the titles and center them */
            h1 {
                color: #FF4B4B;
                font-family: 'Helvetica';
                padding-top: 1%;
            }

            /*
            h2, h3, h4, h5, h6 {
                color: #37474F;
                font-family: 'Helvetica';
            } */

            /* Center the title h1#profile_finder_chatbot */
            h1#profile_finder_chatbot {
                text-align: center;
            }


            /* Customize the background and color of the sidebar */
            .sidebar .sidebar-content {
                background-color: #F0F0F0;
                color: #333333;
            }

            /* Change the appearance of the buttons */
            .stButton>button {
                # padding: 10% 24%;
                # border-radius: 8%;
                # font-family: 'Helvetica';
                # font-size: 16%;
            }

            /* Reduce the margin of the container */
            .st-emotion-cache-7tauuy {
                padding: 2% 10%;
            }

            .st-emotion-cache-qdbtli {
                padding: 2% 20% 5% 10%;

        </style>
        """,
        unsafe_allow_html=True,
    )
