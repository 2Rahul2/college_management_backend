# from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Faculty, Student, Subject, StudentSubjectEnrollment ,User ,StudentFaculty
from .serializers import FacultySerializer, StudentSerializer, SubjectSerializer , SubjectWithFacultiesSerializer , EnrollmentSerializer,StudentSubjectEnrollmentSerializer
from rest_framework import status
from rest_framework.generics import CreateAPIView  ,RetrieveUpdateAPIView

from rest_framework.permissions import AllowAny
from rest_framework.generics import ListAPIView
from .serializers import RegisterSerializer
from rest_framework.exceptions import PermissionDenied

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
def index(request):
    return render(request , "index.html")
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
    permission_classes = [AllowAny] 

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        print("LoginView hit with data:", request.data)
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user) 
            return Response({"message": "Login successful"}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)


# returns whether the user is a student or faculty
class ReturnRole(APIView):
    permission_classes = [IsAuthenticated]
    def get(self , request):
        user = request.user
        print(user)
        print(user.username , user.is_faculty)
        if user.is_faculty:
            return Response({"is_faculty":True})
        return Response({"is_faculty":False})



# returns a list of all subject to which student has enrolled
class StudentEnrolledSubjectsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        student = request.user.student  
        # Get all enrollments for the student
        enrollments = StudentSubjectEnrollment.objects.filter(student=student)  
        
        if not enrollments.exists(): 
            return Response({"message": "No enrolled subjects found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Serialize the enrollments data
        serializer = StudentSubjectEnrollmentSerializer(enrollments, many=True)
        return Response({"enrollments": serializer.data}, status=status.HTTP_200_OK)
    

# saves the student enrollments with the respective faculty selected by the user
class StudentEnrollmentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # list of enrollments from frontend
        data = request.data.get('selectedSubjects', [])

        errors = []
        student = request.user.student

        # loop through the selected subjects and faculties
        for enrollment in data:
            try:
                subject = Subject.objects.get(id=enrollment['subject'])
                faculty = Faculty.objects.get(id=enrollment['faculty'])

                # check if the student is already enrolled in the subject
                if StudentSubjectEnrollment.objects.filter(student=student, subject=subject).exists():
                    errors.append(f"{student.first_name} is already enrolled in {subject.name} with {faculty.first_name}")
                    continue

                # create the enrollment
                StudentSubjectEnrollment.objects.create(student=student, subject=subject, faculty=faculty)

            except Subject.DoesNotExist:
                errors.append(f"Subject with ID {enrollment['subject']} not found.")
            except Faculty.DoesNotExist:
                errors.append(f"Faculty with ID {enrollment['faculty']} not found.")

        if errors:
            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Enrollment successful!"}, status=status.HTTP_201_CREATED)
    

# sends user id back to the user
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


# returns all subject list with the faculties assign to that subject
class SubjectWithFaculties(APIView):
    permission_classes = [IsAuthenticated]


    def get(self , request):
        subjects = Subject.objects.all()
        serialzer = SubjectWithFacultiesSerializer(subjects , many=True)
        return Response({'subjects':serialzer.data} , status=status.HTTP_200_OK)
    

# assigns faculty to a single student
class AssignFacultyToStudentView(APIView):
    # permission_classes = [AllowAny] 
    permission_classes = [IsAuthenticated]


    def post(self, request):
        try:
            # get the authenticated user and ensure they are a faculty member
            user = request.user
            print(user.username)
            if not hasattr(user, 'faculty'):
                print("its not a faculty")
                return Response({"error": "Only faculty can assign themselves to students."}, status=status.HTTP_403_FORBIDDEN)

            faculty = user.faculty  
            
            # get the student_id from the request body
            student_id = request.data.get('student_id')
            if not student_id:
                return Response({"error": "Student ID is required."}, status=status.HTTP_400_BAD_REQUEST)
            
            # ensure the student exists
            try:
                student = Student.objects.get(id=student_id)
            except Student.DoesNotExist:
                return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

            # check if the faculty is already assigned to the student
            if StudentFaculty.objects.filter(student=student, faculty=faculty).exists():
                return Response({"message": "Faculty is already assigned to this student."}, status=status.HTTP_200_OK)

            # create the faculty-student relationship
            StudentFaculty.objects.create(student=student, faculty=faculty)

            return Response({"message": "Faculty assigned to the student successfully.","name":faculty.first_name}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# returns students profile details and handles updatation of profile details(GET and POST)
class StudentDetailView(RetrieveUpdateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]
    # permission_classes = [AllowAny]


    def get_object(self):
        #  get the student object based on the studentId passed in the URL(student id)
        student = super().get_object()  
        user = self.request.user


        print(f"Logged-in user: {user}")
        print(f"Student's user: {student.user}")
        # faculty can view any student's details
        if Faculty.objects.filter(user=user).exists():
            return student
        
        # only the student can edit their own details
        if user == student.user:
            return student
        else:
            print("not allowed")
            Response({"error": "An error occurred:"}, status=status.HTTP_302_FOUND)

    def update(self, request, *args, **kwargs):
        student = self.get_object()  

        # check if the user is the student or a faculty member
        if request.user != student.user and not Faculty.objects.filter(user=request.user).exists():
            raise PermissionDenied("You do not have permission to update this student's details.")
        # ensure that the profile_pic is part of the request.FILES
        if 'profile_pic' in request.FILES:
            print("Profile picture received:", request.FILES['profile_pic'])
        # proceed with the update if the permission check passes
        return super().update(request, *args, **kwargs)


# returns number of students (student count)
class RowCountView(APIView):
    # permission_classes = [AllowAny]
    permission_classes = [IsAuthenticated]

    

    def get(self , request , *args , **kwargs):
        total_count = Student.objects.count()
        return Response({"total_count":total_count})


# each page has 5 students 
class CustomPagination(PageNumberPagination):
    page_size = 5

class StudentListView(ListAPIView):
    # queryset = User.objects.filter(student__isnull=False) 
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    # permission_classes = [AllowAny]
    permission_classes = [IsAuthenticated]

    pagination_class = CustomPagination


# faculty adds student with name , email and password 
class RegisterView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [IsAuthenticated]
    # permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()

        # create a Student entry and associate it with the User
        Student.objects.create(user=user ,first_name=user.username,last_name="")




# UNUSED VIEWS BELOW


# class MyTokenRefreshView(TokenRefreshView):
#     pass
#
# class MyTokenObtainPairView(TokenObtainPairView):
#     pass

# Faculty viewset
class FacultyViewSet(viewsets.ModelViewSet):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]
    # permission_classes = [AllowAny]


    def get_queryset(self):
        user = self.request.user
        return Student.objects.filter(user=user)

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]



    def get_queryset(self):
        user = self.request.user
        return Subject.objects.filter(faculty__user=user)

