"""
Run with:
  docker compose -f docker-compose.dev.yml exec web python manage.py shell < seed_community_posts.py
"""
import urllib.request
import os
from django.core.files.base import ContentFile
from django.contrib.contenttypes.models import ContentType
from authentication.models import User
from location.models import Division, District, Upozila
from post.models import (
    BloodNeedPost, MedicineNeedPost, EquipmentNeedPost,
    EquipmentSellPost, MedicinePost, GeneralPost, AmbulanceNeedPost,
    PostImage,
)
from profiles.models.blood_donor_mod import BloodDonationPost, BloodDonor

# ── helpers ──────────────────────────────────────────────────────────────────

def get_user():
    u = User.objects.filter(user_type='regular').first() or User.objects.first()
    if not u:
        u = User.objects.create_user(email='seed@medihub.com', password='seed1234', user_type='regular', is_verified=True)
    return u

def get_loc():
    div  = Division.objects.first()
    dist = District.objects.filter(division=div).first() if div else District.objects.first()
    upz  = Upozila.objects.filter(district=dist).first() if dist else Upozila.objects.first()
    return div, dist, upz

def attach_images(post_instance, urls):
    """Download images from placeholder URLs and attach as PostImage records."""
    ct = ContentType.objects.get_for_model(post_instance.__class__)
    for i, url in enumerate(urls):
        try:
            with urllib.request.urlopen(url, timeout=8) as resp:
                data = resp.read()
            pi = PostImage(content_type=ct, object_id=post_instance.id, order=i)
            pi.image.save(f'seed_{post_instance.__class__.__name__}_{post_instance.id}_{i}.jpg', ContentFile(data), save=True)
            print(f"  ✅ image {i+1} attached")
        except Exception as e:
            print(f"  ⚠️  image {i+1} skipped ({e})")

# Placeholder image URLs (picsum.photos — reliable, no auth needed)
IMG = [
    'https://picsum.photos/seed/med1/600/400',
    'https://picsum.photos/seed/med2/600/400',
    'https://picsum.photos/seed/med3/600/400',
]

user = get_user()
div, dist, upz = get_loc()
print(f"Using user: {user.email} | div: {div} | dist: {dist} | upz: {upz}\n")

# ── 1. Blood Need ─────────────────────────────────────────────────────────────
print("🩸 Seeding BloodNeedPost...")
BloodNeedPost.objects.filter(patient_name='Seed Patient').delete()
p = BloodNeedPost.objects.create(
    user=user, division=div, district=dist, upozila=upz,
    patient_name='Seed Patient', patient_age=45, patient_gender='male',
    blood_group='O+', bags_needed=2,
    hospital_name='Dhaka Medical College Hospital',
    hospital_address='Bakshi Bazar, Dhaka',
    needed_date='2025-09-01', needed_time='10:00:00',
    contact_number='01811000001', urgency='critical',
    description='Urgent O+ blood needed for open heart surgery. Please contact immediately.',
    status='open',
)
attach_images(p, IMG)
print(f"  Created BloodNeedPost id={p.id}\n")

# ── 2. Blood Donated ──────────────────────────────────────────────────────────
print("❤️  Seeding BloodDonationPost...")
donor = BloodDonor.objects.first()
if donor:
    BloodDonationPost.objects.filter(donor=donor, medical_facility='Seed Hospital').delete()
    p = BloodDonationPost.objects.create(
        donor=donor, division=div, district=dist, upozila=upz,
        bags_donated=1,
        medical_facility='Seed Hospital',
        donation_date='2025-08-20', donation_time='09:00:00',
        patient_description='Donated blood for a thalassemia patient. Feeling great about it!',
    )
    attach_images(p, IMG)
    print(f"  Created BloodDonationPost id={p.id} (donor: {donor})\n")
else:
    print("  ⚠️  No BloodDonor profile found in database — skipping.\n")

# ── 3. Ambulance Need ─────────────────────────────────────────────────────────
print("🚑 Seeding AmbulanceNeedPost...")
AmbulanceNeedPost.objects.filter(address='Seed Pickup Address').delete()
p = AmbulanceNeedPost.objects.create(
    user=user, division=div, district=dist, upozila=upz,
    ambulance_type='icu',
    address='Seed Pickup Address',
    contact_number='01811000002',
    needed_date='2025-09-02', needed_time='08:00:00',
    urgency='critical',
    description='ICU ambulance needed urgently for cardiac patient transfer to NICVD.',
    status='open',
)
attach_images(p, IMG)
print(f"  Created AmbulanceNeedPost id={p.id}\n")

