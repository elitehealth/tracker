from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^add_sales', views.add_sales, name='add_sales'),
    url(r'^sales_info/(?P<slicer1>[0-9]{4})/(?P<slicer2>[0-9]{2})/$', views.sales_table, name='sales_info'),
    url(r'^sales_info$', views.sales_info,name='sales_info'),
    url(r'^sales_chart/(?P<slicer1>[0-9]{4})/(?P<slicer2>[0-9]{2})/$', views.chart, name='sales_chart'),
    url(r'^sales_chart$', views.sales_chart_info,name='sales_chart_info'),
    url(r'^sales_kpi/(?P<slicer1>[0-9]{4})/(?P<slicer2>[0-9]{2})/$', views.sales_kpi_table, name='sales_kpi_table'),
    url(r'^sales_kpi$', views.sales_kpi,name='sales_kpi'),
    url(r'^sales_kpi_chart/(?P<slicer1>[0-9]{4})/(?P<slicer2>[0-9]{2})/$', views.sales_kpi_chart, name='sales_kpi_chart_detail'),
    url(r'^sales_kpi_chart$', views.sales_kpi_chart_info, name='sales_kpi_chart'),
    url(r'^sales_current_kpi$', views.sales_current_kpi_table, name='sales_current_kpi'),
    url(r'^current_kpi_chart$', views.sales_current_kpi_chart, name='current_kpi_chart'),

]
