from django.contrib import admin

from .models import Faculty , Student ,Subject, StudentSubjectEnrollment ,StudentFaculty  ,User

# Register your models here.
admin.site.register(Faculty)
admin.site.register(User)

admin.site.register(Student)
admin.site.register(Subject)
# admin.site.register(StudentSubject)

admin.site.register(StudentFaculty)
admin.site.register(StudentSubjectEnrollment)

