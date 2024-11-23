import os
import requests
from fastapi import HTTPException, Depends, status
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from docker_check import is_running_in_docker

# Configuration du secret et des algorithmes
SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

venv = is_running_in_docker()


def get_user(username: str):
    try:
        user = requests.post(
            f"http://{venv['db_api_host']}:{venv['db_api_port']}/user",
            json={"email": username},
        )
        if user.status_code == 200:
            return user.json()
        else:
            return None
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Créez un token JWT pour l'utilisateur spécifié.
    
    Args:
        data (dict): Dictionnaire contenant les informations de l'utilisateur
        expires_delta (timedelta): Durée de validité du token
        
    Returns:
        str: Token JWT
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Vérifiez si le token fourni est valide et renvoie les informations correspondantes de l'utilisateur.
    Cette fonction décode le token JWT pour extraire le nom d'utilisateur, puis récupère les informations de l'utilisateur depuis la base de données.
    Si le token est invalide ou si l'utilisateur n'existe pas, une exception HTTP 401 Unauthorized est levée.

    Args:
        token (str): Token de l'utilisateur

    Returns:
        dict: Dictionnaire contenant les informations de l'utilisateur

    Raises:
        HTTPException: Exception HTTP 401 Unauthorized si le token est invalide ou si l'utilisateur n'existe pas
    """
    token = credentials.credentials

    # Créez une exception HTTP 401 Unauthorized si les informations d'identification ne peuvent pas être validées
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Décodez le token JWT pour extraire le nom d'utilisateur
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    # Récupérez les informations de l'utilisateur depuis la base de données
    user = get_user(username)
    if user is None:
        raise credentials_exception
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    return token
