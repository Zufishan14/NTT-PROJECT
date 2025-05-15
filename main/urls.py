from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('change-password/', views.change_password, name='change_password'),
    path('tables/', views.tables, name='tables'),
    path('excel-management/', views.excel_management, name='excel_management'),
    path('upload-excel/', views.upload_excel, name='upload_excel'),
    path('view-excel/<int:file_id>/', views.view_excel, name='view_excel'),
    path('edit-excel/<int:file_id>/', views.edit_excel, name='edit_excel'),
    path('delete-excel/<int:file_id>/', views.delete_excel, name='delete_excel'),
    path('download-excel/<int:file_id>/', views.download_excel, name='download_excel'),
    path('search-excel/', views.search_excel, name='search_excel'),
] 