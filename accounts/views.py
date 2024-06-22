from django.shortcuts import render
from django.contrib import messages
from django.views.generic import FormView
from .forms import UserRegistrationForm,UserUpdateForm,PasswordUpdateForm
from django.contrib.auth import login, logout
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView,PasswordChangeView
from django.views import View
from django.shortcuts import redirect
from django.conf import settings
from django.core.mail import send_mail

class UserRegistrationView(FormView):
    template_name = 'accounts/user_registration.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('profile')
    
    def form_valid(self,form):
        print(form.cleaned_data)
        user = form.save()
        login(self.request, user)
        print(user)
        return super().form_valid(form) # form_valid function call hobe jodi sob thik thake
    

class UserLoginView(LoginView):
    template_name = 'accounts/user_login.html'
    def get_success_url(self):
        return reverse_lazy('home')

# class UserLogoutView(LogoutView):
#     def get_success_url(self):
#         if self.request.user.is_authenticated:
#             logout(self.request)
#         return reverse_lazy('home')

def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('home')

class UserBankAccountUpdateView(View):
    template_name = 'accounts/profile.html'

    def get(self, request):
        form = UserUpdateForm(instance=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirect to the user's profile page
        return render(request, self.template_name, {'form': form})
    
    
class PassWordUpdateView(PasswordChangeView):
    form_class = PasswordUpdateForm
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('profile')
    def form_valid(self, form):
        messages.success(self.request, 'Your password was successfully updated!')
        subject = 'Password Changed'
        message = f'Hi {self.request.user.username}, Your password is changed successfully'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [self.request.user.email ]
        send_mail( subject, message, email_from, recipient_list )
        return super().form_valid(form)   