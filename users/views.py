from django.http import JsonResponse
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login


def login_page_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Redirect to the home page upon successful login
            return redirect('Dashboard')
        else:
            # Handle incorrect login credentials here (e.g., display an error message)
            pass  # You can add your desired code here, or simply use the 'pass' keyword to do nothing

    return render(request, "users/loginPage.html", {})


@login_required
def settings_view(request):
    user = request.user
    return render(request, 'users/Setting.html', {'user': user})


@login_required
def update_user_info(request):
    print('update_user_info view was called')
    if request.method == 'POST':
        # Get the new user information from the request
        username = request.POST.get('username')
        first_name = request.POST.get('firstName')
        last_name = request.POST.get('lastName')
        email = request.POST.get('email')
        password = request.POST.get('password')

        print('Received the following data:')
        print('Username:', username)
        print('First name:', first_name)
        print('Last name:', last_name)
        print('Email:', email)
        print('Password:', password)

        # Get the current user
        user = User.objects.get(username=request.user.username)

        # Update the user's information
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.set_password(password)
        user.save()

        print('Updated user information:')
        print('Username:', user.username)
        print('First name:', user.first_name)
        print('Last name:', user.last_name)
        print('Email:', user.email)
        print('Password:', user.password)
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@login_required
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('currentPassword')
        new_password = request.POST.get('newPassword')
        confirm_password = request.POST.get('confirmPassword')

        if new_password != confirm_password:
            return JsonResponse({'status': 'error', 'message': 'Passwords do not match'})

        user = authenticate(
            request, username=request.user.username, password=current_password)

        if user is not None:
            user.set_password(new_password)
            user.save()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Incorrect current password'})

    return render(request, 'users/Setting.html')
