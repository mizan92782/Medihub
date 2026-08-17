"""
Fill in the seed-data gaps that leave the frontend rendering blanks:

  * Doctor.consultation_fee / .address / .upozila   (cards showed "৳0" and a
    half-empty location line)
  * DiagnosticTest.turnaround_time                  (lab cards showed no ETA)
  * BloodDonor.last_donated / .availability         (cards showed "Last: N/A")
  * AmbulanceProfile.is_available                   (whole fleet read as busy)
  * DoctorRating rows                               (profile page had no reviews
    even though DoctorStats carried aggregates)
  * profile_dp for donors, ambulances, pharmacies and diagnostics

Idempotent: re-running only touches rows that are still empty unless --force is
passed. Deterministic: seeded RNG, so repeated runs produce the same values.

    python manage.py enrich_seed
    python manage.py enrich_seed --force        # overwrite existing values
    python manage.py enrich_seed --skip-photos  # no network calls
"""
import random
import urllib.parse
import urllib.request
from datetime import timedelta
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from core.enum import AvailabilityChoices
from authentication.models import User
from location.models import Upozila
from profiles.models import (
    AmbulanceProfile, BloodDonor, DiagnosticProfile, DiagnosticTest,
    Doctor, DoctorRating, DoctorStats, PharmacyProfile,
)

SEED = 20260814

# Consultation fees follow the local market: seniority and specialty driven.
BASE_FEE_BY_SPECIALITY = {
    "Cardiology": 1500,
    "Neurology": 1500,
    "Oncology": 1600,
    "Nephrology": 1400,
    "Gastroenterology": 1300,
    "Endocrinology": 1200,
    "Gynecology & Obstetrics": 1000,
    "Orthopedics": 1000,
    "Dermatology": 900,
    "Psychiatry": 1200,
    "Pediatrics": 800,
    "ENT": 800,
    "Ophthalmology": 900,
    "Urology": 1200,
    "General Medicine": 700,
}
DEFAULT_BASE_FEE = 800

TURNAROUND_BY_CATEGORY = {
    "Hematology": "Same day",
    "Endocrinology": "6 - 8 hours",
    "Biochemistry": "Same day",
    "Microbiology": "48 - 72 hours",
    "Pathology": "24 hours",
    "Radiology": "2 - 4 hours",
    "Imaging": "2 - 4 hours",
    "Cardiology": "Same day",
    "Immunology": "24 - 48 hours",
    "Serology": "24 hours",
    "Molecular": "48 hours",
    "Histopathology": "3 - 5 days",
}
DEFAULT_TURNAROUND = "24 hours"

REVIEW_POOL = [
    ("Very attentive, explained my reports in detail. Highly recommended.", 5),
    ("Took time to listen and did not rush the consultation.", 5),
    ("Good treatment, though the chamber wait was a bit long.", 4),
    ("Professional and clear about the treatment plan.", 5),
    ("Prescription worked well. Follow-up advice was practical.", 4),
    ("Decent consultation, but I expected more detail on the diet plan.", 3),
    ("Very polite and patient with elderly family members.", 5),
    ("Reasonable fee for the level of care provided.", 4),
    ("Diagnosis was accurate and recovery was quick.", 5),
    ("Consultation felt rushed, though the treatment was effective.", 3),
]

ROAD_NAMES = [
    "Green Road", "Satmasjid Road", "Mirpur Road", "Elephant Road",
    "Bailey Road", "Shaheed Suhrawardy Avenue", "Kazi Nazrul Islam Avenue",
    "College Road", "Station Road", "Hospital Road",
]

# Unsplash CDN, same approach as assign_profile_pictures.
DONOR_PHOTOS = [
    "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=300&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=300&h=300&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=300&h=300&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=300&h=300&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=300&h=300&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=300&h=300&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=300&h=300&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?w=300&h=300&fit=crop&crop=face",
]
AMBULANCE_PHOTOS = [
    "https://images.unsplash.com/photo-1587745416684-47953f16f02f?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1615486364159-8ed7bcc4c7ba?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1516574187841-cb9cc2ca948b?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1612824006051-0e0d0d6e3d3d?w=400&h=300&fit=crop",
]
PHARMACY_PHOTOS = [
    "https://images.unsplash.com/photo-1587854692152-cbe660dbde88?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1576602976047-174e57a47881?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1585435557343-3b092031a831?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1471864190281-a93a3070b6de?w=400&h=300&fit=crop",
]
DIAGNOSTIC_PHOTOS = [
    "https://images.unsplash.com/photo-1579154204601-01588f351e67?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1582719508461-905c673771fd?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1530026405186-ed1f139313f8?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1516549655169-df83a0774514?w=400&h=300&fit=crop",
]


