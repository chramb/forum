# credit: https://github.com/ianrufus/youtube/blob/main/fastapi-jwt-auth/src/auth.py
import jwt
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordRequestForm, OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta

from util.config import config

class AuthHandler:
    options = config(filename="config.ini", section="auth")
    security = HTTPBearer()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    secret = options['jwt_secret']
    jwt_algorithm = 'HS256'


    # TODO: move those to config.ini

    def password_hash(self, password):
        return self.pwd_context.hash(password)

    def password_verify(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def token_encode(self, user_uid):
        payload = {
            'exp': datetime.utcnow() + timedelta(days=0, minutes=30),
            'iat': datetime.utcnow(),
            'sub': user_uid
        }
        return jwt.encode(
            payload,
            self.secret,
            algorithm=self.jwt_algorithm
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
        """
        :returns: account_uid
        """
        return self.token_decode(auth.credentials)