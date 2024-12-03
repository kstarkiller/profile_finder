from fastapi import FastAPI, HTTPException
import uvicorn

from users_manager import (
    get_user,
    check_user,
    create_user,
    delete_user,
    add_search_to_history,
    update_search_in_history,
    get_search_history,
    get_search_by_chat_id,
    add_message_to_chat,
    delete_search_from_history,
    delete_all_searches_from_history,
)
from sources_manager import (
    get_profiles,
    truncate_table,
    insert_profile,
    replace_profiles,
)

app = FastAPI()


@app.post(
    "/", summary="Racine de l'API", response_description="API en cours d'exécution"
)
async def root():
    try:
        return {"message": "API en cours d'exécution"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/test", summary="Test de l'API", response_description="Test réussi")
async def test_api(input: dict):
    try:
        return {"message": input.get("message") + " Success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post(
    "/profile",
    summary="Ajouter un profil dans la base de données",
    response_description="Profil ajouté avec succès",
)
async def insert_profile_api(profile: dict):
    try:
        return insert_profile(profile)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put(
    "/profiles",
    summary="Remplacer les profils dans la base de données",
    response_description="Profils remplacés avec succès",
)
async def replace_profiles_api():
    try:
        return replace_profiles()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get(
    "/profiles",
    summary="Récupérer tous les profils de la base de données",
    response_description="Liste des profils",
)
async def get_profiles_api(params: dict):
    try:
        return get_profiles(params)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete(
    "/profiles",
    summary="Supprimer les profils",
    response_description="Table vidée avec succès",
)
async def truncate_table_api(json: dict):
    try:
        return truncate_table(json)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post(
    "/user",
    summary="Vérifier si un utilisateur existe",
    response_description="Utilisateur trouvé",
)
async def check_user_api(user: dict):
    try:
        return check_user(user.get("email"))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get(
    "/user",
    summary="Récupérer un utilisateur",
    response_description="Utilisateur trouvé",
)
async def get_user_api(user: dict):
    try:
        return get_user(user.get("email"), user.get("password"))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete(
    "/user",
    summary="Supprimer un utilisateur",
    response_description="Utilisateur supprimé",
)
async def delete_user_account_api(user: dict):
    try:
        return delete_user(user.get("email"), user.get("password"))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put(
    "/user",
    summary="Créer un utilisateur",
    response_description="Utilisateur créé",
)
async def create_user_api(user: dict):
    try:
        return create_user(user.get("name"), user.get("email"), user.get("password"))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put(
    "/search",
    summary="Ajouter une recherche à l'historique",
    response_description="Recherche ajoutée avec succès",
)
async def add_search_to_history_api(search: dict):
    try:
        return add_search_to_history(
            search.get("chat_id"), search.get("first_message"), search.get("user_email")
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post(
    "/search",
    summary="Mettre à jour une recherche dans l'historique",
    response_description="Recherche mise à jour avec succès",
)
async def update_search_in_history_api(chat_id):
    try:
        return update_search_in_history(chat_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get(
    "/searches",
    summary="Récupérer l'historique des recherches",
    response_description="Historique des recherches",
)
async def get_search_history_api(user_email: str):
    try:
        return get_search_history(user_email)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get(
    "/search",
    summary="Récupérer une recherche par chat_id",
    response_description="Recherche trouvée",
)
def get_search_by_chat_id_api(chat_id: str):
    try:
        return get_search_by_chat_id(chat_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post(
    "/message",
    summary="Ajouter un message à un chat",
    response_description="Message ajouté avec succès",
)
async def add_message_to_chat_api(message: dict):
    try:
        return add_message_to_chat(
            message.get("chat_id"),
            message.get("chat_history"),
            message.get("duration"),
            message.get("model"),
            message.get("model_label"),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete(
    "/search",
    summary="Supprimer une recherche de l'historique",
    response_description="Recherche supprimée avec succès",
)
async def delete_search_from_history_api(json: dict):
    try:
        delete_search_from_history(json.get("chat_id"))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete(
    "/searches",
    summary="Supprimer toutes les recherches de l'historique",
    response_description="Recherches supprimées avec succès",
)
async def delete_user_data_api(user: dict):
    try:
        delete_all_searches_from_history(user.get("email"))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5050)
