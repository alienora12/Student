from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework.views import APIView
from django.http import Http404
import logging
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.authentication import TokenAuthentication

from .serializers import UserSerializer, UniversitySerializer, CourseSerializer
from .models import University, Course
from .permissions import IsHeadAdminOrUniversityAdmin

# Set up logging
logger = logging.getLogger(__name__)
User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing users
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # Change permission to require authentication
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter users based on role and university"""
        user = self.request.user
        
        # Students can see all users (previously they could only see themselves)
        if user.role == 'student':
            # For students, return all users or filter by their university
            return User.objects.all()
            # Alternative: return only users from their university:
            # return User.objects.filter(university=user.university) if user.university else User.objects.all()
        
        # Teachers can see students and teachers from their university
        if user.role == 'teacher' and user.university:
            return User.objects.filter(university=user.university)
        
        # University admins can see all users from their university
        if user.university and not user.is_superuser:
            return User.objects.filter(university=user.university)
            
        # Head admins can see all users
        return User.objects.all()
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error in UserViewSet.list: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def perform_create(self, serializer):
        try:
            # Hash the password if it's provided
            if 'password' in self.request.data and self.request.data['password']:
                password = make_password(self.request.data['password'])
                serializer.save(password=password)
            else:
                serializer.save()
        except Exception as e:
            logger.error(f"Error in perform_create: {str(e)}")
            raise
    
    def perform_update(self, serializer):
        try:
            # Only hash the password if it's changed
            if 'password' in self.request.data and self.request.data['password']:
                password = make_password(self.request.data['password'])
                serializer.save(password=password)
            else:
                serializer.save()
        except Exception as e:
            logger.error(f"Error in perform_update: {str(e)}")
            raise

class UniversityViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing universities
    """
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    permission_classes = [permissions.IsAuthenticated, IsHeadAdminOrUniversityAdmin]
    
    def get_queryset(self):
        """Filter universities by user access"""
        user = self.request.user
        
        # Head admin sees all universities
        if not user.university:
            return University.objects.all()
            
        # University admin sees only their university
        return University.objects.filter(id=user.university.id)
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error in UniversityViewSet.list: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CourseViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing courses
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated, IsHeadAdminOrUniversityAdmin]
    
    def get_queryset(self):
        """Filter courses by university and user access"""
        user = self.request.user
        university_id = self.request.query_params.get('university', None)
        
        # Base queryset
        queryset = Course.objects.all()
        
        # Apply university filter if provided
        if university_id is not None:
            queryset = queryset.filter(university_id=university_id)
        
        # Filter by user permissions
        if user.is_authenticated and user.university:
            # University admin can only see their university's courses
            queryset = queryset.filter(university_id=user.university.id)
            
        return queryset
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error in CourseViewSet.list: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def perform_create(self, serializer):
        """Ensure university admin can only create courses for their university"""
        user = self.request.user
        
        # If university admin, force university to be their own
        if user.university:
            serializer.save(university=user.university)
        else:
            serializer.save()

@api_view(['GET'])
@permission_classes([permissions.AllowAny])  # For development, allow any access
def get_current_user(request):
    """
    Get the currently logged-in user
    """
    try:
        if not request.user.is_authenticated:
            return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Error in get_current_user: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])  # For development, allow any access
def get_user_roles(request):
    """
    Get all available user roles
    """
    try:
        return Response(dict(User.ROLE_CHOICES))
    except Exception as e:
        logger.error(f"Error in get_user_roles: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])  # For development, allow any access
def get_user_statuses(request):
    """
    Get all available user statuses
    """
    try:
        return Response(dict(User.STATUS_CHOICES))
    except Exception as e:
        logger.error(f"Error in get_user_statuses: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def user_login(request):
    """
    Custom login view that returns user data along with token
    """
    try:
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({'error': 'Please provide both username and password'},
                            status=status.HTTP_400_BAD_REQUEST)
        
        # Authenticate user
        user = authenticate(username=username, password=password)
        
        if not user:
            return Response({'error': 'Invalid credentials'}, 
                            status=status.HTTP_401_UNAUTHORIZED)
        
        # Check if user is active
        if not user.is_active:
            return Response({'error': 'User is disabled'}, 
                            status=status.HTTP_401_UNAUTHORIZED)
        
        # Get or create token
        token, created = Token.objects.get_or_create(user=user)
        
        # Return user data with token
        serializer = UserSerializer(user)
        response_data = serializer.data
        response_data['token'] = token.key
        
        return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error in user_login: {str(e)}")
        return Response({"error": str(e)}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Add a debug endpoint to help troubleshoot student creation
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def debug_student_data(request, pk=None):
    """
    Debug endpoint to check stored student data
    """
    try:
        if pk:
            student = User.objects.get(id=pk)
            serializer = UserSerializer(student)
            return Response({
                'user_data': serializer.data,
                'raw_courses_with_grades': student.coursesWithGrades,
                'courses_with_grades_type': str(type(student.coursesWithGrades))
            })
        else:
            return Response({'error': 'Please provide a student ID'}, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def debug_create_student(request):
    """
    Debug endpoint to help troubleshoot student creation with university
    """
    try:
        # Log the incoming data
        print("Received data:", request.data)
        
        # Extract university ID if present
        university_id = request.data.get('university_id') or request.data.get('university')
        print(f"University ID extracted: {university_id}")
        
        # Try to find university
        if university_id:
            try:
                university = University.objects.get(id=university_id)
                print(f"Found university: {university}")
            except University.DoesNotExist:
                print(f"University with ID {university_id} not found")
        
        # Create user via serializer
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            print(f"User created with university: {user.university}")
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        else:
            print("Validation errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"Error in debug_create_student: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

