from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'd4dEndpoint.views.home', name='home'),
    # url(r'^d4dEndpoint/', include('d4dEndpoint.foo.urls')),
    url(r'^similar/(?P<left>\w+)/(?P<relation>\w+)/(?P<right>\w+)/(?P<count>\d+)/(?P<threshold>\d+)/$',
        'd4d.views.similar_endpoint'),
    url(r'^d4d/(?P<query>\w+)/$', 'd4d.views.index'),
    url(r'^visualize/$', 'd4d.views.visualize'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
