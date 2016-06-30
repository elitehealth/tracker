from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^profile', views.direct, name='profile'),
    url(r'^add_client', views.add_client, name='add_client'),
    url(r'^client_info/(?P<slicer1>[0-9]{4})/(?P<slicer2>[0-9]{2})/$', views.client_table, name='client_info'),
    url(r'^client_info', views.client_info,name='client_info'),
    url(r'^client_chart/(?P<slicer1>[0-9]{4})/(?P<slicer2>[0-9]{2})/$', views.chart, name='client_chart'),
    url(r'^client_chart', views.client_chart_info,name='client_chart_info'),


]
