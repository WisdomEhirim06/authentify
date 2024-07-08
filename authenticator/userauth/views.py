from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated  # Adjust permissions as needed
from rest_framework.authtoken.models import User  # Assuming custom User model
from .serializers import UserSerializer, OrganizationSerializer  # Import your UserSerializer
from django.http import status
from .models import Organization
from rest_framework_jwt.authentication import JWTAuthentication  # Import JWTAuthentication

class RegisterView(APIView):
    permission_classes = [AllowAny]  # Allow anyone to register

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(user.password)  # Ensure password hashing
            org_name = f"{user.first_name}'s Organisation"
            organization = Organization.objects.create(name=org_name)
            organization.users.add(user)
            user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    authentication_classes = [JWTAuthentication]  # Use JWT authentication

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'Please provide both email and password'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.check_password(password):
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        # Use JWT library to generate token
        token = JWTAuthentication().authenticate(user)[1]
        return Response({'token': token}, status=status.HTTP_200_OK)


class OrganizationListView(APIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users

    def get(self, request):
        organizations = Organization.objects.filter(users__in=[request.user])
        serializer = OrganizationSerializer(organizations, many=True)
        return Response(serializer.data)

class OrganizationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, org_id):
        try:
            organization = Organization.objects.get(pk=org_id)
            if request.user in organization.users.all():
                serializer = OrganizationSerializer(organization)
                return Response(serializer.data)
            else:
                return Response({'message': 'Unauthorized access to organization'}, status=status.HTTP_403_FORBIDDEN)
        except Organization.DoesNotExist:
            return Response({'message': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)
