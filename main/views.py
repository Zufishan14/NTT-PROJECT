from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, update_session_auth_hash, logout
from django.contrib import messages
from .models import UserProfile, ExcelFile
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import FileResponse, JsonResponse
import os
import pandas as pd
from django.conf import settings
from django.db.models import Q

def is_admin(user):
    return user.is_staff

# Create your views here.

@login_required
def index(request):
    return render(request, 'main/index.html')

def login(request):
    next_url = request.GET.get('next', 'index')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        is_admin_login = request.POST.get('is_admin') == 'true'
        next_url = request.POST.get('next', 'index')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if is_admin_login and not user.is_staff:
                messages.error(request, 'You do not have administrator privileges.')
                return render(request, 'main/pages-login.html', {'next': next_url})
            
            auth_login(request, user)
            if is_admin_login:
                return redirect('admin:index')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'main/pages-login.html', {'next': next_url})

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        can_view = request.POST.get('can_view') == 'true'
        can_upload = request.POST.get('can_upload') == 'true'

        # Validation
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'main/pages-register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'main/pages-register.html')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'main/pages-register.html')

        # Create user
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            # Update UserProfile with privileges
            user.userprofile.can_view = can_view
            user.userprofile.can_upload = can_upload
            user.userprofile.save()
            messages.success(request, 'Registration successful! Please login.')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Error creating user: {str(e)}')
            return render(request, 'main/pages-register.html')

    return render(request, 'main/pages-register.html')

@login_required
def profile(request):
    if request.method == 'POST':
        # Update user information
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()

        # Update user profile
        user_profile = user.userprofile
        user_profile.phone = request.POST.get('phone', '')
        user_profile.address = request.POST.get('address', '')
        
        # Handle profile picture upload
        profile_pic = request.FILES.get('profile_picture')
        if profile_pic:
            user_profile.profile_picture = profile_pic
            
        user_profile.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')

    # Fetch the user profile for the template
    user_profile = request.user.userprofile
    return render(request, 'main/users-profile.html', {'user_profile': user_profile})

@login_required
@user_passes_test(is_admin)
def manage_users(request):
    users = User.objects.all().select_related('userprofile')
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        can_view = request.POST.get('can_view') == 'on'
        can_upload = request.POST.get('can_upload') == 'on'
        
        try:
            user = User.objects.get(id=user_id)
            user.userprofile.can_view = can_view
            user.userprofile.can_upload = can_upload
            user.userprofile.save()
            messages.success(request, f'Privileges updated for {user.username}')
        except User.DoesNotExist:
            messages.error(request, 'User not found')
            
    return render(request, 'main/manage-users.html', {'users': users})

@login_required
def change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        # Validate old password
        if not request.user.check_password(old_password):
            messages.error(request, 'Your current password is incorrect.')
            return redirect('profile')

        # Validate new password
        if new_password1 != new_password2:
            messages.error(request, 'The two password fields didn\'t match.')
            return redirect('profile')

        try:
            validate_password(new_password1, request.user)
        except ValidationError as e:
            messages.error(request, '\n'.join(e.messages))
            return redirect('profile')

        # Change password
        request.user.set_password(new_password1)
        request.user.save()
        update_session_auth_hash(request, request.user)
        messages.success(request, 'Your password was successfully updated!')
        return redirect('profile')

    return redirect('profile')

@login_required
def tables(request):
    return render(request, 'main/tables-general.html')

@login_required
def excel_management(request):
    if request.method == 'POST':
        excel_file = request.FILES.get('excel_file')
        has_header = request.POST.get('has_header') == 'on'

        if excel_file:
            if not excel_file.name.endswith(('.xlsx', '.xls')):
                messages.error(request, 'Please upload only Excel files (.xlsx or .xls)')
                return redirect('excel_management')

            try:
                excel = ExcelFile.objects.create(
                    user=request.user,
                    file=excel_file,
                    has_header=has_header
                )
                messages.success(request, 'File uploaded successfully!')
            except Exception as e:
                messages.error(request, f'Error uploading file: {str(e)}')
        else:
            messages.error(request, 'Please select a file to upload.')

    # Get all files for admin, only user's files for regular users
    if request.user.is_staff:
        excel_files = ExcelFile.objects.all().order_by('-upload_date')
    else:
        excel_files = ExcelFile.objects.filter(user=request.user).order_by('-upload_date')

    return render(request, 'main/excel-management.html', {'excel_files': excel_files})

@login_required
def view_excel(request, file_id):
    excel_file = get_object_or_404(ExcelFile, id=file_id)
    
    # Check if user has permission to view the file
    if not request.user.is_staff and excel_file.user != request.user:
        messages.error(request, 'You do not have permission to view this file.')
        return redirect('excel_management')

    try:
        # Read the Excel file
        df = pd.read_excel(excel_file.file.path, header=0 if excel_file.has_header else None)
        
        # Convert DataFrame to HTML
        table_html = df.to_html(classes='table table-striped table-bordered', index=False)
        
        return render(request, 'main/view-excel.html', {
            'excel_file': excel_file,
            'table_html': table_html,
            'columns': df.columns.tolist() if excel_file.has_header else None,
            'data': df.values.tolist()
        })
    except Exception as e:
        messages.error(request, f'Error reading Excel file: {str(e)}')
        return redirect('excel_management')

