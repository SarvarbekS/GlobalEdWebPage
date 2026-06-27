from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from .models import ResultPoster, University, Program, News, Event, Certification
import requests


def home(request):
    posters = ResultPoster.objects.all()
    programs = Program.objects.all()
    universities = University.objects.exclude(logo='').order_by('country', 'name')
    news_items = News.objects.all()
    events = Event.objects.all()

    return render(request, 'home.html', {
        'posters': posters,
        'programs': programs,
        'universities': universities,
        'news_items': news_items,
        'events': events
    })


def country_detail(request, country_name):
    universities = University.objects.filter(country=country_name).order_by('name')
    return render(request, 'country_detail.html', {
        'country': country_name,
        'universities': universities
    })


def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": settings.TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
    }
    response = requests.post(url, data=payload, timeout=10)
    response.raise_for_status()


def contact_view(request):
    form_data = {}

    if request.method == 'POST':
        form_data = request.POST

        sender_type = request.POST.get('sender_type', 'student').strip()

        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        message = request.POST.get('message', '').strip()

        country_interest = request.POST.get('country_interest', '').strip()
        study_level = request.POST.get('study_level', '').strip()
        subject = request.POST.get('subject', '').strip()

        institution_name = request.POST.get('institution_name', '').strip()
        organization_type = request.POST.get('organization_type', '').strip()
        partner_country = request.POST.get('partner_country', '').strip()
        partner_subject = request.POST.get('partner_subject', '').strip()

        if not name or not email or not message:
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'contact.html', {'form_data': form_data})

        if sender_type == 'student':
            if not subject:
                messages.error(request, 'Please choose a subject for your student inquiry.')
                return render(request, 'contact.html', {'form_data': form_data})

            telegram_message = f"""
<b>New Student Inquiry</b>

<b>Name:</b> {name}
<b>Email:</b> {email}
<b>Phone:</b> {phone or 'Not provided'}
<b>Country of Interest:</b> {country_interest or 'Not specified'}
<b>Study Level:</b> {study_level or 'Not specified'}
<b>Subject:</b> {subject}

<b>Message:</b>
{message}
""".strip()

        elif sender_type == 'partner':
            if not institution_name or not organization_type or not partner_country or not partner_subject:
                messages.error(request, 'Please complete all required partner fields.')
                return render(request, 'contact.html', {'form_data': form_data})

            telegram_message = f"""
<b>New Partner Inquiry</b>

<b>Contact Person:</b> {name}
<b>Email:</b> {email}
<b>Phone:</b> {phone or 'Not provided'}
<b>Institution / Organization:</b> {institution_name}
<b>Organization Type:</b> {organization_type}
<b>Country:</b> {partner_country}
<b>Collaboration Topic:</b> {partner_subject}

<b>Message:</b>
{message}
""".strip()

        else:
            messages.error(request, 'Invalid inquiry type selected.')
            return render(request, 'contact.html', {'form_data': form_data})

        try:
            send_telegram_message(telegram_message)
            messages.success(request, 'Your message has been sent successfully. We will get back to you shortly.')
            return redirect('contact')
        except Exception:
            messages.error(request, 'Something went wrong while sending your message. Please try again.')
            return render(request, 'contact.html', {'form_data': form_data})

    return render(request, 'contact.html', {'form_data': form_data})

def certifications_view(request):
    certifications = Certification.objects.all()
    return render(request, "certifications.html", {
        "certifications": certifications,
    })