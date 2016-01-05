from django.conf.urls import include, url, patterns
from django.contrib import admin

from django.views.generic import TemplateView
urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='home'),
    url(r'^twitterapp/', include('twitterapp.urls'))
)
