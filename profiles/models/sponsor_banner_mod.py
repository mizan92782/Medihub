from django.db import models
from django.utils import timezone


class SponsorBanner(models.Model):
    SLOT_CHOICES = [
        ('home_hero', 'Home Page - Top Hero'),
        ('home_middle', 'Home Page - Middle Section'),
        ('feed_inline', 'Community Feed - Between Posts'),
        ('medicine_page', 'Medicine & Pharmacy Page'),
        ('sidebar', 'Global Sidebar'),
        ('interstitial_popup', 'Welcome Modal / Interstitial Ad (First Visit Popup)'),
    ]

    MEDIA_TYPE_CHOICES = [
        ('image', 'Static Graphic / Image'),
        ('video', 'Video Ad (Upload or URL)'),
    ]

    sponsor_name = models.CharField(max_length=150, help_text="e.g. Popular Diagnostic Center, Square Pharmaceuticals")
    title = models.CharField(max_length=200, blank=True, help_text="Short campaign or banner headline")
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPE_CHOICES, default='image', help_text="Image or Video advertisement")
    banner_image = models.ImageField(upload_to='sponsors/banners/', blank=True, null=True, help_text="Banner graphic (or video poster/thumbnail)")
    banner_video = models.FileField(upload_to='sponsors/videos/', blank=True, null=True, help_text="Uploaded MP4/WebM video ad file")
    video_url = models.CharField(max_length=500, blank=True, help_text="Direct video MP4/WebM URL or YouTube embed URL")
    skip_delay_seconds = models.PositiveIntegerField(
        default=10,
        help_text="Mandatory viewing time in seconds before user can skip/close (e.g. 5, 10, 15, 20)"
    )
    target_url = models.CharField(max_length=500, help_text="Redirect destination link upon user click (e.g. /doctors or https://...)")
    slot = models.CharField(max_length=50, choices=SLOT_CHOICES, default='home_hero')

    # Date scheduling
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(help_text="Banner automatically stops showing after this date")
    is_active = models.BooleanField(default=True, help_text="Manual kill-switch or active toggle")

    # Financial / contact details
    monthly_fee_bdt = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True)
    contact_person = models.CharField(max_length=100, blank=True)
    contact_phone = models.CharField(max_length=30, blank=True)

    # Analytics
    impressions_count = models.PositiveIntegerField(default=0)
    clicks_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Sponsor Banner'
        verbose_name_plural = 'Sponsor Banners'

    @property
    def is_currently_running(self):
        today = timezone.now().date()
        return self.is_active and (self.start_date <= today <= self.end_date)

    def __str__(self):
        return f"{self.sponsor_name} ({self.get_slot_display()})"
