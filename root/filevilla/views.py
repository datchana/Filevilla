from django.shortcuts import render
from django.views.generic.edit import FormView
from .forms import RegisterForm, LoginForm
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.db import IntegrityError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from google.cloud import storage
from root.settings import BASE_DIR
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import cloudstorage as gcs

from io import BytesIO
import os

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
  template_name = 'login.html'
  form_class = LoginForm

  def get(self, request):
    form = self.form_class(request.GET)
    if request.user.is_authenticated:
      return HttpResponseRedirect('home')
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
        return HttpResponseRedirect('home')
      else:
        return render(request, self.template_name, {'error': 'invalid user', 'form': form})
    else:
      return render(request, self.template_name, {'error': 'invalid user', 'form': form})

class FileVilla(LoginRequiredMixin, View):
  login_url = '/'
  template_name = 'home.html'

  def get(self, request):
    name = request.GET.get('name')
    content_type = request.GET.get('content_type')
    storage_client = storage.Client.from_service_account_json(str(BASE_DIR) + '\eternal-calling-287810-b0e92f492121.json')
    blobs = storage_client.list_blobs('filevilla')
    if name and content_type:
      tmp_file = str(BASE_DIR) + '/tmp/' + name
      bucket = storage_client.bucket('filevilla')
      data = ''
      print (name, content_type)
      gcs_file = bucket.blob(name)
      gcs_file.download_to_filename(str(BASE_DIR) + '/tmp/' + name)
      with open(str(BASE_DIR) + '/tmp/' + name, 'rb') as file:
        data = file.read()
      http_response = HttpResponse(data)
      http_response['content-type'] = content_type
      http_response['content-length'] = len(data)
      if os.path.exists(tmp_file):
        os.remove(tmp_file)
      return http_response
    return render(request, self.template_name, {'blobs':blobs})

  def post(self, request):
    try:
      filevilla = request.FILES.get('filevilla')
      path = default_storage.save(filevilla._name, ContentFile(filevilla.read()))
      tmp_file = os.path.join(BASE_DIR, path)
      storage_client = storage.Client.from_service_account_json(str(BASE_DIR) + '\eternal-calling-287810-b0e92f492121.json')
      bucket = storage_client.get_bucket('filevilla')
      blob = bucket.blob(filevilla._name)
      try:
          blob.upload_from_filename(tmp_file)
          if os.path.exists(tmp_file):
              os.remove(tmp_file)
      except UnicodeDecodeError:
          pass
      return HttpResponseRedirect('home')

    except:
      return render(request, self.template_name)
