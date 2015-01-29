from django.conf.urls import url

from Web import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^intro$', views.intro, name='intro'),
    url(r'^tweets$', views.tweets, name='tweets'),
    url(r'^search$', views.search_and_classify, name='search_and_classify'),
    url(r'^classify$', views.classify_by_query, name='classify_by_query'),
    url(r'^rest/classify$', views.classify_by_query_rest, name='classify_by_query'),
]
