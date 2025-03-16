from django.urls import path
# from .views import Home
# from api.views.storage_views import StorageListView, StorageDetailView
from api.views import StorageListView, StorageDetailView, StaffUserView, UserUpdateView, UserDetailView, UserListView, StudentCreateView, StudentListView, TeacherCreateView, TeacherListView, SessionView, UserInfoView, VerifyTokenView, CombinedCountView, PieChartStaticView
from api.views.course_views import CompletedCoursesView, CourseCreateView, CourseListView
from api.views.session_views import SessionProgressView
from api.views.student_views import AddStudentView, UserStudentListView
from api.views.user_views import ProfileView
# from api.views.user_views import StaffUserView, UserUpdateView

urlpatterns = [
    # path('', Home.as_view()),
    path('storages/', StorageListView.as_view(), name='storage-list'),
    path('storages/<int:pk>/', StorageDetailView.as_view(), name='storage-detail'),
    path('user/create/', StaffUserView.as_view(), name='user-create'),
    path('user/update/', UserUpdateView.as_view(), name='user-update'),
    path('user/info/', UserInfoView.as_view(), name="user-info"),
    path('user/verify/', VerifyTokenView.as_view(), name="user-verify"),
    path('user/list/', UserListView.as_view(), name="user-list"),
    path('user/<int:user_id>/', UserDetailView.as_view(), name="user-detail"),
    path('user/students/', UserStudentListView.as_view(), name="user-students"),
    path('students/create/', StudentCreateView.as_view(), name="student-create"),
    path("students/add/<int:user_id>/", AddStudentView.as_view(), name="add-student"),
    path('students/', StudentListView.as_view(), name="student-list"),
    path('teachers/create/', TeacherCreateView.as_view(), name="teacher-create"),
    path('teachers/', TeacherListView.as_view(), name="teacher-list"),
    path('sessions/create/', SessionView.as_view(), name="session-create"),
    path("sessions/progress/", SessionProgressView.as_view(), name="session-progress"),
    path("static/count/", CombinedCountView.as_view(), name="combined-count"),
    path("static/pie/", PieChartStaticView.as_view(), name="pie-count"),
    path('courses/', CourseListView.as_view(), name='course-list'),  # GET /courses/
    path('courses/create/', CourseCreateView.as_view(), name='course-create'),  # POST /courses/create/
    path("courses/completed/", CompletedCoursesView.as_view(), name="completed-courses"),
    path("profile/", ProfileView.as_view(), name="profile"),

]