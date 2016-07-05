from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^add_appointment', views.add_appointment, name='add_appointment'),
    url(r'^appointment_info/(?P<slicer1>[0-9]{4})/(?P<slicer2>[0-9]{2})/$', views.appointment_table, name='appointment_info'),
    url(r'^appointment_info$', views.appointment_info,name='appointment_info'),
    url(r'^appointment_chart/(?P<slicer1>[0-9]{4})/(?P<slicer2>[0-9]{2})/$', views.appointment_chart, name='appointment_chart'),
    url(r'^appointment_chart$', views.appointment_chart_info,name='appointment_chart_info'),

]
