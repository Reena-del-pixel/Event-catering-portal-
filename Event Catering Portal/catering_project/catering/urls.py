from django.contrib import admin # [FIX] एडमिन को इम्पोर्ट करने का सही तरीका
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # [FIX] एडमिन साइट का सही रास्ता
    path('admin/', admin.site.urls),
    
    # खाली पाथ पर लॉगिन पेज सेट किया गया है ताकि सबसे पहले लॉगिन ही खुले
    path('', views.login_page, name='login'), 
    
    # बाकी सारे पेजों के पाथ नीचे इस तरह हैं
    path('home/', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('booking/<str:event_type>/', views.booking, name='booking'),
    path('payment/<int:id>/', views.payment, name='payment'),
    path('op-page/<int:id>/', views.op_page, name='op_page'),
    path('order-details/<int:id>/', views.get_order_details, name='get_order_details'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('profile/', views.profile, name='profile'),
    path('contact/', views.contact_us, name='contact_us'),
    path('about/', views.about_us, name='about_us'),
    path('logout/', views.logout_page, name='logout'),
    path('booking/update/<int:booking_id>/', views.update_booking, name='update_booking'),
    path('booking/cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
]


# Media and Static Files serving in Development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 