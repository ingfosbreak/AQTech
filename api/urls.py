from django.urls import path
# from .views import Home
# from api.views.storage_views import StorageListView, StorageDetailView
from api.views import StorageListView, StorageDetailView, StaffUserView, UserUpdateView, StudentCreateView, StudentListView, TeacherCreateView, TeacherListView, SessionView, UserInfoView, VerifyTokenView, CombinedCountView
# from api.views.user_views import StaffUserView, UserUpdateView

urlpatterns = [
    # path('', Home.as_view()),
    path('storages/', StorageListView.as_view(), name='storage-list'),
    path('storages/<int:pk>/', StorageDetailView.as_view(), name='storage-detail'),
    path('user/create/', StaffUserView.as_view(), name='user-create'),
    path('user/update/', UserUpdateView.as_view(), name='user-update'),
    path('user/info/', UserInfoView.as_view(), name="user-info"),
    path('user/verify/', VerifyTokenView.as_view(), name="user-verify"),
    path('students/create/', StudentCreateView.as_view(), name="student-create"),
    path('students/', StudentListView.as_view(), name="student-list"),
    path('teachers/create/', TeacherCreateView.as_view(), name="teacher-create"),
    path('teachers/', TeacherListView.as_view(), name="teacher-list"),
    path('sessions/create/', SessionView.as_view(), name="session-create"),
    path("static/count/", CombinedCountView.as_view(), name="combined-count"),
]