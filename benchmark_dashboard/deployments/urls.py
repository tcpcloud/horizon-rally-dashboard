from django.conf.urls import patterns
from django.conf.urls import url

from . import views

urlpatterns = patterns(
    '',
    url(r'^index$',
        views.IndexView.as_view(),
        name='index'),
)
