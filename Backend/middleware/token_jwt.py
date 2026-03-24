import jwt
import datetime
from config.settings import settings

SECRET_KEY = settings.jwt_secret_key
ALGORITHM = settings.jwt_algo


def create_jwt_token():
    payload = {
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24),
        "iat": datetime.datetime.utcnow(),
        "scope": "AI_Chat_Bot"
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_jwt_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
