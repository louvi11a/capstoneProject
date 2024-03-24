import hashlib
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy
from django.contrib.auth.forms import AuthenticationForm


# def login_page_view(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         # Print the hashed password
#         print(hashlib.sha256(password.encode()).hexdigest())
#         user = authenticate(request, username=username, password=password)

#         if user is not None:
#             login(request, user)
#             # Redirect to the home page upon successful login
#             return redirect('Dashboard')
#         else:
#             # Handle incorrect login credentials here (e.g., display an error message)
#             pass  # You can add your desired code here, or simply use the 'pass' keyword to do nothing

#     return render(request, "users/loginPage.html", {})

def login_page_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # messages.success(request, 'You have successfully logged in.')
            return redirect('Dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()

    return render(request, "users/loginPage.html", {'form': form})


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
    print('change_password view was called')  # New print statement
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            print('Form is valid')  # New print statement
            user = form.save()
            print(user.password)  # Print the hashed password
            update_session_auth_hash(request, user)  # Important!
            messages.success(
                request, 'Your password was successfully updated!')
            return JsonResponse({'status': 'success'})
        else:
            print('Form is not valid')  # New print statement
            print(form.errors)  # Print form errors
            return JsonResponse({'status': 'error', 'message': 'Failed to change password. Please try again.', 'errors': form.errors}, status=400)
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'users/Setting.html', {
        'form': form
    })


class CustomPasswordResetView(PasswordResetView):
    template_name = 'users/password_reset_form.html'
    email_template_name = 'users/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')
