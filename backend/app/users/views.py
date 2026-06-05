from rest_framework.generics import CreateAPIView
from rest_framework.viewsets import GenericViewSet
from .serlializers import (
    EmailValidationSerializer,
    UserRegisterSerializer,
    EmailTokenObtainSerializer,
    RedisTokenSerializer,
)
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache
from . import register_logic



# -- 
class SwaggerLoginView(TokenObtainPairView):
    permission_classes = []

    def post(self, request, *args, **kwargs):

        serializer = EmailTokenObtainSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        return Response(
            {
                "access_token": data["access"],
                "refresh_token": data["refresh"],
                "token_type": "Bearer",
            }
        )

# ++ registration : view for registration, login with email and password, generating confirmation code and sending it to email, then validating the code and returning JWT tokens
class UserRegisterAPIView(GenericViewSet):
    parser_classes = [JSONParser,FormParser, MultiPartParser]
    permission_classes = [AllowAny]


    @action(
        detail=False, 
        methods=["post"], 
        url_path="get-email-code", 
        serializer_class=EmailValidationSerializer
    )
    def get_email_confirmation_code(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        use_case = register_logic.RegistWithCodeFromEmailUseCase()
        try: 
            use_case.execute(email=email)
            return Response({"message": "Confirmation code sent to email"}, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=400)
        

    @action(
        detail=False,
        methods=["post"],
        url_path="register",
        serializer_class=UserRegisterSerializer,
    )
    def register(self,request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        code = serializer.validated_data['code']

        cached_code = cache.get(f"email_confirmation_code_{email}")
        if not cached_code or cached_code != code:
            return Response({"error": "Invalid or expired confirmation code"}, status=400)
        
        user = serializer.save()
        cache.delete(f"email_confirmation_code_{email}")

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'token_type': 'Bearer',
            }
        )
        
        
            
        





# -- login : logic for login with email and password, generating confirmation code and sending it to email, then validating the code and returning JWT tokens
class RedisTokenObtainView(TokenObtainPairView):
    serializer_class = RedisTokenSerializer
    