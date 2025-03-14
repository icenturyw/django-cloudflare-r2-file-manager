from django.urls import path
from . import views

app_name = 'file_manager'

urlpatterns = [
    # 文件相关URL
    path('', views.FileListView.as_view(), name='file_list'),
    path('file/<int:pk>/', views.FileDetailView.as_view(), name='file_detail'),
    path('file/upload/', views.FileUploadView.as_view(), name='file_upload'),
    path('file/<int:pk>/update/', views.FileUpdateView.as_view(), name='file_update'),
    path('file/<int:pk>/delete/', views.FileDeleteView.as_view(), name='file_delete'),
    path('file/<int:pk>/download/', views.download_file, name='file_download'),
    path('file/<int:pk>/preview/', views.file_preview, name='file_preview'),
    path('file/<int:pk>/serve/', views.serve_file, name='serve_file'),
    
    # 分类相关URL
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('category/<int:pk>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('category/create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('category/<int:pk>/update/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('category/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
] 