import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model
from django.shortcuts import render, redirect

from accounts.forms import UserLoginForm, UserRegistrationForm, UserUpdateForm, ContactForm
from scraping.models import Error

User = get_user_model()


def login_view(request):
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        data = form.cleaned_data
        email = data.get('email')
        password = data.get('password')
        user = authenticate(request, email=email, password=password)

        login(request, user)
        return redirect('home')
    return render(request, 'accounts/login.html', {'form': form})


from django.contrib.auth import logout


def logout_view(request):
    logout(request)
    return redirect('home')


def register_view(request):
    form = UserRegistrationForm(request.POST or None)
    if form.is_valid():
        new_user = form.save(commit=False)
        new_user.set_password(form.cleaned_data['password'])
        new_user.save()
        messages.success(request, 'New user has been registered')
        return render(request, 'accounts/registration_complete.html', {'new_user': new_user})
    messages.error(request, 'This email already has benn taken')
    return render(request, 'accounts/register.html', {'form': form})


def user_update_view(request):
    contact_form = ContactForm()
    if request.user.is_authenticated:
        user = request.user
        if request.method == 'POST':
            form = UserUpdateForm(request.POST or None)
            if form.is_valid():
                data = form.cleaned_data
                user.city = data['city']
                user.language = data['language']
                user.send_email = data['send_email']
                user.save()
                messages.success(request, 'New user settings are saved')
                return redirect('accounts:update')

        form = UserUpdateForm(initial={'city': user.city, 'language': user.language, 'send_email': user.send_email})
        return render(request, 'accounts/update.html', {'form': form, 'contact_form': contact_form})
    else:
        return redirect('accounts:login')


def user_delete_view(request):
    if request.user.is_authenticated:
        user = request.user
        if request.method == 'GET':
            qs = User.objects.get(pk=user.pk)
            qs.delete()
    return redirect('home')


def new_search_params_view(request):
    if request.method == 'POST':
        contact_form = ContactForm(request.POST or None)
        if contact_form.is_valid():
            data = contact_form.cleaned_data
            city = data.get('city')
            language = data.get('language')
            email = data.get('email')
            qs = Error.objects.filter(timestamp=datetime.date.today())
            if qs.exists():
                query = qs.first()
                data_for_new_search = query.data.get('user_desirable_search_params', [])
                data_for_new_search.append({'city': city, 'language': language, 'email': email})
                query.data['user_desirable_search_params'] = data_for_new_search
                query.save()
            else:
                data_for_new_search = [{'city': city, 'language': language, 'email': email}]
                Error(data=f"user_desirable_search_params: {data_for_new_search}").save()
            messages.success(request, 'Данные отправлены администрации')
            return redirect('accounts:update')
        else:
            return redirect('accounts:update')
    else:
        return redirect('accounts:login')
