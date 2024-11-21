from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
# from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .models import Faculty, Student, Subject, StudentSubjectEnrollment ,User ,StudentFaculty
from .serializers import FacultySerializer, StudentSerializer, SubjectSerializer , SubjectWithFacultiesSerializer , EnrollmentSerializer,StudentSubjectEnrollmentSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.generics import CreateAPIView ,RetrieveAPIView ,RetrieveUpdateAPIView
# from django.contrib.auth.models import User

from rest_framework.permissions import AllowAny
from rest_framework.generics import ListAPIView
from .serializers import UserSerializer
from .serializers import RegisterSerializer
from rest_framework.exceptions import PermissionDenied

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination


from django.contrib.auth import authenticate, login, logout

from .customPermission import IsFaculty
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


class Health(APIView):
    permission_classes = [AllowAny]
    def get(self, request, *args, **kwargs):
        # Return a 200 OK response with no content
        return Response(status=status.HTTP_200_OK)

class LogoutView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        logout(request)  # Log the user out
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
# @method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    permission_classes = [AllowAny]  # Anyone can access this view

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        print("LoginView hit with data:", request.data)
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)  # Log the user in
            return Response({"message": "Login successful"}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

class ReturnRole(APIView):
    permission_classes = [IsAuthenticated]
    def get(self , request):
        user = request.user
        print(user)
        print(user.username , user.is_faculty)
        if user.is_faculty:
            return Response({"is_faculty":True})
        return Response({"is_faculty":False})


class StudentEnrolledSubjectsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        student = request.user.student  # Access the logged-in student's instance
        enrollments = StudentSubjectEnrollment.objects.filter(student=student)  # Get all enrollments for the student
        
        if not enrollments.exists():  # Check if there are any enrollments
            return Response({"message": "No enrolled subjects found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Serialize the enrollments data
        serializer = StudentSubjectEnrollmentSerializer(enrollments, many=True)
        return Response({"enrollments": serializer.data}, status=status.HTTP_200_OK)

class StudentEnrollmentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data.get('selectedSubjects', [])  # List of enrollments from frontend

        errors = []
        student = request.user.student  # Assuming the logged-in user is a student

        # Loop through the selected subjects and faculties
        for enrollment in data:
            try:
                subject = Subject.objects.get(id=enrollment['subject'])
                faculty = Faculty.objects.get(id=enrollment['faculty'])

                # Check if the student is already enrolled in the subject
                if StudentSubjectEnrollment.objects.filter(student=student, subject=subject).exists():
                    errors.append(f"{student.first_name} is already enrolled in {subject.name} with {faculty.first_name}")
                    continue

                # Create the enrollment
                StudentSubjectEnrollment.objects.create(student=student, subject=subject, faculty=faculty)

            except Subject.DoesNotExist:
                errors.append(f"Subject with ID {enrollment['subject']} not found.")
            except Faculty.DoesNotExist:
                errors.append(f"Faculty with ID {enrollment['faculty']} not found.")

        if errors:
            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Enrollment successful!"}, status=status.HTTP_201_CREATED)
class ReturnUserid(APIView):
    permission_classes =[IsAuthenticated]

    def get(self , request):
        user = request.user
        print(user)
        try:
            student = Student.objects.get(user=user)
            return Response({"user_id":student.id}) 
        except:
            return Response({"user_id":None}) 

class SubjectWithFaculties(APIView):
    permission_classes = [IsAuthenticated]


    def get(self , request):
        subjects = Subject.objects.all()
        serialzer = SubjectWithFacultiesSerializer(subjects , many=True)
        return Response({'subjects':serialzer.data} , status=status.HTTP_200_OK)
class AssignFacultyToStudentView(APIView):
    # permission_classes = [AllowAny]  # Ensure only logged-in users can access this view
    permission_classes = [IsAuthenticated]


    def post(self, request):
        try:
            # Get the authenticated user and ensure they are a faculty member
            user = request.user
            print(user.username)
            if not hasattr(user, 'faculty'):
                print("its not a faculty")
                return Response({"error": "Only faculty can assign themselves to students."}, status=status.HTTP_403_FORBIDDEN)

            faculty = user.faculty  # Get the faculty object linked to the logged-in user
            
            # Get the student_id from the request body
            student_id = request.data.get('student_id')
            if not student_id:
                return Response({"error": "Student ID is required."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Ensure the student exists
            try:
                student = Student.objects.get(id=student_id)
            except Student.DoesNotExist:
                return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

            # Check if the faculty is already assigned to the student
            if StudentFaculty.objects.filter(student=student, faculty=faculty).exists():
                return Response({"message": "Faculty is already assigned to this student."}, status=status.HTTP_200_OK)

            # Create the faculty-student relationship
            StudentFaculty.objects.create(student=student, faculty=faculty)

            return Response({"message": "Faculty assigned to the student successfully.","name":faculty.first_name}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class StudentDetailView(RetrieveUpdateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]
    # permission_classes = [AllowAny]


    def get_object(self):
        student = super().get_object()  # Get the student object based on the studentId passed in the URL
        user = self.request.user
        # Faculty can view any student's details
        if Faculty.objects.filter(user=user).exists():
            return student
        
        # Only the student can edit their own details
        if user == student.user:
            return student
        else:
            print("not allowed")
            Response({"error": f"An error occurred:"}, status=status.HTTP_302_FOUND)

    def update(self, request, *args, **kwargs):
        student = self.get_object()  # Get the student object

        # Check if the user is the student or a faculty member
        if request.user != student.user and not Faculty.objects.filter(user=request.user).exists():
            raise PermissionDenied("You do not have permission to update this student's details.")
        # Ensure that the profile_pic is part of the request.FILES
        if 'profile_pic' in request.FILES:
            print("Profile picture received:", request.FILES['profile_pic'])
        # Proceed with the update if the permission check passes
        return super().update(request, *args, **kwargs)

class RowCountView(APIView):
    # permission_classes = [AllowAny]
    permission_classes = [IsAuthenticated]

    

    def get(self , request , *args , **kwargs):
        total_count = Student.objects.count()
        return Response({"total_count":total_count})


class CustomPagination(PageNumberPagination):
    page_size = 5

class StudentListView(ListAPIView):
    # queryset = User.objects.filter(student__isnull=False) 
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    # permission_classes = [AllowAny]
    permission_classes = [IsAuthenticated]

    pagination_class = CustomPagination

class RegisterView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [IsAuthenticated]
    # permission_classes = [AllowAny]

    def perform_create(self, serializer):
        # Save the User instance
        user = serializer.save()

        # Create a Student entry and associate it with the User
        Student.objects.create(user=user ,first_name=user.username,last_name="")


# class MyTokenRefreshView(TokenRefreshView):
#     pass
# # Login API View (Token-based Authentication)
# class MyTokenObtainPairView(TokenObtainPairView):
#     pass

# Faculty viewset
class FacultyViewSet(viewsets.ModelViewSet):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]


# Student viewset
class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]
    # permission_classes = [AllowAny]


    def get_queryset(self):
        user = self.request.user
        return Student.objects.filter(user=user)

# Subject viewset
class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]
    # permission_classes = [AllowAny]


    def get_queryset(self):
        user = self.request.user
        return Subject.objects.filter(faculty__user=user)

