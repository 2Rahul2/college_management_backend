from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FacultyViewSet,StudentEnrollmentView ,Health , StudentEnrolledSubjectsView ,LoginView ,RowCountView ,ReturnUserid , SubjectWithFaculties ,ReturnRole,LogoutView, StudentViewSet,SubjectViewSet,AssignFacultyToStudentView ,RegisterView , StudentListView , StudentDetailView

# router = DefaultRouter()
# router.register(r'faculties', FacultyViewSet)
# router.register(r'students', StudentViewSet)
# router.register(r'subjects', SubjectViewSet)

urlpatterns = [
    path('health/' , Health.as_view()),
     path('api/login/', LoginView.as_view(), name='login'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    # path('api/', include(router.urls)),
    path('student-count/' , RowCountView.as_view() ,name="student_count"),
    # path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/token/refresh/', MyTokenRefreshView.as_view(), name='token_refresh'), 
    path('register/', RegisterView.as_view(), name='register'),
    path('students/', StudentListView.as_view(), name='user-list'),
    path('student/<int:pk>/' , StudentDetailView.as_view() , name='student-details'),
    path('assign-faculty-to-student/' ,AssignFacultyToStudentView.as_view() ),
    path('role/' , ReturnRole.as_view()),
    path('userid/' , ReturnUserid.as_view()),
    path('subject-with-faculties/' , SubjectWithFaculties.as_view()),
    path('enroll/' , StudentEnrollmentView.as_view()),
    path('student/enrollments/' ,StudentEnrolledSubjectsView.as_view()),
]


