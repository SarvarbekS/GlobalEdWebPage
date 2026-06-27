from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse, parse_qs

from django.db import models
from django.core.files.base import ContentFile
from PIL import Image
from pdf2image import convert_from_bytes
from pdf2image.exceptions import PDFInfoNotInstalledError


class ResultPoster(models.Model):
    image = models.ImageField(upload_to='results/')

    class Meta:
        ordering = []

    def __str__(self):
        return "image"

    def save(self, *args, **kwargs):
        if self.image:
            img = Image.open(self.image)
            if img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")
            max_width = 1200
            if img.width > max_width:
                new_height = int((max_width / img.width) * img.height)
                img = img.resize((max_width, new_height), Image.LANCZOS)
            output = BytesIO()
            img.save(output, format='JPEG', quality=72, optimize=True)
            output.seek(0)
            new_name = f"{Path(self.image.name).stem}.jpg"
            self.image.save(new_name, ContentFile(output.read()), save=False)
        super().save(*args, **kwargs)


class University(models.Model):
    COUNTRY_CHOICES = [
        ('US', 'US'),
        ('South Korea', 'South Korea'),
        ('UK', 'UK'),
        ('Australia', 'Australia'),
        ('New Zealand', 'New Zealand'),
        ('Europe', 'Europe'),
    ]

    TYPE_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]

    name = models.CharField(max_length=255)
    country = models.CharField(max_length=50, choices=COUNTRY_CHOICES)
    city = models.CharField(max_length=100, blank=True)
    university_type = models.CharField(max_length=10, choices=TYPE_CHOICES, blank=True)
    logo = models.ImageField(upload_to='universities/')
    qs_ranking = models.PositiveIntegerField(blank=True, null=True)
    tuition_min = models.PositiveIntegerField(blank=True, null=True, help_text="Annual tuition in USD (minimum)")
    tuition_max = models.PositiveIntegerField(blank=True, null=True, help_text="Annual tuition in USD (maximum)")
    scholarship_available = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    campus_tour_url = models.URLField(blank=True, help_text="Paste a YouTube watch/share/embed link.")

    class Meta:
        ordering = ['country', 'name']

    def __str__(self):
        return f"{self.name} ({self.country})"

    def get_youtube_embed_url(self):
        url = (self.campus_tour_url or '').strip()
        if not url:
            return ''

        parsed = urlparse(url)

        if 'youtu.be' in parsed.netloc:
            video_id = parsed.path.strip('/')
            return f'https://www.youtube.com/embed/{video_id}'

        if 'youtube.com' in parsed.netloc:
            if parsed.path == '/watch':
                video_id = parse_qs(parsed.query).get('v', [''])[0]
                if video_id:
                    return f'https://www.youtube.com/embed/{video_id}'
            if parsed.path.startswith('/embed/'):
                return url

        return ''

    def save(self, *args, **kwargs):
        if self.logo:
            img = Image.open(self.logo)
            original_name = Path(self.logo.name).stem

            has_alpha = (
                    img.mode in ("RGBA", "LA")
                    or (img.mode == "P" and "transparency" in img.info)
            )

            max_width = 600
            if img.width > max_width:
                new_height = int((max_width / img.width) * img.height)
                img = img.resize((max_width, new_height), Image.LANCZOS)

            output = BytesIO()

            if has_alpha:
                img = img.convert("RGBA")
                new_name = f"{original_name}.png"
                img.save(output, format="PNG", optimize=True)
            else:
                img = img.convert("RGB")
                new_name = f"{original_name}.jpg"
                img.save(output, format="JPEG", quality=70, optimize=True)

            output.seek(0)
            self.logo.save(new_name, ContentFile(output.read()), save=False)

        super().save(*args, **kwargs)


