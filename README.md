# College Management System

This is a full-stack College Management System built using Django Rest Framework and React. The application allows faculty and students to interact with various features such as login , creating student profiles, managing subjects, and editing student information.



1. Clone the repository:
   ```bash
   git clone https://github.com/2Rahul2/college_management_backend
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   
3. Apply migrations to set up the database:
   ```bash
   python manage.py migrate
   ```
4. Run the server:
   ```bash
   python manage.py runserver
   ```

### API Endpoints
- **Authentication:**
  - `POST /api/login/` - Login using username and password
  - `POST /api/logout/` - Logout using username and password
  
- **Student:**
  - `GET /api/student-count/` - Returns count of students.
  - `GET /api/student/<int:pk>/` - Get details of a single student.
  - `POST /api/register/` - Create a new student.
  - `POST /api/student/<int:pk>/` - Update an existing student's profile.

- **Subjects:**
  - `GET /api/subject-with-faculties/` - Get a list of all subjects with the faculties.

- **Student-Subject Management:**
  - `GET /api/student/enrollments/` - Get a list of all all the subject which student has enrolled
  - `POST /api/enroll` - Add a subject in student profile
