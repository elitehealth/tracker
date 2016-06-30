from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^add_appointment', views.add_appointment, name='add_appointment'),

]
