import os
import sys
import django
from datetime import timedelta
from django.utils import timezone
from PIL import Image, ImageDraw, ImageFont

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medihub.settings')
django.setup()

from profiles.models import SponsorBanner

# Directory for banner images
MEDIA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'sponsors', 'banners')
os.makedirs(MEDIA_DIR, exist_ok=True)

def create_banner_graphic(filename, width, height, bg_start, bg_end, brand, headline, subtext, badge_text, cta_text):
    img = Image.new("RGB", (width, height), bg_start)
    draw = ImageDraw.Draw(img)

    # Draw horizontal gradient
    for x in range(width):
        r = int(bg_start[0] + (bg_end[0] - bg_start[0]) * (x / width))
        g = int(bg_start[1] + (bg_end[1] - bg_start[1]) * (x / width))
        b = int(bg_start[2] + (bg_end[2] - bg_start[2]) * (x / width))
        draw.line([(x, 0), (x, height)], fill=(r, g, b))

    # Decorative geometric background curves
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)
    ov_draw.ellipse([width - 320, -100, width + 150, height + 100], fill=(255, 255, 255, 18))
    ov_draw.ellipse([width - 180, height - 120, width + 80, height + 80], fill=(255, 255, 255, 25))
    ov_draw.rectangle([0, 0, 8, height], fill=(255, 255, 255, 180)) # accent left stripe
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    try:
        font_brand = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(height * 0.12))
        font_headline = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(height * 0.14))
        font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", int(height * 0.08))
        font_cta = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(height * 0.08))
        font_badge = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(height * 0.065))
    except Exception:
        font_brand = ImageFont.load_default()
        font_headline = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_cta = ImageFont.load_default()
        font_badge = ImageFont.load_default()

    # Draw Badge
    badge_x, badge_y = 40, int(height * 0.14)
    draw.rounded_rectangle([badge_x, badge_y, badge_x + 220, badge_y + int(height * 0.13)], radius=8, fill=(255, 255, 255, 45), outline=(255, 255, 255, 120), width=1)
    draw.text((badge_x + 12, badge_y + 4), badge_text.upper(), fill=(255, 255, 255), font=font_badge)

    # Draw Brand
    draw.text((40, int(height * 0.32)), brand, fill=(255, 235, 120), font=font_brand)

    # Draw Headline
    draw.text((40, int(height * 0.48)), headline, fill=(255, 255, 255), font=font_headline)

    # Draw Subtext
    draw.text((40, int(height * 0.68)), subtext, fill=(225, 235, 245), font=font_sub)

    # Draw CTA Button on the right
    cta_w = 200
    cta_h = int(height * 0.22)
    cta_x = width - cta_w - 50
    cta_y = int((height - cta_h) / 2)
    draw.rounded_rectangle([cta_x, cta_y, cta_x + cta_w, cta_y + cta_h], radius=12, fill=(255, 255, 255), outline=(255, 255, 255))
    draw.text((cta_x + 30, cta_y + int(cta_h * 0.24)), cta_text, fill=(bg_start[0], bg_start[1], bg_start[2]), font=font_cta)

    filepath = os.path.join(MEDIA_DIR, filename)
    img.save(filepath, "JPEG", quality=92)
    print(f"Generated graphic: {filepath}")
    return f"sponsors/banners/{filename}"


