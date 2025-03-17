from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from rest_framework.authtoken import views as auth_views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'universities', views.UniversityViewSet)
router.register(r'courses', views.CourseViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('current-user/', views.get_current_user, name='current-user'),
    path('user-roles/', views.get_user_roles, name='user-roles'),
    path('user-statuses/', views.get_user_statuses, name='user-statuses'),
    path('login/', views.user_login, name='user-login'),
    path('api-token-auth/', auth_views.obtain_auth_token, name='api-token-auth'),
    path('debug/student/<int:pk>/', views.debug_student_data, name='debug-student'),
    path('debug/create-student/', views.debug_create_student, name='debug-create-student'),
]
