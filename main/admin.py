from django.contrib import admin
from .models import ResultPoster, University, Program, News, Event, Certification


@admin.register(ResultPoster)
class ResultPosterAdmin(admin.ModelAdmin):
    list_display = ()
    list_editable = ()
    search_fields = ()
    ordering = ()


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'country',
        'city',
        'university_type',
        'qs_ranking',
        'scholarship_available',
        'created_at',
    )
    list_filter = ('country', 'university_type', 'scholarship_available')
    search_fields = ('name', 'city', 'qs_ranking', 'description')
    ordering = ('country', 'name')
    fieldsets = (
        ('Basic info', {
            'fields': ('name', 'country', 'city', 'university_type', 'logo', 'qs_ranking')
        }),
        ('Details', {
            'fields': ('tuition_min', 'tuition_max', 'scholarship_available', 'description')
        }),
        ('Media', {
            'fields': ('campus_tour_url',)
        }),
    )


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name', 'description', 'benefits')
    ordering = ('name',)


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_at', 'source', 'created_at')
    search_fields = ('title', 'summary', 'body', 'source')
    list_filter = ('published_at', 'source')
    ordering = ('-published_at', '-created_at')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'location', 'featured', 'created_at')
    list_filter = ('featured', 'start_date', 'location')
    search_fields = ('title', 'subtitle', 'summary', 'body', 'location')
    ordering = ('-featured', '-start_date', '-created_at')


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "issued_by", "issued_date", "created_at")
    search_fields = ("title", "category", "issued_by")
    list_filter = ("category", "issued_date", "created_at")