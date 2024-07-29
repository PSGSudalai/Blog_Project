from django.conf import settings
from django.urls import path
from . import views
from django.conf.urls.static import static

urlpatterns = [

    path('',views.index,name="home"),
    path('blog/<int:pk>',views.blogs,name='blog'),

    path('Signin',views.Signin,name='Signin' ),
    path('Signup',views.regist_view,name='Signup' ),
    path('Signout',views.Signout,name='Signout' ),

    path('create_blog',views.create_Blog,name='create' ),
    path('edit_blog/<int:pk>',views.edit_Blog,name='edit' ),
    path('delete_blog/<int:pk>',views.delete_Blog,name='delete' ),

    path('custom_tag',views.create_tag,name='custom_tag' ),
    path('profile/',views.profile,name='profile'),

    # path('create_comment/<int:pk>',views.create_Cmt,name='create_cmt' ),
    path('edit_comment/<int:pk>/<int:pk1>',views.edit_Cmt,name='edit_cmt' ),
    path('delete_comment/<int:pk>/<int:pk1>',views.delete_Cmt,name='delete_cmt' ),

    path('approve_blog/<int:pk>',views.approve,name='approve_blog'),
    path('reject_blog/<int:pk>',views.reject,name='reject_blog'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

 