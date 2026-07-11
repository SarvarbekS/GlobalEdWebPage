from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from .models import ResultPoster, University, Program, News, Event, Certification, ConsultationBooking
import requests
from django.db import models
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

import datetime
import json



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


def get_tomorrow_uzb():
    """Returns tomorrow's date based on Uzbekistan time (UTC+5)."""
    utc_now = datetime.datetime.utcnow()
    uzb_now = utc_now + datetime.timedelta(hours=5)
    return (uzb_now + datetime.timedelta(days=1)).date()


def consultation_slots(request):
    """Returns tomorrow's date and the list of already-booked time slots."""
    tomorrow = get_tomorrow_uzb()
    booked = list(
        ConsultationBooking.objects.filter(booking_date=tomorrow)
        .values_list("time_slot", flat=True)
    )
    return JsonResponse({"date": str(tomorrow), "booked": booked})


@csrf_protect
@require_POST
def book_consultation(request):
    """Books a free consultation slot for tomorrow and notifies admin via Telegram."""
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({"error": "invalid_request"}, status=400)

    email = data.get("email", "").strip().lower()
    phone = data.get("phone", "").strip()
    time_slot = data.get("time_slot", "").strip()
    tomorrow = get_tomorrow_uzb()

    if not email or not phone or not time_slot:
        return JsonResponse({"error": "missing_fields"}, status=400)

    already_booked = ConsultationBooking.objects.filter(
        booking_date=tomorrow
    ).filter(models.Q(email__iexact=email) | models.Q(phone=phone))
    if already_booked.exists():
        return JsonResponse({"error": "duplicate"}, status=409)

    slot_taken = ConsultationBooking.objects.filter(
        booking_date=tomorrow, time_slot=time_slot
    ).exists()
    if slot_taken:
        return JsonResponse({"error": "slot_taken"}, status=409)

    try:
        ConsultationBooking.objects.create(
            email=email, phone=phone, booking_date=tomorrow, time_slot=time_slot
        )
    except Exception:
        return JsonResponse({"error": "slot_taken"}, status=409)

    message = (
        "\U0001F4C5 New Free Consultation Booking\n"
        f"Date: {tomorrow} (UZ time)\n"
        f"Time: {time_slot}\n"
        f"Email: {email}\n"
        f"Phone: {phone}"
    )

    bot_token = getattr(settings, "TELEGRAM_BOT_TOKEN", None)
    chat_id = getattr(settings, "TELEGRAM_CHAT_ID", None)

    if bot_token and chat_id:
        try:
            requests.post(
                f"https://api.telegram.org/bot{bot_token}/sendMessage",
                data={"chat_id": chat_id, "text": message},
                timeout=5,
            )
        except requests.RequestException:
            pass

    return JsonResponse({"success": True})