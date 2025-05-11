from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import CustomUser
from .serializers import CustomUserSerializer, RegisterSerializer
import logging

logger = logging.getLogger(__name__)

class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        # 회원가입 성공 시 쿠키 설정
        response.set_cookie(
            'registration_status',
            'success',
            samesite='None',
            secure=True,
            httponly=True,
            max_age=3600
        )
        return response

class UserDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CustomUserSerializer

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        # 사용자 정보 조회 시 쿠키 설정
        response.set_cookie(
            'auth_token',
            request.auth,
            samesite='None',
            secure=True,
            httponly=True,
            max_age=3600
        )
        return response
    
@method_decorator(csrf_exempt, name='dispatch')
class DeleteAccountView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def delete(self, request):
        try:
            user = request.user
            password = request.data.get('password')

            if not password:
                return Response(
                    {"error": "비밀번호를 입력해주세요."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # check_password 메서드를 사용하여 비밀번호 검증
            if not user.check_password(password):
                return Response(
                    {"error": "비밀번호가 올바르지 않습니다."}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # 토큰 제거
            RefreshToken.for_user(user)
            
            user.delete()
            response = Response(
                {"message": "계정이 성공적으로 삭제되었습니다."}, 
                status=status.HTTP_200_OK
            )
            
            # 모든 관련 쿠키 삭제
            response.delete_cookie('auth_token')
            response.delete_cookie('registration_status')
            response.delete_cookie('access_token')
            response.delete_cookie('refresh_token')
            
            return response
            
        except Exception as e:
            logger.error(f"Account deletion failed: {str(e)}")
            return Response(
                {"error": "회원 탈퇴 처리 중 오류가 발생했습니다."}, 
                status=status.HTTP_400_BAD_REQUEST
            )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    # 사용자 인증 로직
    user = authenticate(username=request.data['username'], password=request.data['password'])
    if user:
        refresh = RefreshToken.for_user(user)
        response = Response({
            'message': 'Successfully logged in',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })
        response.set_cookie(
            'access_token',
            str(refresh.access_token),
            httponly=True,
            samesite='None',
            secure=True,
            max_age=3600
        )
        return response
    return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.COOKIES.get('refresh_token')
        token = RefreshToken(refresh_token)
        token.blacklist()
        response = Response({'message': 'Successfully logged out'})
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)