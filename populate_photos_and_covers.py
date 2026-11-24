import os
import urllib.request
from datetime import date
from django.conf import settings
from profiles.models import (
    Doctor, BloodDonor, RegularUserProfile,
    PharmacyProfile, DiagnosticProfile, AmbulanceProfile
)
from PIL import Image, ImageDraw, ImageFont

# Set up local directories
DIR_DOC_DP = os.path.join(settings.MEDIA_ROOT, "doctor", "dp")
DIR_DOC_CV = os.path.join(settings.MEDIA_ROOT, "doctor", "cover")
DIR_DON_DP = os.path.join(settings.MEDIA_ROOT, "donor", "dp")
DIR_DON_CV = os.path.join(settings.MEDIA_ROOT, "donor", "cover")
DIR_USR_DP = os.path.join(settings.MEDIA_ROOT, "user", "dp")
DIR_USR_CV = os.path.join(settings.MEDIA_ROOT, "user", "cover")
DIR_PHA_DP = os.path.join(settings.MEDIA_ROOT, "pharmacy", "dp")
DIR_PHA_CV = os.path.join(settings.MEDIA_ROOT, "pharmacy", "cover")
DIR_DIA_DP = os.path.join(settings.MEDIA_ROOT, "diagnostic", "dp")
DIR_DIA_CV = os.path.join(settings.MEDIA_ROOT, "diagnostic", "cover")
DIR_AMB_DP = os.path.join(settings.MEDIA_ROOT, "ambulance", "dp")
DIR_AMB_CV = os.path.join(settings.MEDIA_ROOT, "ambulance", "cover")

for d in [DIR_DOC_DP, DIR_DOC_CV, DIR_DON_DP, DIR_DON_CV, DIR_USR_DP, DIR_USR_CV,
          DIR_PHA_DP, DIR_PHA_CV, DIR_DIA_DP, DIR_DIA_CV, DIR_AMB_DP, DIR_AMB_CV]:
    os.makedirs(d, exist_ok=True)