# ── 4. Equipment Sell ─────────────────────────────────────────────────────────
print("🔧 Seeding EquipmentSellPost...")
EquipmentSellPost.objects.filter(equipment_name='Seed Oxygen Cylinder').delete()
p = EquipmentSellPost.objects.create(
    user=user, division=div, district=dist, upozila=upz,
    equipment_name='Seed Oxygen Cylinder',
    quantity='1', condition='good', price=3500,
    address='House 5, Road 3, Dhaka',
    contact_number='01811000003',
    description='Used oxygen cylinder in good condition. Patient has recovered. Comes with regulator and trolley.',
    status='open',
)
attach_images(p, IMG)
print(f"  Created EquipmentSellPost id={p.id}\n")

# ── 5. Equipment Need ─────────────────────────────────────────────────────────
print("🩺 Seeding EquipmentNeedPost...")
EquipmentNeedPost.objects.filter(equipment_name='Seed Wheelchair').delete()
p = EquipmentNeedPost.objects.create(
    user=user, division=div, district=dist, upozila=upz,
    equipment_name='Seed Wheelchair',
    quantity='1', condition='good',
    address='House 12, Mirpur, Dhaka',
    contact_number='01811000004',
    urgency='medium',
    description='Need a wheelchair for elderly patient. Can rent or borrow. Please contact.',
    status='open',
)
attach_images(p, IMG)
print(f"  Created EquipmentNeedPost id={p.id}\n")

# ── 6. Medicine (Buy/Sell) ────────────────────────────────────────────────────
print("💊 Seeding MedicinePost (sell)...")
MedicinePost.objects.filter(medicine_name='Seed Insulin Glargine').delete()
p = MedicinePost.objects.create(
    user=user, division=div, district=dist, upozila=upz,
    listing_type='sell',
    medicine_name='Seed Insulin Glargine 100IU',
    quantity='3 vials', price=1200,
    address='House 7, Gulshan, Dhaka',
    contact_number='01811000005',
    description='Unused insulin vials, bought extra. Expiry 2026. Selling at low price to help others.',
    status='open',
)
attach_images(p, IMG)
print(f"  Created MedicinePost (sell) id={p.id}\n")

print("💉 Seeding MedicinePost (buy)...")
MedicinePost.objects.filter(medicine_name='Seed Warfarin 5mg').delete()
p = MedicinePost.objects.create(
    user=user, division=div, district=dist, upozila=upz,
    listing_type='buy',
    medicine_name='Seed Warfarin 5mg',
    quantity='2 strips',
    address='House 9, Sylhet Sadar',
    contact_number='01811000006',
    description='Heart patient urgently needs Warfarin 5mg. Not available locally. Please help.',
    status='open',
)
attach_images(p, IMG)
print(f"  Created MedicinePost (buy) id={p.id}\n")

# ── 7. Medicine Need ──────────────────────────────────────────────────────────
print("💉 Seeding MedicineNeedPost...")
MedicineNeedPost.objects.filter(medicine_name='Seed Metformin 500mg').delete()
p = MedicineNeedPost.objects.create(
    user=user, division=div, district=dist, upozila=upz,
    medicine_name='Seed Metformin 500mg',
    quantity='3 strips',
    address='House 3, Khulna Sadar',
    contact_number='01811000007',
    urgency='high',
    description='Diabetic patient needs Metformin urgently. Out of stock in local pharmacies.',
    status='open',
)
attach_images(p, IMG)
print(f"  Created MedicineNeedPost id={p.id}\n")

# ── 8. General Post ───────────────────────────────────────────────────────────
print("📝 Seeding GeneralPost...")
GeneralPost.objects.filter(title='Seed: Free Health Camp - Dhaka').delete()
p = GeneralPost.objects.create(
    user=user, division=div, district=dist, upozila=upz,
    title='Seed: Free Health Camp - Dhaka',
    content='A free health camp will be held this Friday at Savar Upazila Health Complex from 9am to 4pm. All are welcome. Free checkup, blood pressure, diabetes screening available.',
    contact_number='01811000008',
    status='open',
)
attach_images(p, IMG)
print(f"  Created GeneralPost id={p.id}\n")

print("=" * 50)
print("✅ All community post types seeded with images!")
print(f"  BloodNeedPost:     {BloodNeedPost.objects.count()}")
print(f"  AmbulanceNeedPost: {AmbulanceNeedPost.objects.count()}")
print(f"  EquipmentSellPost: {EquipmentSellPost.objects.count()}")
print(f"  EquipmentNeedPost: {EquipmentNeedPost.objects.count()}")
print(f"  MedicinePost:      {MedicinePost.objects.count()}")
print(f"  MedicineNeedPost:  {MedicineNeedPost.objects.count()}")
print(f"  GeneralPost:       {GeneralPost.objects.count()}")
print(f"  PostImage:         {PostImage.objects.count()}")
