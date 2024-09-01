from datetime import date
import streamlit as st

from processing_request import process_input
from model_precision_improvements import structure_query  # Import de la fonction structure_query

# Contexte du chatbot
# starting_context = f"""
# Today it's {date.today()} and you're a French chatbot assistant that helps users find team members based on the data provided.
# Keep the answer concise and don't hesitate to use a table to present the data.
# If you don't know the answer, just say you don't know, don't try to make up an answer.
# """
# starting_context = f"""
# You are a French chatbot assistant specialized in finding team members based on their location, availability, skills and certifications.
# - Answer concisely. Use tables to structure data.
# - Use the current date ({date.today()}) for any time-related questions. For months, consider the nearest future month unless otherwise specified.
# - Combine occupancy periods and percentages to calculate availability if requested.
# - Do not modify data and only provide results if all user criteria are met. If unsure, indicate that you don't know.
# """
starting_context = f"""
You are a French chatbot assistant that helps the user find team members based on their location, availability, skills, and certifications.
- Format responses as concise, consistently and clearly as possible, using headers and tables when necessary. Don't explain what you're doing and summarize the data when necessary.
- Use the current date ({date.today()}) for any time-related questions.
- For months, consider the nearest future month unless otherwise specified. Don't consider months in the past or more than 12 months in the futur unless otherwise specified.
- Combine occupancy periods and percentages to calculate total availability over a given period.
- Do not assume anything, do not make up the data and only return members that meet user's criteria.
- If several members match the criteria, present them in order of relevance (availability, skills, etc.).
"""

print(starting_context)

def display_accueil():
    """
    Display the chatbot interface.
    
    :return: None
    """
    try:
        if "chat_history" not in st.session_state:
            st.session_state["chat_history"] = [
                {"role": "system", "content": starting_context}
            ]
            st.session_state["chat"] = []
            st.session_state["query_context"] = []

        def update_input():
            user_input = st.session_state["temp_input"]

            if user_input:
                # Rechercher le terme 'développeur' dans la question de l'utilisateur est le remplacer par 'profil'
                if 'développeur' in user_input:
                    modified_user_input = user_input.replace('développeur', 'profil')
                elif 'développeurs' in user_input:
                    modified_user_input = user_input.replace('développeurs', 'profils')
                else:
                    modified_user_input = user_input
                
                query_context = structure_query(modified_user_input)
                st.session_state["query_context"].append({"query": modified_user_input, "context": query_context})
                chatbot_response, updated_chat_history = process_input(
                    st.session_state["query_context"], st.session_state["chat_history"]
                )

                st.session_state["chat_history"] = updated_chat_history
                st.session_state["chat"].append(
                    {"user": user_input, "assistant": chatbot_response}
                )
                st.session_state["query_context"].append({"context": chatbot_response})

        st.chat_input(
            placeholder="Posez votre question...", key="temp_input", on_submit=update_input
        )

        if len(st.session_state["chat"]) == 0:
            with st.chat_message("Assistant"):
                st.write("Bonjour, comment puis-je vous aider ?")
        else:
            for i in range(len(st.session_state["chat"])):
                bot_message = st.session_state["chat"][i]["assistant"]
                user_message = st.session_state["chat"][i]["user"]

                with st.chat_message("User"):
                    st.write(f"Vous : {user_message}")
                    # Ajouter un identifiant unique au message de l'utilisateur
                    st.markdown(f"<div id='message-{i}-user'></div>", unsafe_allow_html=True)

                with st.chat_message("Assistant"):
                    st.write(f"Assistant : {bot_message}")
                    # Ajouter un identifiant unique au message de l'assistant
                    st.markdown(f"<div id='message-{i}-assistant'></div>", unsafe_allow_html=True)

            # Ajouter un script JavaScript pour faire défiler jusqu'au début du message le plus récent
            st.markdown(
                f"""
                <script>
                var latestMessage = document.getElementById('message-{len(st.session_state["chat"])-1}-user');
                if (latestMessage) {{
                    latestMessage.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                }}
                </script>
                """,
                unsafe_allow_html=True
            )
    except Exception as e:
        st.error(f"An error occurred in display_accueil: {e}")

if __name__ == "__main__":
    display_accueil()
