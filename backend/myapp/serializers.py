from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import University, Course

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})
    role_display = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    university_id = serializers.IntegerField(source='university.id', read_only=True, required=False, allow_null=True)
    # Add a writable field for university
    university = serializers.PrimaryKeyRelatedField(queryset=University.objects.all(), required=False, allow_null=True)
    gpa = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'name', 'username', 'email', 'password', 
                  'role', 'role_display', 'status', 'status_display', 
                  'date_joined', 'is_active', 'university_id', 'university', 'coursesWithGrades', 'gpa']
        extra_kwargs = {
            'password': {'write_only': True},
        }
    
    def get_role_display(self, obj):
        """Safely get role display name"""
        try:
            return obj.get_role_display()
        except (AttributeError, KeyError):
            return obj.role
    
    def get_status_display(self, obj):
        """Safely get status display name"""
        try:
            return obj.get_status_display()
        except (AttributeError, KeyError):
            return obj.status

    def get_gpa(self, obj):
        """Calculate GPA from coursesWithGrades"""
        try:
            courses_with_grades = obj.coursesWithGrades or []
            
            if not courses_with_grades:
                return '0.00'
                
            grade_values = {
                'A+': 4.0, 'A': 4.0, 'A-': 3.7,
                'B+': 3.3, 'B': 3.0, 'B-': 2.7,
                'C+': 2.3, 'C': 2.0, 'C-': 1.7,
                'D+': 1.3, 'D': 1.0, 'D-': 0.7,
                'F': 0.0, 'N/A': 0.0
            }
            
            total_points = 0
            total_credits = 0
            
            for enrollment in courses_with_grades:
                course_id = enrollment.get('courseId')
                grade = enrollment.get('grade', 'N/A')
                
                try:
                    course = Course.objects.get(id=course_id)
                    credits = course.credits
                    grade_value = grade_values.get(grade, 0)
                    
                    total_points += credits * grade_value
                    total_credits += credits
                except:
                    # Skip if course doesn't exist
                    pass
            
            if total_credits > 0:
                return '{:.2f}'.format(total_points / total_credits)
            else:
                return '0.00'
                
        except Exception as e:
            # If any error in calculation, default to 0
            return '0.00'

class UniversitySerializer(serializers.ModelSerializer):
    # Custom field for website with more flexible validation
    website = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    
    class Meta:
        model = University
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_website(self, value):
        """
        Validate and clean website URLs
        """
        if not value:
            return None
            
        # Ensure URL has protocol
        if value and not (value.startswith('http://') or value.startswith('https://')):
            value = 'https://' + value
            
        return value

class CourseSerializer(serializers.ModelSerializer):
    university_name = serializers.ReadOnlyField(source='university.name')
    enrolled_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'name', 'credits', 'professor', 'type', 'description', 
                  'university', 'university_name', 'enrolled_count']
    
    def get_enrolled_count(self, obj):
        """Calculate the number of students enrolled in this course"""
        enrolled_count = 0
        try:
            # Query all users who have this course in their coursesWithGrades
            users = User.objects.all()
            for user in users:
                if hasattr(user, 'coursesWithGrades'):
                    courses = getattr(user, 'coursesWithGrades', [])
                    if courses and any(c.get('courseId') == obj.id for c in courses):
                        enrolled_count += 1
        except:
            pass
        return enrolled_count