class Program(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    benefits = models.TextField(
        help_text="Enter one benefit per line."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class News(models.Model):
    title = models.CharField(max_length=200)
    summary = models.TextField(help_text="Short teaser shown on the card.")
    body = models.TextField(help_text="Full news content shown in modal.")
    source = models.CharField(max_length=200, blank=True)
    published_at = models.DateField()
    image = models.ImageField(upload_to='news/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.image:
            img = Image.open(self.image)

            has_alpha = (
                img.mode in ("RGBA", "LA")
                or (img.mode == "P" and "transparency" in img.info)
            )

            max_width = 1200
            if img.width > max_width:
                new_height = int((max_width / img.width) * img.height)
                img = img.resize((max_width, new_height), Image.LANCZOS)

            output = BytesIO()
            base_name = Path(self.image.name).stem

            if has_alpha:
                img = img.convert("RGBA")
                new_name = f"{base_name}.png"
                img.save(output, format="PNG", optimize=True)
            else:
                img = img.convert("RGB")
                new_name = f"{base_name}.jpg"
                img.save(output, format="JPEG", quality=80, optimize=True)

            output.seek(0)
            self.image.save(new_name, ContentFile(output.read()), save=False)

        super().save(*args, **kwargs)

class Event(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=250, blank=True)
    location = models.CharField(max_length=200, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    summary = models.TextField(help_text="Short description shown on the card.")
    body = models.TextField(help_text="Full event details shown in modal.")
    image = models.ImageField(upload_to='events/', blank=True, null=True)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-featured', '-start_date', '-created_at']

    def __str__(self):
        return self.title

    def date_range_display(self):
        if self.end_date and self.end_date != self.start_date:
            return f"{self.start_date:%b %d, %Y} – {self.end_date:%b %d, %Y}"
        return f"{self.start_date:%b %d, %Y}"

    def save(self, *args, **kwargs):
        if self.image:

            img = Image.open(self.image)
            has_alpha = (
                img.mode in ("RGBA", "LA")
                or (img.mode == "P" and "transparency" in img.info)
            )

            max_width = 1200
            if img.width > max_width:
                new_height = int((max_width / img.width) * img.height)
                img = img.resize((max_width, new_height), Image.LANCZOS)

            output = BytesIO()
            base_name = Path(self.image.name).stem

            if has_alpha:
                img = img.convert("RGBA")
                new_name = f"{base_name}.png"
                img.save(output, format="PNG", optimize=True)
            else:
                img = img.convert("RGB")
                new_name = f"{base_name}.jpg"
                img.save(output, format="JPEG", quality=80, optimize=True)

            output.seek(0)
            self.image.save(new_name, ContentFile(output.read()), save=False)

        super().save(*args, **kwargs)

class Certification(models.Model):
    title = models.CharField(max_length=255)
    category = models.CharField(
        max_length=120,
        blank=True,
        help_text="e.g. License, Contract, Partnership, Registration"
    )
    pdf = models.FileField(upload_to="certifications/")
    preview_image = models.ImageField(
        upload_to="certifications/previews/",
        blank=True,
        null=True,
        help_text="Auto-generated thumbnail of first page"
    )
    issued_by = models.CharField(max_length=255, blank=True)
    issued_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if not self.pdf or self.preview_image:
            return

        try:
            self.pdf.open("rb")
            pdf_bytes = self.pdf.read()
            self.pdf.close()

            pages = convert_from_bytes(pdf_bytes, first_page=1, last_page=1, fmt="jpeg")
            # ... generate thumbnail as before ...
        except PDFInfoNotInstalledError:
            # Skip preview if poppler not available
            return
        except Exception:
            # Avoid breaking admin on any unexpected error
            return

        # Read first page of PDF and convert to JPEG thumbnail
        self.pdf.open("rb")
        pdf_bytes = self.pdf.read()
        self.pdf.close()

        pages = convert_from_bytes(pdf_bytes, first_page=1, last_page=1, fmt="jpeg")
        if not pages:
            return

        img = pages[0]

        # Resize to a reasonable width for cards (similar to your other thumbnails)
        max_width = 800
        if img.width > max_width:
            new_height = int(max_width * img.height / img.width)
            img = img.resize((max_width, new_height), Image.LANCZOS)

        output = BytesIO()
        img.save(output, format="JPEG", quality=80, optimize=True)
        output.seek(0)

        name_stem = Path(self.pdf.name).stem
        preview_name = f"{name_stem}_preview.jpg"
        self.preview_image.save(preview_name, ContentFile(output.read()), save=False)

        super().save(update_fields=["preview_image"])