@login_required
@user_passes_test(is_admin)
def edit_excel(request, file_id):
    excel_file = get_object_or_404(ExcelFile, id=file_id)
    
    if request.method == 'POST':
        try:
            # Read the Excel file
            df = pd.read_excel(excel_file.file.path, header=0 if excel_file.has_header else None)
            
            # Process the form data
            for key, value in request.POST.items():
                if key.startswith('cell_'):
                    # Extract row and column from the key (format: cell_row_col)
                    _, row, col = key.split('_')
                    row, col = int(row), int(col)
                    
                    # Update the cell value
                    if excel_file.has_header:
                        df.iloc[row, col] = value
                    else:
                        df.iloc[row, col] = value
            
            # Save the updated DataFrame back to Excel
            df.to_excel(excel_file.file.path, index=False, header=excel_file.has_header)
            messages.success(request, 'File updated successfully!')
            return redirect('view_excel', file_id=file_id)
            
        except Exception as e:
            messages.error(request, f'Error updating Excel file: {str(e)}')
    
    try:
        # Read the Excel file for display
        df = pd.read_excel(excel_file.file.path, header=0 if excel_file.has_header else None)
        
        return render(request, 'main/edit-excel.html', {
            'excel_file': excel_file,
            'columns': df.columns.tolist() if excel_file.has_header else None,
            'data': df.values.tolist()
        })
    except Exception as e:
        messages.error(request, f'Error reading Excel file: {str(e)}')
        return redirect('excel_management')

@login_required
def download_excel(request, file_id):
    excel_file = get_object_or_404(ExcelFile, id=file_id)
    
    # Check if user has permission to download the file
    if not request.user.is_staff and excel_file.user != request.user:
        messages.error(request, 'You do not have permission to download this file.')
        return redirect('excel_management')
    
    response = FileResponse(excel_file.file, as_attachment=True)
    return response

@login_required
def delete_excel(request, file_id):
    excel_file = get_object_or_404(ExcelFile, id=file_id)
    
    # Check if user has permission to delete the file
    if not request.user.is_staff and excel_file.user != request.user:
        messages.error(request, 'You do not have permission to delete this file.')
        return redirect('excel_management')
    
    try:
        # Delete the file from storage
        if excel_file.file:
            if os.path.isfile(excel_file.file.path):
                os.remove(excel_file.file.path)
        # Delete the database record
        excel_file.delete()
        messages.success(request, 'File deleted successfully!')
    except Exception as e:
        messages.error(request, f'Error deleting file: {str(e)}')
    return redirect('excel_management')

@login_required
def search_excel(request):
    # Get all unique financial years for the dropdown
    financial_years = ExcelFile.objects.values_list('financial_year', flat=True).distinct().order_by('-financial_year')
    
    # Initialize the query
    query = Q()
    
    # Add search criteria if provided
    if request.GET.get('client_po'):
        query &= Q(client_po_number__icontains=request.GET['client_po'])
    
    if request.GET.get('po_date'):
        query &= Q(client_po_date=request.GET['po_date'])
    
    if request.GET.get('sales_doc'):
        query &= Q(sales_document__icontains=request.GET['sales_doc'])
    
    if request.GET.get('financial_year'):
        query &= Q(financial_year=request.GET['financial_year'])
    
    # Get the filtered files
    excel_files = ExcelFile.objects.filter(query).order_by('-upload_date')
    
    context = {
        'excel_files': excel_files,
        'financial_years': financial_years,
    }
    return render(request, 'main/search-excel.html', context)

@login_required
def upload_excel(request):
    if not request.user.userprofile.can_upload:
        messages.error(request, "You don't have permission to upload files.")
        return redirect('index')
    
    if request.method == 'POST':
        excel_file = request.FILES.get('excel_file')
        has_header = request.POST.get('has_header') == 'on'
        financial_year = request.POST.get('financial_year')
        client_po_number = request.POST.get('client_po_number')
        client_po_date = request.POST.get('client_po_date')
        sales_document = request.POST.get('sales_document')
        
        if not all([excel_file, client_po_number, client_po_date, sales_document]):
            messages.error(request, "All fields are required.")
            return redirect('excel_management')
        
        try:
            # Check for duplicate entries
            existing_file = ExcelFile.objects.filter(
                client_po_number=client_po_number,
                client_po_date=client_po_date,
                sales_document=sales_document
            ).first()
            
            if existing_file:
                # Update the existing file
                existing_file.file = excel_file
                existing_file.has_header = has_header
                existing_file.financial_year = financial_year
                existing_file.save()
                messages.success(request, "File updated successfully.")
            else:
                # Create new file
                excel_file_obj = ExcelFile(
                    user=request.user,
                    file=excel_file,
                    has_header=has_header,
                    financial_year=financial_year,
                    client_po_number=client_po_number,
                    client_po_date=client_po_date,
                    sales_document=sales_document
                )
                excel_file_obj.save()
                messages.success(request, "File uploaded successfully.")
            
            return redirect('excel_management')
            
        except Exception as e:
            messages.error(request, f"Error uploading file: {str(e)}")
            return redirect('excel_management')
    
    # Get all unique financial years for the dropdown
    financial_years = ExcelFile.objects.values_list('financial_year', flat=True).distinct().order_by('-financial_year')
    
    context = {
        'financial_years': financial_years,
    }
    return render(request, 'main/upload-excel.html', context)

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    # Redirect to login page
    return redirect('login')