def download_or_generate_image(url, save_abs_path, fallback_type="cover", text="MediHub", bg=(37, 99, 235), w=1200, h=400):
    if os.path.exists(save_abs_path) and os.path.getsize(save_abs_path) > 3000:
        return True
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = resp.read()
            if len(data) > 1000:
                with open(save_abs_path, 'wb') as f:
                    f.write(data)
                return True
    except Exception as e:
        print(f"Fallback generated for {os.path.basename(save_abs_path)} due to: {e}")

    # Fallback generator using Pillow
    img = Image.new("RGB", (w, h), bg)
    draw = ImageDraw.Draw(img)
    if fallback_type == "cover":
        for x in range(w):
            r = int(bg[0] + (255 - bg[0]) * 0.15 * (x / w))
            g = int(bg[1] + (255 - bg[1]) * 0.15 * (x / w))
            b = int(bg[2] + (255 - bg[2]) * 0.15 * (x / w))
            draw.line([(x, 0), (x, h)], fill=(r, g, b))
        draw.rectangle([0, h - 8, w, h], fill=(255, 255, 255))
    else:
        draw.ellipse([8, 8, w - 8, h - 8], outline=(255, 255, 255), width=4)

    try:
        font = ImageFont.load_default(size=int(h * 0.2))
    except Exception:
        font = ImageFont.load_default()
    draw.text((w // 4, h // 3), text, fill=(255, 255, 255), font=font)
    img.save(save_abs_path, "JPEG", quality=85)
    return True

# 1. Image Pools from high quality Unsplash health collections
DOCTOR_MALE_PHOTOS = [
    "https://images.unsplash.com/photo-1622253692010-333f2da6031d?w=400&h=400&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=400&h=400&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1537368910025-700350fe46c7?w=400&h=400&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1582750433449-648ed127bb54?w=400&h=400&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1638202993928-7267aad84c31?w=400&h=400&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1651008376811-b90baee60c1f?w=400&h=400&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1607990281513-2c110a25bd8c?w=400&h=400&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=400&h=400&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1594824813566-82823d5afe4a?w=400&h=400&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=400&h=400&fit=crop&crop=face",
]

DOCTOR_FEMALE_PHOTOS = [
    "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=400&h=400&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1594824813566-82823d5afe4a?w=400&h=400&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1527613426441-4da17471b66d?w=400&h=400&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1614608682850-e0d6ed316d47?w=400&h=400&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1643297654416-05795d62e39c?w=400&h=400&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1651008376811-b90baee60c1f?w=400&h=400&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=400&h=400&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1607990281513-2c110a25bd8c?w=400&h=400&fit=crop&crop=face",
]

DOCTOR_COVERS = [
    "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?w=1200&h=450&fit=crop",
    "https://images.unsplash.com/photo-1586773860418-d37222d8fce3?w=1200&h=450&fit=crop",
    "https://images.unsplash.com/photo-1504813184591-01572f98c85f?w=1200&h=450&fit=crop",
    "https://images.unsplash.com/photo-1516549655169-df83a0774514?w=1200&h=450&fit=crop",
    "https://images.unsplash.com/photo-1538108149393-fbbd81895907?w=1200&h=450&fit=crop",
    "https://images.unsplash.com/photo-1579684385127-1ef15d508118?w=1200&h=450&fit=crop",
]

DONOR_MALE_PHOTOS = [
    "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=400&h=400&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1570295999919-56ceb5ecca61?w=400&h=400&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&h=400&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=400&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=400&h=400&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=400&h=400&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1463453091185-61582044d556?w=400&h=400&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?w=400&h=400&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?w=400&h=400&fit=crop&crop=face",
]

DONOR_FEMALE_PHOTOS = [
    "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&h=400&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=400&h=400&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400&h=400&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400&h=400&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?w=400&h=400&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?w=400&h=400&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=400&h=400&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=400&h=400&fit=crop&crop=face",
]

DONOR_COVERS = [
    "https://images.unsplash.com/photo-1615461066841-6116e61058f4?w=1200&h=450&fit=crop",
    "https://images.unsplash.com/photo-1584515979956-d9f6e5d09982?w=1200&h=450&fit=crop",
    "https://images.unsplash.com/photo-1579154204601-01588f351e67?w=1200&h=450&fit=crop",
]

USER_COVERS = [
    "https://images.unsplash.com/photo-1507652313519-d4e9174996dd?w=1200&h=450&fit=crop",
    "https://images.unsplash.com/photo-1532938911079-1b06ac7ceec7?w=1200&h=450&fit=crop",
]

PHARMACY_DPS = [
    "https://images.unsplash.com/photo-1587854692152-cbe660dbde88?w=400&h=400&fit=crop",
    "https://images.unsplash.com/photo-1471864190281-a93a3070b6de?w=400&h=400&fit=crop",
]

PHARMACY_COVERS = [
    "https://images.unsplash.com/photo-1631549916768-4119b2e5f926?w=1200&h=450&fit=crop",
    "https://images.unsplash.com/photo-1576602976047-174e57a47881?w=1200&h=450&fit=crop",
]

DIAGNOSTIC_DPS = [
    "https://images.unsplash.com/photo-1582719471384-894fbb16e074?w=400&h=400&fit=crop",
    "https://images.unsplash.com/photo-1579165466741-7f35e4755660?w=400&h=400&fit=crop",
]

DIAGNOSTIC_COVERS = [
    "https://images.unsplash.com/photo-1516549655169-df83a0774514?w=1200&h=450&fit=crop",
    "https://images.unsplash.com/photo-1579165466741-7f35e4755660?w=1200&h=450&fit=crop",
]

AMBULANCE_DPS = [
    "https://images.unsplash.com/photo-1587745416684-47953f16f02f?w=400&h=400&fit=crop",
    "https://images.unsplash.com/photo-1516574187841-cb9cc2ca948b?w=400&h=400&fit=crop",
]

AMBULANCE_COVERS = [
    "https://images.unsplash.com/photo-1516574187841-cb9cc2ca948b?w=1200&h=450&fit=crop",
    "https://images.unsplash.com/photo-1587745416684-47953f16f02f?w=1200&h=450&fit=crop",
]

# 2. Update Doctors
print("Updating Doctor DP and Cover Photos...")
for i, doc in enumerate(Doctor.objects.all()):
    # DP
    pool = DOCTOR_FEMALE_PHOTOS if doc.gender == 'female' else DOCTOR_MALE_PHOTOS
    dp_url = pool[i % len(pool)]
    dp_rel = f"doctor/dp/doctor_{doc.id}.jpg"
    dp_abs = os.path.join(settings.MEDIA_ROOT, dp_rel)
    download_or_generate_image(dp_url, dp_abs, "dp", f"Dr. {doc.first_name[0]}{doc.last_name[0]}", (14, 116, 144), 400, 400)
    doc.profile_dp = dp_rel

    # Cover
    cv_url = DOCTOR_COVERS[i % len(DOCTOR_COVERS)]
    cv_rel = f"doctor/cover/doctor_cover_{doc.id}.jpg"
    cv_abs = os.path.join(settings.MEDIA_ROOT, cv_rel)
    download_or_generate_image(cv_url, cv_abs, "cover", f"{doc.specialization.name_eng if doc.specialization else 'Healthcare'}", (15, 23, 42), 1200, 450)
    doc.cover_photo = cv_rel

    doc.save()

# 3. Update Donors
print("Updating Blood Donor DP and Cover Photos...")
for i, donor in enumerate(BloodDonor.objects.all()):
    pool = DONOR_FEMALE_PHOTOS if donor.gender == 'female' else DONOR_MALE_PHOTOS
    dp_url = pool[i % len(pool)]
    dp_rel = f"donor/dp/donor_{donor.id}.jpg"
    dp_abs = os.path.join(settings.MEDIA_ROOT, dp_rel)
    download_or_generate_image(dp_url, dp_abs, "dp", donor.blood_group, (220, 38, 38), 400, 400)
    donor.profile_dp = dp_rel

    cv_url = DONOR_COVERS[i % len(DONOR_COVERS)]
    cv_rel = f"donor/cover/donor_cover_{donor.id}.jpg"
    cv_abs = os.path.join(settings.MEDIA_ROOT, cv_rel)
    download_or_generate_image(cv_url, cv_abs, "cover", "Blood Donation Saves Lives", (185, 28, 28), 1200, 450)
    donor.cover_photo = cv_rel

    donor.save()

# 4. Update Regular Users
print("Updating Regular User DP and Cover Photos...")
for i, u_prof in enumerate(RegularUserProfile.objects.all()):
    pool = DONOR_FEMALE_PHOTOS if u_prof.gender == 'female' else DONOR_MALE_PHOTOS
    dp_url = pool[i % len(pool)]
    dp_rel = f"user/dp/user_{u_prof.id}.jpg"
    dp_abs = os.path.join(settings.MEDIA_ROOT, dp_rel)
    download_or_generate_image(dp_url, dp_abs, "dp", f"{u_prof.first_name[0]}{u_prof.last_name[0]}", (2, 132, 199), 400, 400)
    u_prof.profile_dp = dp_rel

    cv_url = USER_COVERS[i % len(USER_COVERS)]
    cv_rel = f"user/cover/user_cover_{u_prof.id}.jpg"
    cv_abs = os.path.join(settings.MEDIA_ROOT, cv_rel)
    download_or_generate_image(cv_url, cv_abs, "cover", "MediHub Wellness", (30, 41, 59), 1200, 450)
    u_prof.cover_photo = cv_rel

    u_prof.save()

# 5. Update Pharmacies
print("Updating Pharmacy DP and Cover Photos...")
for i, pharm in enumerate(PharmacyProfile.objects.all()):
    dp_url = PHARMACY_DPS[i % len(PHARMACY_DPS)]
    dp_rel = f"pharmacy/dp/pharm_{pharm.id}.jpg"
    dp_abs = os.path.join(settings.MEDIA_ROOT, dp_rel)
    download_or_generate_image(dp_url, dp_abs, "dp", "Rx", (16, 185, 129), 400, 400)
    pharm.profile_dp = dp_rel

    cv_url = PHARMACY_COVERS[i % len(PHARMACY_COVERS)]
    cv_rel = f"pharmacy/cover/pharm_cover_{pharm.id}.jpg"
    cv_abs = os.path.join(settings.MEDIA_ROOT, cv_rel)
    download_or_generate_image(cv_url, cv_abs, "cover", pharm.pharmacy_name, (6, 78, 59), 1200, 450)
    pharm.cover_photo = cv_rel

    pharm.save()

# 6. Update Diagnostics
print("Updating Diagnostic DP and Cover Photos...")
for i, diag in enumerate(DiagnosticProfile.objects.all()):
    dp_url = DIAGNOSTIC_DPS[i % len(DIAGNOSTIC_DPS)]
    dp_rel = f"diagnostic/dp/diag_{diag.id}.jpg"
    dp_abs = os.path.join(settings.MEDIA_ROOT, dp_rel)
    download_or_generate_image(dp_url, dp_abs, "dp", "Lab", (79, 70, 229), 400, 400)
    diag.profile_dp = dp_rel

    cv_url = DIAGNOSTIC_COVERS[i % len(DIAGNOSTIC_COVERS)]
    cv_rel = f"diagnostic/cover/diag_cover_{diag.id}.jpg"
    cv_abs = os.path.join(settings.MEDIA_ROOT, cv_rel)
    download_or_generate_image(cv_url, cv_abs, "cover", diag.diagnostic_name, (49, 46, 129), 1200, 450)
    diag.cover_photo = cv_rel

    diag.save()

# 7. Update Ambulances
print("Updating Ambulance DP and Cover Photos...")
for i, amb in enumerate(AmbulanceProfile.objects.all()):
    dp_url = AMBULANCE_DPS[i % len(AMBULANCE_DPS)]
    dp_rel = f"ambulance/dp/amb_{amb.id}.jpg"
    dp_abs = os.path.join(settings.MEDIA_ROOT, dp_rel)
    download_or_generate_image(dp_url, dp_abs, "dp", "24/7", (220, 38, 38), 400, 400)
    amb.profile_dp = dp_rel

    cv_url = AMBULANCE_COVERS[i % len(AMBULANCE_COVERS)]
    cv_rel = f"ambulance/cover/amb_cover_{amb.id}.jpg"
    cv_abs = os.path.join(settings.MEDIA_ROOT, cv_rel)
    download_or_generate_image(cv_url, cv_abs, "cover", amb.owner_name, (127, 29, 29), 1200, 450)
    amb.cover_photo = cv_rel

    amb.save()

print("✅ ALL PROFILE AND BACKGROUND COVER PHOTOS SUCCESSFULLY POPULATED!")
