from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class AllowInactiveJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that allows inactive users to authenticate.
    Only blocked users are restricted at the view level.
    """
    def get_user(self, validated_token):
        user = super().get_user(validated_token)
        # super() raises InvalidToken if user.is_active is False — we catch and re-fetch
        return user

    def authenticate(self, request):
        try:
            return super().authenticate(request)
        except Exception:
            # If super() fails due to is_active=False, manually validate token
            header = self.get_header(request)
            if header is None:
                return None
            raw_token = self.get_raw_token(header)
            if raw_token is None:
                return None
            try:
                validated_token = self.get_validated_token(raw_token)
            except TokenError:
                return None
            # Get user without is_active check
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                user_id = validated_token.get('user_id')
                user = User.objects.get(id=user_id)
                return user, validated_token
            except User.DoesNotExist:
                return None
