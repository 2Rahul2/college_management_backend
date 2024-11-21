from rest_framework import serializers
from .models import Faculty, Student, Subject ,User  ,StudentSubjectEnrollment
# from django.contrib.auth.models import User



# app/serializers.py



class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__' 

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']  # Adjust fields as needed

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email']
    
    def create(self, validated_data):
        # Create the user
        user = User(
            username=validated_data['username'],
            email=validated_data['email']
        )
        # Explicitly hash the password
        user.set_password(validated_data['password'])
        user.save()
        return user

class EnrollmentSerializer(serializers.Serializer):
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all())
    faculty = serializers.PrimaryKeyRelatedField(queryset=Faculty.objects.all())

    def create(self, validated_data):
        student = self.context['request'].user.student
        subject = validated_data['subject']
        faculty = validated_data['faculty']

        # Save enrollment
        student.subjects.add(subject)
        student.faculties.add(faculty)
        return validated_data
    
class StudentSubjectEnrollmentSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    faculty_name = serializers.CharField(source='faculty.first_name', read_only=True)
    faculty_contact_number = serializers.CharField(source='faculty.contact_number', read_only=True)

    class Meta:
        model = StudentSubjectEnrollment
        fields = ['subject_name', 'faculty_name', 'faculty_contact_number', 'enrolled_on' ,'id']   
# Faculty serializer
class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = ['id', 'first_name', 'last_name', 'contact_number']


class SubjectWithFacultiesSerializer(serializers.ModelSerializer):
    faculties = FacultySerializer(source='faculty', many=True)

    class Meta:
        model = Subject
        fields = ['id', 'name', 'faculties']
# Student serializer
class StudentSerializer(serializers.ModelSerializer):
    profile_pic = serializers.ImageField(required=False)
    faculties = FacultySerializer(many=True, read_only=True)

    class Meta:
        model = Student
        fields = ['id', 'first_name', 'last_name', 'dob', 'gender', 'blood_group', 'contact_number', 'address', 'profile_pic', 'faculties']
    
# Subject serializer
class SubjectSerializer(serializers.ModelSerializer):
    faculty = FacultySerializer(read_only=True)
    
    class Meta:
        model = Subject
        fields = ['id', 'name', 'faculty']

# Enrollment serializer
# class StudentSubjectSerializer(serializers.ModelSerializer):
#     student = StudentSerializer(read_only=True)
#     subject = SubjectSerializer(read_only=True)
    
#     class Meta:
#         model = StudentSubject
#         fields = ['id', 'student', 'subject', 'enrolled_on']
