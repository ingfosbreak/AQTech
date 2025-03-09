from django.urls import path
# from .views import Home
# from api.views.storage_views import StorageListView, StorageDetailView
from api.views import StorageListView, StorageDetailView, StaffUserView, UserUpdateView, UserDetailView, UserListView, StudentCreateView, StudentListView, TeacherCreateView, TeacherListView, SessionView, UserInfoView, VerifyTokenView, CombinedCountView, PieChartStaticView
from api.views.student_views import AddStudentView
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
    path('students/create/', StudentCreateView.as_view(), name="student-create"),
    path("students/add/<int:user_id>/", AddStudentView.as_view(), name="add-student"),
    path('students/', StudentListView.as_view(), name="student-list"),
    path('teachers/create/', TeacherCreateView.as_view(), name="teacher-create"),
    path('teachers/', TeacherListView.as_view(), name="teacher-list"),
    path('sessions/create/', SessionView.as_view(), name="session-create"),
    path("static/count/", CombinedCountView.as_view(), name="combined-count"),
    path("static/pie/", PieChartStaticView.as_view(), name="pie-count"),
]