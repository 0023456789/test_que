import jwt
import os
from rest_framework import authentication
from rest_framework import exceptions

JWT_SECRET = os.environ.get("JWT_SECRET", "super-secret-demo-key")

class DummyUser:
    def __init__(self, payload):
        self.payload = payload
        self.is_authenticated = True

    @property
    def role(self):
        return self.payload.get("role")

    @property
    def patient_id(self):
        return self.payload.get("patient_id")

class MicroserviceJWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Invalid token')

        user = DummyUser(payload)
        return (user, token)
