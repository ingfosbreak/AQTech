from django.urls import path
# from .views import Home
from api.views.storage_views import StorageListView, StorageDetailView
from api.views.user_views import StaffUserView, UserUpdateView

urlpatterns = [
    # path('', Home.as_view()),
    path('storages/', StorageListView.as_view(), name='storage-list'),
    path('storages/<int:pk>/', StorageDetailView.as_view(), name='storage-detail'),
    path('user/create/', StaffUserView.as_view(), name='user-create'),
    path('user/update/', UserUpdateView.as_view(), name='user-update')
]