def fetch(url, save_path, timeout=10):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
        if not data:
            return False
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        Path(save_path).write_bytes(data)
        return True
    except Exception:
        return False


def fetch_with_fallback(url, save_path, label, colour):
    """Try the real photo; fall back to a generated initials avatar."""
    if fetch(url, save_path):
        return True
    avatar = (
        "https://ui-avatars.com/api/?name="
        f"{urllib.parse.quote(label)}&size=300&background={colour}&color=fff&bold=true"
    )
    return fetch(avatar, save_path)


class Command(BaseCommand):
    help = "Fill gaps in seeded profile data (fees, turnaround, availability, ratings, photos)"

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true",
                            help="overwrite values that are already set")
        parser.add_argument("--skip-photos", action="store_true",
                            help="skip downloading profile images")

    def handle(self, *args, **opts):
        self.rng = random.Random(SEED)
        self.force = opts["force"]
        self.media = Path(settings.MEDIA_ROOT)

        with transaction.atomic():
            self.fill_doctor_fees()
            self.fill_doctor_locations()
            self.fill_test_turnaround()
            self.fill_donor_history()
            self.fill_ambulance_availability()
            self.create_doctor_reviews()

        if opts["skip_photos"]:
            self.stdout.write("photos: skipped (--skip-photos)")
        else:
            self.assign_photos()

        self.stdout.write(self.style.SUCCESS("\n✅ enrich_seed complete"))

    # ── doctors ──────────────────────────────────────────────────────────
    def fill_doctor_fees(self):
        qs = Doctor.objects.all() if self.force else Doctor.objects.filter(consultation_fee=0)
        n = 0
        for doctor in qs.select_related("specialization"):
            spec = doctor.specialization.name_eng if doctor.specialization else ""
            base = BASE_FEE_BY_SPECIALITY.get(spec, DEFAULT_BASE_FEE)
            # +25 BDT per year of experience, rounded to the nearest 50.
            raw = base + (doctor.years_of_experience or 0) * 25
            fee = int(round(raw / 50.0) * 50)
            doctor.consultation_fee = Decimal(fee)
            doctor.save(update_fields=["consultation_fee"])
            n += 1
        self.stdout.write(f"doctors  : consultation_fee set on {n}")

    def fill_doctor_locations(self):
        qs = Doctor.objects.all() if self.force else Doctor.objects.filter(upozila__isnull=True)
        filled_upozila = 0
        for doctor in qs.select_related("district"):
            if not doctor.district_id:
                continue
            choices = list(Upozila.objects.filter(district_id=doctor.district_id)[:20])
            if choices:
                doctor.upozila = self.rng.choice(choices)
                doctor.save(update_fields=["upozila"])
                filled_upozila += 1

        addr_qs = Doctor.objects.all() if self.force else Doctor.objects.filter(address__isnull=True)
        filled_addr = 0
        for doctor in addr_qs:
            house = self.rng.randint(1, 120)
            road = self.rng.choice(ROAD_NAMES)
            doctor.address = f"House {house}, {road}"
            doctor.save(update_fields=["address"])
            filled_addr += 1

        self.stdout.write(f"doctors  : upozila set on {filled_upozila}, address on {filled_addr}")

    def create_doctor_reviews(self):
        """DoctorStats carried aggregates with no DoctorRating rows behind them."""
        if DoctorRating.objects.exists() and not self.force:
            self.stdout.write(f"doctors  : {DoctorRating.objects.count()} ratings already present")
            return
        if self.force:
            DoctorRating.objects.all().delete()

        reviewers = list(User.objects.filter(user_type="regular")[:60])
        if not reviewers:
            self.stdout.write(self.style.WARNING("doctors  : no users to attribute reviews to"))
            return

        now = timezone.now()
        created = 0
        for doctor in Doctor.objects.all():
            n_reviews = self.rng.randint(4, 12)
            picked = self.rng.sample(reviewers, min(n_reviews, len(reviewers)))
            ratings = []
            for user in picked:
                review, stars = self.rng.choice(REVIEW_POOL)
                DoctorRating.objects.create(
                    doctor=doctor, user=user, rating=stars, review=review,
                )
                ratings.append(stars)
                created += 1

            # Keep the cached aggregate consistent with the rows we just wrote.
            stats, _ = DoctorStats.objects.get_or_create(doctor=doctor)
            stats.avg_rating = round(sum(ratings) / len(ratings), 1)
            stats.total_rating = len(ratings)
            if not stats.total_profile_views:
                stats.total_profile_views = self.rng.randint(120, 4200)
            stats.last_active = now - timedelta(hours=self.rng.randint(0, 72))
            stats.save()

        self.stdout.write(f"doctors  : {created} ratings created")

    # ── diagnostics ──────────────────────────────────────────────────────
    def fill_test_turnaround(self):
        qs = DiagnosticTest.objects.all() if self.force else DiagnosticTest.objects.filter(
            turnaround_time__isnull=True
        )
        n = 0
        for test in qs:
            test.turnaround_time = TURNAROUND_BY_CATEGORY.get(test.category or "", DEFAULT_TURNAROUND)
            test.save(update_fields=["turnaround_time"])
            n += 1
        self.stdout.write(f"tests    : turnaround_time set on {n}")

    # ── donors ───────────────────────────────────────────────────────────
    def fill_donor_history(self):
        today = timezone.now().date()
        qs = BloodDonor.objects.all() if self.force else BloodDonor.objects.filter(last_donated__isnull=True)
        n = 0
        for donor in qs:
            # A donor is eligible ~120 days after donating; spread dates so the
            # availability flag and the date agree with each other.
            days_ago = self.rng.randint(20, 400)
            donor.last_donated = today - timedelta(days=days_ago)
            donor.availability = (
                AvailabilityChoices.AVAILABLE if days_ago >= 120 else AvailabilityChoices.UNAVAILABLE
            )
            if not donor.lives_saved_count:
                donor.lives_saved_count = self.rng.randint(1, 18)
            donor.save(update_fields=["last_donated", "availability", "lives_saved_count"])
            n += 1
        available = BloodDonor.objects.filter(availability=AvailabilityChoices.AVAILABLE).count()
        self.stdout.write(f"donors   : history set on {n} ({available} now available)")

    # ── ambulances ───────────────────────────────────────────────────────
    def fill_ambulance_availability(self):
        n = 0
        for amb in AmbulanceProfile.objects.all():
            # ~70% on the road and free; the rest genuinely busy.
            amb.is_available = self.rng.random() < 0.7
            amb.save(update_fields=["is_available"])
            n += 1
        free = AmbulanceProfile.objects.filter(is_available=True).count()
        self.stdout.write(f"ambulance: availability set on {n} ({free} available)")

    # ── photos ───────────────────────────────────────────────────────────
    def assign_photos(self):
        self.stdout.write("\ndownloading profile photos…")
        self._photos_for(
            BloodDonor, DONOR_PHOTOS, "donor/dp", "donor_dp",
            lambda o: f"{o.first_name}+{o.last_name}", "e11d48",
        )
        self._photos_for(
            AmbulanceProfile, AMBULANCE_PHOTOS, "ambulance/dp", "ambulance_dp",
            lambda o: o.owner_name.replace(" ", "+"), "047857",
        )
        self._photos_for(
            PharmacyProfile, PHARMACY_PHOTOS, "pharmacy/dp", "pharmacy_dp",
            lambda o: o.pharmacy_name.replace(" ", "+"), "0d9488",
        )
        self._photos_for(
            DiagnosticProfile, DIAGNOSTIC_PHOTOS, "diagnostic/dp", "diagnostic_dp",
            lambda o: o.diagnostic_name.replace(" ", "+"), "065f46",
        )

    def _photos_for(self, model, urls, subdir, prefix, label_fn, colour):
        qs = model.objects.all() if self.force else model.objects.filter(profile_dp="")
        qs = qs | model.objects.filter(profile_dp__isnull=True)
        qs = qs.distinct()
        total = qs.count()
        ok = 0
        for i, obj in enumerate(qs):
            filename = f"{prefix}_{obj.id}.jpg"
            save_path = self.media / subdir / filename
            if fetch_with_fallback(urls[i % len(urls)], save_path, label_fn(obj), colour):
                obj.profile_dp = f"{subdir}/{filename}"
                obj.save(update_fields=["profile_dp"])
                ok += 1
        style = self.style.SUCCESS if ok == total else self.style.WARNING
        self.stdout.write(style(f"  {model.__name__:<18} {ok}/{total} photos"))