def seed_banners():
    today = timezone.now().date()
    end_date = today + timedelta(days=60)

    banners_data = [
        {
            "slot": "home_hero",
            "sponsor_name": "Popular Diagnostic Center Ltd.",
            "title": "Comprehensive Executive Health Checkup — 25% Off",
            "target_url": "/diagnostics",
            "monthly_fee_bdt": 25000,
            "contact_person": "Dr. Tariqul Islam (Marketing)",
            "contact_phone": "01711000001",
            "filename": "popular_diagnostic_hero.jpg",
            "w": 1200, "h": 260,
            "bg1": (15, 23, 42), "bg2": (2, 132, 199), # Slate to Sky Blue
            "brand": "Popular Diagnostic Center",
            "headline": "Full-Body Executive Health Checkup Packages",
            "subtext": "Accredited Pathology & Radiology Labs with 100% Verified Digital Reports.",
            "badge": "★ Verified Partner",
            "cta": "Explore Tests →"
        },
        {
            "slot": "home_middle",
            "sponsor_name": "Square Hospitals Dhaka",
            "title": "24/7 Multi-Specialty Emergency, Trauma & Cardiac ICU",
            "target_url": "/doctors",
            "monthly_fee_bdt": 20000,
            "contact_person": "Rezaul Karim",
            "contact_phone": "01712000002",
            "filename": "square_hospital_middle.jpg",
            "w": 1200, "h": 240,
            "bg1": (6, 78, 59), "bg2": (5, 150, 105), # Emerald to Green
            "brand": "Square Hospital",
            "headline": "24/7 Specialized Emergency & Critical Care",
            "subtext": "World-class Intensive Care Units and round-the-clock BMDC specialist surgeons.",
            "badge": "JCI Accredited",
            "cta": "Book Specialist →"
        },
        {
            "slot": "medicine_page",
            "sponsor_name": "Beximco Pharma / Arogga Online",
            "title": "100% Genuine Prescription Medicines Delivered to Your Doorstep",
            "target_url": "/medicines",
            "monthly_fee_bdt": 18000,
            "contact_person": "Tanvir Ahmed",
            "contact_phone": "01713000003",
            "filename": "beximco_medicine_page.jpg",
            "w": 1100, "h": 220,
            "bg1": (30, 27, 75), "bg2": (67, 56, 202), # Indigo to Purple
            "brand": "Arogga & Beximco Pharma",
            "headline": "Flat 10% Off on All Genuine Chronic Care Medicines",
            "subtext": "Temperature-controlled medicine delivery across all 64 districts within 24 hours.",
            "badge": "DGDA Licensed",
            "cta": "Order Medicine →"
        },
        {
            "slot": "feed_inline",
            "sponsor_name": "Labaid Cancer Care Hospital",
            "title": "Leading Oncology & Cardiology Specialists in Bangladesh",
            "target_url": "/doctors",
            "monthly_fee_bdt": 15000,
            "contact_person": "Farhana Sultana",
            "contact_phone": "01714000004",
            "filename": "labaid_cancer_feed.jpg",
            "w": 960, "h": 230,
            "bg1": (136, 19, 55), "bg2": (225, 29, 72), # Rose to Crimson
            "brand": "Labaid Specialized Hospital",
            "headline": "Specialized Oncology, Cancer Care & Cardiac Surgery",
            "subtext": "Free screening camp this Friday. Book direct consultation appointment online.",
            "badge": "Center of Excellence",
            "cta": "View Doctors →"
        },
        {
            "slot": "sidebar",
            "sponsor_name": "Ibn Sina Medical Center",
            "title": "Advanced 3 Tesla MRI & 128-Slice CT Scan Imaging Center",
            "target_url": "/diagnostics",
            "monthly_fee_bdt": 12000,
            "contact_person": "Mahbubur Rahman",
            "contact_phone": "01715000005",
            "filename": "ibn_sina_sidebar.jpg",
            "w": 650, "h": 360,
            "bg1": (19, 78, 74), "bg2": (13, 148, 136), # Dark Teal
            "brand": "Ibn Sina Diagnostics",
            "headline": "Advanced 3 Tesla MRI & High-Res Ultrasound",
            "subtext": "Fast digital reporting with consultant radiologist reviews.",
            "badge": "Modern Imaging",
            "cta": "Book Imaging →"
        },
        {
            "slot": "interstitial_popup",
            "sponsor_name": "Evercare Hospital Emergency & Trauma Care",
            "title": "24/7 Emergency Ambulance & Critical ICU Response — Hotline 10678",
            "target_url": "/ambulances",
            "monthly_fee_bdt": 35000,
            "contact_person": "Ashfaqur Rahman (Brand & Corporate)",
            "contact_phone": "01720000006",
            "filename": "evercare_welcome_popup.jpg",
            "w": 900, "h": 500,
            "bg1": (15, 23, 42), "bg2": (225, 29, 72), # Dark Slate to Medical Crimson
            "brand": "Evercare Hospital Dhaka",
            "headline": "24/7 Rapid Emergency & Critical Care",
            "subtext": "Immediate ICU, Cardiac Trauma units & Emergency Teleconsultation.",
            "badge": "★ Official Healthcare Partner",
            "cta": "Emergency Help →",
            "media_type": "image",
            "skip_delay_seconds": 10
        }
    ]

    for item in banners_data:
        rel_path = create_banner_graphic(
            item["filename"], item["w"], item["h"],
            item["bg1"], item["bg2"],
            item["brand"], item["headline"], item["subtext"],
            item["badge"], item["cta"]
        )

        banner, created = SponsorBanner.objects.update_or_create(
            sponsor_name=item["sponsor_name"],
            slot=item["slot"],
            defaults={
                "title": item["title"],
                "media_type": item.get("media_type", "image"),
                "skip_delay_seconds": item.get("skip_delay_seconds", 10),
                "banner_image": rel_path,
                "target_url": item["target_url"],
                "start_date": today,
                "end_date": end_date,
                "is_active": True,
                "monthly_fee_bdt": item["monthly_fee_bdt"],
                "contact_person": item["contact_person"],
                "contact_phone": item["contact_phone"],
                "impressions_count": 1420,
                "clicks_count": 86,
            }
        )
        print(f"✅ Banner for '{banner.sponsor_name}' in slot '{banner.slot}' {'created' if created else 'updated'}.")

if __name__ == '__main__':
    seed_banners()
