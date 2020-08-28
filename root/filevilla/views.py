from django.shortcuts import render
from django.views.generic.edit import FormView
from .forms import RegisterForm, LoginForm
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.db import IntegrityError
from django.contrib.auth import authenticate, login, logout

# Create your views here.

class UserRegister(FormView):
  login_url = '/'
  template_name = 'index.html'
  form_class = RegisterForm


  def get(self, request):
    form_class = self.get_form_class()
    form = self.get_form(form_class)
    return render(request, self.template_name, {'form': form})

  def post(self, request):
    try:
      form = self.form_class(request.POST)
      if form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        confirm_password = form.cleaned_data['confirm_password']
        email = form.cleaned_data['email']
        check_password = form.validate(password, confirm_password)
        if check_password:
          user = User.objects.create_user(
            username=username,
            password=password,
            email=email
          )
          user.save()
          return HttpResponseRedirect('/')
        else:
          return render(request, self.template_name, {'form': form, 'error': 'Password Incorrect'})
      return render(request, self.template_name, {'form': form})
    except IntegrityError:
            return render(request, self.template_name, {'form': form, 'error': 'User already exists'})

class Login(FormView):
  template_name = 'index.html'
  form_class = LoginForm

  def get(self, request):
    form = self.form_class(request.GET)
    if request.user.is_authenticated:
      return HttpResponseRedirect('/')
    else:
      form_class = self.get_form_class()
      form = self.get_form(form_class)
      return self.render_to_response(self.get_context_data(form=form))

  def post(self, request):
    form = self.form_class(request.POST)
    if form.is_valid():
      username = form.cleaned_data['username']
      password = form.cleaned_data['password']
      user = authenticate(username=username, password=password)
      if user is not None:
        login(request, user)
        return HttpResponse('Ok')
      else:
        return render(request, self.template_name, {'error': 'invalid user', 'form': form})
