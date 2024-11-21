from django.db import models
from django.contrib.auth.models import AbstractUser
# from django.contrib.auth.models import User
from django.contrib.auth.models import BaseUserManager



class User(AbstractUser):
    is_faculty = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Check if the password is already hashed
        if self.password:
            self.set_password(self.password)  # Hash the password
        super().save(*args, **kwargs)  
class Subject(models.Model):
    name = models.CharField(max_length=100)
    # faculties = models.ManyToManyField(Faculty, through='SubjectFaculty')

    def __str__(self):
        return self.name
# Faculty model
class Faculty(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='faculty', null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# Student model
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    blood_group = models.CharField(max_length=5, blank=True, null=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_pic = models.ImageField(upload_to='students/profile_pics/', blank=True, null=True)
    faculties = models.ManyToManyField(Faculty, through='StudentFaculty')



    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.id}"


class SubjectFaculty(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.faculty.first_name} teaches {self.subject.name}"
    
class StudentSubjectEnrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="enrollments")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    enrolled_on = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'subject')  # Prevent duplicate enrollments in the same subject

    def __str__(self):
        return f"{self.student.first_name} enrolled in {self.subject.name} with {self.faculty.first_name}"


class StudentFaculty(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    assigned_on = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.first_name} assigned to {self.faculty.first_name}"