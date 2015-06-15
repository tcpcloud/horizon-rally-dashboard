from django.conf.urls import patterns
from django.conf.urls import url

from . import views

urlpatterns = patterns(
    '',
    url(r'^task/select$',
        views.SelectScenarioView.as_view(), name='task_select'),
    url(r'^task/edit$',
        views.CreateTaskView.as_view(), name='task_create'),
    url(r'^task/(?P<task_id>[^/]+)/detail$',
        views.DetailTaskView.as_view(), name='detail'),
    url(r'^task/(?P<task_id>[^/]+)/report$',
        views.DownloadTaskReportView.as_view(), name='report'),
    url(r'^',
        views.TaskIndexView.as_view(),
        name='index'),
)
