from django.urls import path
# from .views import Home
from api.views.storage_views import StorageListView, StorageDetailView

urlpatterns = [
    # path('', Home.as_view()),
    path('storages/', StorageListView.as_view(), name='storage-list'),
    path('storages/<int:pk>/', StorageDetailView.as_view(), name='storage-detail'),
]