from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm
from .models import User


class UserRegistrationView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('main:main_page')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('users:profile')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, 'Реєстрацію успішно завершено!')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Будь ласка, виправте помилки у формі')
        return super().form_invalid(form)


class UserLoginView(LoginView):
    form_class = UserLoginForm
    template_name = 'users/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('users:profile')

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')
        if not remember_me:
            self.request.session.set_expiry(0)
        messages.success(self.request, f'Ласкаво просимо, {form.get_user().get_full_name() or form.get_user().username}!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Невірне ім'я користувача або пароль")
        return super().form_invalid(form)


def logout_view(request):
    logout(request)
    messages.info(request, 'Ви успішно вийшли з системи')
    return redirect('main:main_page')


class UserProfileView(LoginRequiredMixin, UpdateView):
    """
    Профіль: показує дані + форму редагування в одному місці.
    GET  — відображає профіль з формою
    POST — зберігає зміни
    """
    model = User
    form_class = UserProfileForm
    template_name = 'users/profile.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Передаємо замовлення користувача (останні 10)
        context['orders'] = self.request.user.orders.select_related().prefetch_related('items').order_by('-created_at')[:10]
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Профіль успішно оновлено!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Будь ласка, виправте помилки у формі')
        return super().form_invalid(form)


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Окрема сторінка редагування (якщо потрібна)."""
    model = User
    form_class = UserProfileForm
    template_name = 'users/profile_edit.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Профіль успішно оновлено!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Будь ласка, виправте помилки у формі')
        return super().form_invalid(form)