from django.urls import path
from . import views
from .views import country_detail, contact_view, certifications_view
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('', views.home, name='home'),
    path('country/<str:country_name>/', country_detail, name='country_detail'),
    path('contact/', contact_view, name='contact'),
    path("certifications/", certifications_view, name="certifications"),
    path("api/consultation-slots/", views.consultation_slots, name="consultation_slots"),
    path("api/book-consultation/", views.book_consultation, name="book_consultation"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)