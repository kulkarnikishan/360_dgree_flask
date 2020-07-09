from django.conf.urls.defaults import *

urlpatterns = patterns('reporting.views',
    url('^$', 'report_list', name='reporting-list'),
    url('^(?P<slug>.*)/csv/$', 'get_csv', name='export-to-csv'),
    url('^(?P<slug>.*)/plot/$', 'see_plot', name='see-plot'),
    url('^(?P<slug>.*)/$', 'view_report', name='reporting-view'),
)