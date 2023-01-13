# credit: https://github.com/ianrufus/youtube/blob/main/fastapi-jwt-auth/src/auth.py
import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta


class AuthHandler:
    security = HTTPBearer()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    secret = 'SECRET'

    def password_hash(self, password):
        return self.pwd_context.hash(password)

    def password_verify(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def token_encode(self, user_uid):
        payload = {
            'exp': datetime.utcnow() + timedelta(days=0, minutes=5),
            'iat': datetime.utcnow(),
            'sub': user_uid
        }
        return jwt.encode(
            payload,
            self.secret,
            algorithm='HS256'
        )

    def token_decode(self, token):
        try:
            payload = jwt.decode(token, self.secret, algorithms=['HS256'])
            return payload['sub']
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Signature has expired')
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail='Invalid token')

    def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
        return self.decode_token(auth.credentials)
