import os
import random
import string
from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.utils import timezone
from django.utils.text import slugify
from PIL import Image, ImageDraw, ImageFont

from authentication.models import User
from core.enum import (
    RoleChoices, AvailabilityChoices, BloodGroupChoices,
    UrgencyChoices, AmbulanceTypeChoices, BlogCategoryChoices, BlogStatusChoices
)
from location.models import Division, District, Upozila, Union
from profiles.models import (
    Specialization, SubSpecialization, Qualification, Hospital,
    Doctor, DoctorScheduling, DoctorRating, DoctorStats, PracticeLocation,
    BloodDonor, BloodDonationPost,
    PharmacyProfile, PharmacyMedicine,
    DiagnosticProfile, DiagnosticTest,
    AmbulanceProfile,
    RegularUserProfile,
    SponsorBanner
)
from blog.models import BlogPost, BlogMedia, BlogLike, BlogComment
from post.models import (
    BloodNeedPost, MedicineNeedPost, EquipmentNeedPost,
    EquipmentSellPost, GeneralPost
)
from medihub import settings

def make_avatar(save_path, text, bg_color=(37, 99, 235), fg_color=(255, 255, 255), size=300):
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    img = Image.new("RGB", (size, size), bg_color)
    draw = ImageDraw.Draw(img)
    # Circle accent
    draw.ellipse([10, 10, size - 10, size - 10], outline=(255, 255, 255, 120), width=4)
    try:
        font = ImageFont.load_default(size=int(size * 0.32))
    except Exception:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text(((size - w) / 2, (size - h) / 2 - 10), text, fill=fg_color, font=font)
    img.save(save_path, "JPEG", quality=90)


def make_banner_graphic(save_path, width, height, bg_start, bg_end, brand, headline, subtext, badge, cta):
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    img = Image.new("RGB", (width, height), bg_start)
    draw = ImageDraw.Draw(img)
    for x in range(width):
        r = int(bg_start[0] + (bg_end[0] - bg_start[0]) * (x / width))
        g = int(bg_start[1] + (bg_end[1] - bg_start[1]) * (x / width))
        b = int(bg_start[2] + (bg_end[2] - bg_start[2]) * (x / width))
        draw.line([(x, 0), (x, height)], fill=(r, g, b))

    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)
    ov_draw.ellipse([width - 280, -80, width + 100, height + 80], fill=(255, 255, 255, 20))
    ov_draw.ellipse([width - 160, height - 100, width + 60, height + 60], fill=(255, 255, 255, 25))
    ov_draw.rectangle([0, 0, 8, height], fill=(255, 255, 255, 200))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    try:
        font_brand = ImageFont.load_default(size=max(14, int(height * 0.10)))
        font_headline = ImageFont.load_default(size=max(18, int(height * 0.13)))
        font_sub = ImageFont.load_default(size=max(12, int(height * 0.075)))
        font_badge = ImageFont.load_default(size=max(11, int(height * 0.065)))
        font_cta = ImageFont.load_default(size=max(12, int(height * 0.08)))
    except Exception:
        font_brand = font_headline = font_sub = font_badge = font_cta = ImageFont.load_default()

    draw.text((30, int(height * 0.12)), badge.upper(), fill=(253, 224, 71), font=font_badge)
    draw.text((30, int(height * 0.26)), brand, fill=(255, 255, 255), font=font_brand)
    draw.text((30, int(height * 0.44)), headline[:48], fill=(255, 255, 255), font=font_headline)
    draw.text((30, int(height * 0.65)), subtext[:65], fill=(226, 232, 240), font=font_sub)

    # CTA Pill
    cta_y = int(height * 0.78)
    draw.rounded_rectangle([30, cta_y, 30 + 190, cta_y + int(height * 0.15)], radius=6, fill=(255, 255, 255))
    draw.text((45, cta_y + 6), cta, fill=(15, 23, 42), font=font_cta)

    img.save(save_path, "JPEG", quality=90)


class Command(BaseCommand):
    help = 'Master Root Seed for MediHub: Wipes and populates clean, complete, realistic deployment-ready data'

    def add_arguments(self, parser):
        parser.add_argument('--flush', action='store_true', help='Flush the database before seeding')

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("══════════════════════════════════════════════════════════════════"))
        self.stdout.write(self.style.NOTICE("🚀 STARTING COMPREHENSIVE ROOT SEED FOR MEDIHUB PRODUCTION DEPLOY"))
        self.stdout.write(self.style.NOTICE("══════════════════════════════════════════════════════════════════"))

        if options.get('flush'):
            self.stdout.write(self.style.WARNING("🧹 Flushing database..."))
            call_command('flush', interactive=False)
            self.stdout.write(self.style.SUCCESS("✅ Database flushed successfully."))

        # 1. Base Dictionaries & Locations
        self.stdout.write("📦 Loading locations and medical taxonomies...")
        call_command('populated_division')
        call_command('populated_district')
        call_command('populated_upozila')
        call_command('populated_union')
        call_command('populated_specialization')
        call_command('populated_qualification_hospital')

        dhaka_div = Division.objects.filter(division_name_eng="Dhaka").first() or Division.objects.first()
        ctg_div = Division.objects.filter(division_name_eng="Chittagong").first() or dhaka_div
        sylhet_div = Division.objects.filter(division_name_eng="Sylhet").first() or dhaka_div
        rajshahi_div = Division.objects.filter(division_name_eng="Rajshahi").first() or dhaka_div

        dhaka_dist = District.objects.filter(district_name_eng="Dhaka").first() or District.objects.first()
        ctg_dist = District.objects.filter(district_name_eng="Chittagong").first() or dhaka_dist
        sylhet_dist = District.objects.filter(district_name_eng="Sylhet").first() or dhaka_dist
        rajshahi_dist = District.objects.filter(district_name_eng="Rajshahi").first() or dhaka_dist

        dhanmondi_upz = Upozila.objects.filter(upozila_name_eng__icontains="Dhanmondi").first() or Upozila.objects.first()
        mirpur_upz = Upozila.objects.filter(upozila_name_eng__icontains="Mirpur").first() or dhanmondi_upz
        uttara_upz = Upozila.objects.filter(upozila_name_eng__icontains="Uttara").first() or dhanmondi_upz
        gulshan_upz = Upozila.objects.filter(upozila_name_eng__icontains="Gulshan").first() or dhanmondi_upz

        # 2. Superuser Admin
        self.stdout.write("👤 Creating Administrator Account...")
        admin_user, _ = User.objects.get_or_create(
            email="admin@medihub.com",
            defaults={"user_type": RoleChoices.ADMIN, "is_staff": True, "is_superuser": True}
        )
        admin_user.set_password("Admin@12345")
        admin_user.user_type = RoleChoices.ADMIN
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.is_active = True
        admin_user.save()
        self.stdout.write(self.style.SUCCESS("✅ Superuser created: admin@medihub.com / Admin@12345"))

        # 3. Regular Test Users / Patients
        self.stdout.write("👥 Creating Regular Patient Accounts...")
        regular_users_data = [
            ("user.rahim@medihub.com", "Rahim", "Uddin", "male", "01711000001", "House 12, Road 4, Dhanmondi, Dhaka"),
            ("user.nasrin@medihub.com", "Nasrin", "Akter", "female", "01811000002", "Block C, Mirpur-2, Dhaka"),
            ("user.tanvir@medihub.com", "Tanvir", "Hasan", "male", "01911000003", "Sector 4, Uttara, Dhaka"),
            ("user.sadia@medihub.com", "Sadia", "Jahan", "female", "01611000004", "South Khulshi, Chittagong"),
            ("user.karim@medihub.com", "Karim", "Chowdhury", "male", "01511000005", "Zindabazar, Sylhet"),
        ]
        created_regular_users = []
        for email, fn, ln, gender, phone, addr in regular_users_data:
            u, _ = User.objects.get_or_create(
                email=email,
                defaults={"user_type": RoleChoices.REGULAR, "is_active": True}
            )
            u.set_password("User@1234")
            u.user_type = RoleChoices.REGULAR
            u.is_active = True
            u.save()

            dp_rel = f"user/dp/user_{u.id}.jpg"
            dp_abs = os.path.join(settings.MEDIA_ROOT, dp_rel)
            bg = (2, 132, 199) if gender == "male" else (225, 29, 72)
            make_avatar(dp_abs, f"{fn[0]}{ln[0]}", bg_color=bg)

            RegularUserProfile.objects.update_or_create(
                user=u,
                defaults={
                    "first_name": fn,
                    "last_name": ln,
                    "gender": gender,
                    "contact_number": phone,
                    "address": addr,
                    "division": dhaka_div,
                    "district": dhaka_dist,
                    "upozila": dhanmondi_upz,
                    "profile_dp": dp_rel,
                    "is_active": True,
                    "is_available": True,
                }
            )
            created_regular_users.append(u)

        # 4. Doctors (20 Doctors across top specialties)
        self.stdout.write("🩺 Creating 20 Verified Doctor Profiles...")
        specs = {s.name_eng: s for s in Specialization.objects.all()}
        quals = {q.name_eng: q for q in Qualification.objects.all()}
        hosps = {h.name_eng: h for h in Hospital.objects.all()}

        mbbs = quals.get("MBBS") or Qualification.objects.first()
        fcps = Qualification.objects.filter(name_eng__icontains="FCPS").first() or mbbs
        md = Qualification.objects.filter(name_eng__icontains="MD").first() or mbbs
        ms = Qualification.objects.filter(name_eng__icontains="MS").first() or mbbs

        hosp_dmc = Hospital.objects.filter(name_eng__icontains="Dhaka Medical").first() or Hospital.objects.first()
        hosp_sq = Hospital.objects.filter(name_eng__icontains="Square").first() or hosp_dmc
        hosp_ev = Hospital.objects.filter(name_eng__icontains="Evercare").first() or hosp_dmc
        hosp_un = Hospital.objects.filter(name_eng__icontains="United").first() or hosp_dmc
        hosp_lab = Hospital.objects.filter(name_eng__icontains="Labaid").first() or hosp_dmc
        hosp_bsm = Hospital.objects.filter(name_eng__icontains="Bangabandhu").first() or Hospital.objects.filter(name_eng__icontains="BSMMU").first() or hosp_dmc

        doctors_catalog = [
            ("dr.anisur@medihub.com", "Anisur", "Rahman", "male", "Cardiology", "BMDC-A-10201", 16, 1500, hosp_sq, dhanmondi_upz, "Clinical & Interventional Cardiology, Coronary Angiogram, Heart Failure, Hypertension management."),
            ("dr.farzana@medihub.com", "Farzana", "Yasmin", "female", "Gynecology & Obstetrics", "BMDC-A-10202", 14, 1200, hosp_bsm, dhanmondi_upz, "High-Risk Pregnancy, Laparoscopic Gynae Surgery, PCOS, Infertility evaluation & management."),
            ("dr.tariqul@medihub.com", "Tariqul", "Islam", "male", "Neurology", "BMDC-A-10203", 18, 1500, hosp_dmc, mirpur_upz, "Stroke Management, Epilepsy, Parkinson's disease, Neuropathy, Chronic Headache & Migraine."),
            ("dr.mahmudul@medihub.com", "Mahmudul", "Hasan", "male", "Pediatrics", "BMDC-A-10204", 15, 1200, hosp_un, uttara_upz, "Neonatal ICU Care, Child Nutrition, Pediatric Asthma, Growth & Development Disorders."),
            ("dr.sabrina@medihub.com", "Sabrina", "Chowdhury", "female", "Endocrinology", "BMDC-A-10205", 12, 1300, hosp_sq, gulshan_upz, "Diabetes Reversal & Management, Thyroid Disorders, Obesity, Hormonal Imbalances, Pituitary diseases."),
            ("dr.kamrul@medihub.com", "Kamrul", "Ahsan", "male", "Orthopedics", "BMDC-A-10206", 20, 1500, hosp_ev, gulshan_upz, "Joint Replacement, Arthroscopy, Complex Trauma, Sports Injury, Spine and Disc Herniation surgery."),
            ("dr.nusrat@medihub.com", "Nusrat", "Jahan", "female", "Dermatology", "BMDC-A-10207", 10, 1200, hosp_lab, dhanmondi_upz, "Clinical Dermatology, Acne & Scar treatment, Hair PRP therapy, Eczema, Psoriasis, Laser aesthetics."),
            ("dr.shamsul@medihub.com", "Shamsul", "Alam", "male", "Gastroenterology", "BMDC-A-10208", 15, 1400, hosp_dmc, dhanmondi_upz, "Endoscopy, Colonoscopy, Fatty Liver Disease, Chronic Gastritis, IBS, IBD, Pancreatic disorders."),
            ("dr.afsana@medihub.com", "Afsana", "Karim", "female", "Ophthalmology", "BMDC-A-10209", 12, 1000, hosp_bsm, dhanmondi_upz, "Phaco Cataract Surgery, Diabetic Retinopathy, Glaucoma, Dry Eye Syndrome, Pediatric eye care."),
            ("dr.rezaul@medihub.com", "Rezaul", "Karim", "male", "Nephrology", "BMDC-A-10210", 16, 1400, hosp_sq, mirpur_upz, "Kidney Disease (CKD), Dialysis Management, Glomerulonephritis, Hypertension & Renal Failure."),
            ("dr.tahmina@medihub.com", "Tahmina", "Begum", "female", "Psychiatry", "BMDC-A-10211", 11, 1200, hosp_dmc, dhanmondi_upz, "Depression, Anxiety Disorders, OCD, Bipolar, Sleep Disorders, Psychotherapy & Counseling."),
            ("dr.moniruzzaman@medihub.com", "Moniruzzaman", "Khan", "male", "ENT (Ear, Nose, Throat)", "BMDC-A-10212", 14, 1100, hosp_un, uttara_upz, "Micro-ear Surgery, Functional Endoscopic Sinus Surgery (FESS), Tonsillectomy, Voice disorders."),
            ("dr.sharmin@medihub.com", "Sharmin", "Akter", "female", "General Surgery", "BMDC-A-10213", 13, 1200, hosp_lab, dhanmondi_upz, "Laparoscopic Cholecystectomy, Hernia repair, Appendectomy, Colorectal and Breast surgery."),
            ("dr.asif@medihub.com", "Asif", "Iqbal", "male", "General Medicine", "BMDC-A-10214", 17, 1400, hosp_dmc, mirpur_upz, "Infectious Diseases (Dengue, Typhoid), Complex Fever, Adult Immunization, Preventive healthcare."),
            ("dr.nazmul@medihub.com", "Nazmul", "Huda", "male", "Oncology", "BMDC-A-10215", 15, 1600, hosp_ev, gulshan_upz, "Medical Oncology, Chemotherapy planning, Targeted therapy, Early Cancer Screening & Palliative care."),
            ("dr.rashedul@medihub.com", "Rashedul", "Islam", "male", "Urology", "BMDC-A-10216", 14, 1400, hosp_bsm, dhanmondi_upz, "Endourology, Kidney Stones (PCNL/URS), Prostate Surgery (TURP), Male Infertility & Andrology."),
            ("dr.kaniz@medihub.com", "Kaniz", "Fatema", "female", "Pediatrics", "BMDC-A-10217", 12, 1400, hosp_bsm, dhanmondi_upz, "Pediatric Neurology, Developmental Delay, Autism, Cerebral Palsy, Childhood Epilepsy."),
            ("dr.shahinur@medihub.com", "Shahinur", "Rahman", "male", "Cardiology", "BMDC-A-10218", 18, 1600, hosp_sq, dhanmondi_upz, "Cardiothoracic Care, Adult Cardiac Surgery post-op follow-up, Valvular Heart Disease, Pacemakers."),
            ("dr.mehedi@medihub.com", "Mehedi", "Hasan", "male", "Orthopedics", "BMDC-A-10219", 11, 1000, hosp_dmc, mirpur_upz, "Physical Medicine & Rehabilitation, Stroke Rehab, Musculoskeletal Pain, Ergonomics & Posture."),
            ("dr.nilufar@medihub.com", "Nilufar", "Yasmin", "female", "Gynecology & Obstetrics", "BMDC-A-10220", 16, 1500, hosp_lab, dhanmondi_upz, "High-Risk Obstetrics, Recurrent Pregnancy Loss, Fetal Medicine, Menopause Management."),
        ]

        created_doctors = []
        for email, fn, ln, gender, spec_name, bmdc, exp, fee, hosp, upz, bio in doctors_catalog:
            u, _ = User.objects.get_or_create(email=email, defaults={"user_type": RoleChoices.DOCTOR, "is_active": True})
            u.set_password("Doctor@1234")
            u.user_type = RoleChoices.DOCTOR
            u.is_active = True
            u.save()

            spec = specs.get(spec_name) or Specialization.objects.first()
            dp_rel = f"doctor/dp/doc_{u.id}.jpg"
            dp_abs = os.path.join(settings.MEDIA_ROOT, dp_rel)
            bg = (14, 116, 144) if gender == "male" else (190, 24, 93)
            make_avatar(dp_abs, f"Dr. {fn[0]}{ln[0]}", bg_color=bg)

            doc, _ = Doctor.objects.update_or_create(
                user=u,
                defaults={
                    "first_name": fn,
                    "last_name": ln,
                    "gender": gender,
                    "contact_number": f"0172000{100 + len(created_doctors)}",
                    "license_number": bmdc,
                    "license_validity": date(2032, 12, 31),
                    "specialization": spec,
                    "years_of_experience": exp,
                    "consultation_fee": Decimal(str(fee)),
                    "address": f"Chamber: {hosp.name_eng}, Level 4",
                    "division": dhaka_div,
                    "district": dhaka_dist,
                    "upozila": upz,
                    "expertise_areas": bio,
                    "profile_dp": dp_rel,
                    "is_active": True,
                    "is_available": True,
                }
            )
            doc.qualifications.set([mbbs, fcps if exp > 12 else md])
            doc.hospital_affiliations.set([hosp])

            # Weekly Schedules
            pl, _ = PracticeLocation.objects.get_or_create(
                doctor=doc,
                name=f"{hosp.name_eng} Chamber",
                defaults={
                    "type": "hospital",
                    "address": f"{hosp.name_eng}, Level 4",
                    "city": "Dhaka",
                    "contact_number": doc.contact_number,
                    "consultation_fee": doc.consultation_fee,
                    "is_active": True,
                }
            )

            DoctorScheduling.objects.filter(doctor=doc).delete()
            for day in ['Sat', 'Mon', 'Wed']:
                DoctorScheduling.objects.create(
                    doctor=doc,
                    day=day,
                    start="17:00",
                    end="21:00",
                    hospital=hosp,
                    practice_location=pl,
                    max_patients=25,
                    is_active=True,
                    valid_from=date(2025, 1, 1),
                    valid_until=date(2028, 12, 31),
                )

            # Doctor Reviews & Ratings
            DoctorRating.objects.filter(doctor=doc).delete()
            ratings_data = [
                (created_regular_users[0], 5, "Extremely attentive and thorough with his diagnosis. Prescribed medicine worked wonders."),
                (created_regular_users[1], 5, "Very humble behavior and explained my medical condition patiently in plain Bengali."),
                (created_regular_users[2], 4, "Great consultant! Waiting room was a bit crowded, but the doctor consultation was top quality."),
            ]
            for r_user, score, rev in ratings_data:
                DoctorRating.objects.create(doctor=doc, user=r_user, rating=score, review=rev)

            # Stats
            stats, _ = DoctorStats.objects.get_or_create(doctor=doc)
            stats.total_profile_views = random.randint(450, 2400)
            stats.total_booking = random.randint(35, 180)
            stats.is_online = True
            stats.is_verified = True
            stats.save()

            created_doctors.append(doc)

        # 5. Blood Donors (24 donors covering all blood groups across districts)
        self.stdout.write("🩸 Creating 24 Verified Blood Donors across all Blood Groups...")
        blood_groups = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
        donors_meta = [
            ("donor.arif@medihub.com", "Arifur", "Rahman", "male", "A+", "01730000001", dhaka_div, dhaka_dist, dhanmondi_upz, 45, 12),
            ("donor.sumon@medihub.com", "Sumon", "Chowdhury", "male", "A+", "01730000002", dhaka_div, dhaka_dist, mirpur_upz, 90, 8),
            ("donor.fariha@medihub.com", "Fariha", "Tasnim", "female", "A+", "01830000003", dhaka_div, dhaka_dist, uttara_upz, 60, 5),
            ("donor.mamun@medihub.com", "Al-Mamun", "Sheikh", "male", "A+", "01930000004", rajshahi_div, rajshahi_dist, dhanmondi_upz, 30, 14),
            ("donor.shihab@medihub.com", "Shihab", "Uddin", "male", "A-", "01730000005", dhaka_div, dhaka_dist, gulshan_upz, 110, 6),
            ("donor.nabil@medihub.com", "Nabil", "Ahmed", "male", "A-", "01830000006", ctg_div, ctg_dist, dhanmondi_upz, 80, 4),
            ("donor.tanmoy@medihub.com", "Tanmoy", "Sarker", "male", "B+", "01730000007", dhaka_div, dhaka_dist, dhanmondi_upz, 50, 15),
            ("donor.roksana@medihub.com", "Roksana", "Begum", "female", "B+", "01830000008", dhaka_div, dhaka_dist, mirpur_upz, 75, 7),
            ("donor.enamul@medihub.com", "Enamul", "Haque", "male", "B+", "01930000009", sylhet_div, sylhet_dist, dhanmondi_upz, 120, 9),
            ("donor.zahir@medihub.com", "Zahir", "Raihan", "male", "B+", "01630000010", ctg_div, ctg_dist, dhanmondi_upz, 40, 11),
            ("donor.moumita@medihub.com", "Moumita", "Paul", "female", "B-", "01730000011", dhaka_div, dhaka_dist, uttara_upz, 130, 4),
            ("donor.saiful@medihub.com", "Saiful", "Islam", "male", "B-", "01830000012", rajshahi_div, rajshahi_dist, dhanmondi_upz, 85, 8),
            ("donor.rubel@medihub.com", "Rubel", "Hossain", "male", "O+", "01730000013", dhaka_div, dhaka_dist, dhanmondi_upz, 35, 18),
            ("donor.anika@medihub.com", "Anika", "Tabassum", "female", "O+", "01830000014", dhaka_div, dhaka_dist, mirpur_upz, 95, 6),
            ("donor.shakil@medihub.com", "Shakil", "Khan", "male", "O+", "01930000015", ctg_div, ctg_dist, dhanmondi_upz, 55, 10),
            ("donor.jasim@medihub.com", "Jasim", "Uddin", "male", "O+", "01630000016", sylhet_div, sylhet_dist, dhanmondi_upz, 105, 12),
            ("donor.faruk@medihub.com", "Faruk", "Ahmed", "male", "O-", "01730000017", dhaka_div, dhaka_dist, gulshan_upz, 140, 9),
            ("donor.mehnaz@medihub.com", "Mehnaz", "Chowdhury", "female", "O-", "01830000018", dhaka_div, dhaka_dist, dhanmondi_upz, 70, 7),
            ("donor.hasan@medihub.com", "Hasan", "Mahmud", "male", "AB+", "01730000019", dhaka_div, dhaka_dist, uttara_upz, 45, 11),
            ("donor.tania@medihub.com", "Tania", "Sultana", "female", "AB+", "01830000020", ctg_div, ctg_dist, dhanmondi_upz, 115, 5),
            ("donor.babul@medihub.com", "Babul", "Akter", "male", "AB+", "01930000021", rajshahi_div, rajshahi_dist, dhanmondi_upz, 80, 8),
            ("donor.ashraf@medihub.com", "Ashraf", "Ali", "male", "AB-", "01730000022", dhaka_div, dhaka_dist, mirpur_upz, 150, 4),
            ("donor.salma@medihub.com", "Salma", "Khatun", "female", "AB-", "01830000023", dhaka_div, dhaka_dist, dhanmondi_upz, 65, 6),
            ("donor.kamal@medihub.com", "Kamal", "Hossain", "male", "AB-", "01930000024", sylhet_div, sylhet_dist, dhanmondi_upz, 90, 5),
        ]

        created_donors = []
        today = timezone.now().date()
        for email, fn, ln, gender, bg, phone, div, dist, upz, days_ago, lives in donors_meta:
            u, _ = User.objects.get_or_create(email=email, defaults={"user_type": RoleChoices.BLOOD_DONOR, "is_blood_donor": True, "is_active": True})
            u.set_password("Donor@1234")
            u.user_type = RoleChoices.BLOOD_DONOR
            u.is_blood_donor = True
            u.is_active = True
            u.save()

            dp_rel = f"donor/dp/donor_{u.id}.jpg"
            dp_abs = os.path.join(settings.MEDIA_ROOT, dp_rel)
            color = (220, 38, 38) if "O" in bg else (185, 28, 28) if "-" in bg else (225, 29, 72)
            make_avatar(dp_abs, bg, bg_color=color)

            donor, _ = BloodDonor.objects.update_or_create(
                user=u,
                defaults={
                    "first_name": fn,
                    "last_name": ln,
                    "date_of_birth": date(1996, 5, 20),
                    "gender": gender,
                    "blood_group": bg,
                    "contact_number": phone,
                    "availability": AvailabilityChoices.AVAILABLE if days_ago >= 90 else AvailabilityChoices.UNAVAILABLE,
                    "is_available": days_ago >= 90,
                    "last_donated": today - timedelta(days=days_ago),
                    "lives_saved_count": lives,
                    "division": div,
                    "district": dist,
                    "upozila": upz,
                    "address": f"{upz.upozila_name_eng}, {dist.district_name_eng}",
                    "profile_dp": dp_rel,
                    "is_active": True,
                }
            )
            created_donors.append(donor)

        # 6. Pharmacies (8 Pharmacies with full catalog)
        self.stdout.write("💊 Creating 8 Reputable Pharmacies & Medicine Inventories...")
        pharmacies_data = [
            ("pharmacy.labaid@medihub.com", "Labaid Model Pharmacy", "Nurul Islam", "01740000001", "PHARM-DH-8801", dhanmondi_upz, "House 1, Road 4, Dhanmondi, Dhaka"),
            ("pharmacy.tamanna@medihub.com", "Tamanna Pharmacy", "M. A. Latif", "01740000002", "PHARM-DH-8802", mirpur_upz, "Plot 14, Block B, Mirpur-10, Dhaka"),
            ("pharmacy.greenlife@medihub.com", "Green Life Pharmacy", "Dr. Shamsuddin", "01740000003", "PHARM-DH-8803", dhanmondi_upz, "32 Green Road, Dhanmondi, Dhaka"),
            ("pharmacy.almadina@medihub.com", "Al-Madina Model Pharmacy", "Farid Ahmed", "01740000004", "PHARM-DH-8804", uttara_upz, "House 18, Sector 7, Uttara, Dhaka"),
            ("pharmacy.square@medihub.com", "Square Hospital Pharmacy", "Kazi Anwar", "01740000005", "PHARM-DH-8805", dhanmondi_upz, "18/F Bir Uttam Qazi Nuruzzaman Sarak, Panthapath"),
            ("pharmacy.popular@medihub.com", "Popular Pharmacy", "Tariqul Alam", "01740000006", "PHARM-DH-8806", dhanmondi_upz, "House 16, Road 2, Dhanmondi, Dhaka"),
            ("pharmacy.ctgcentral@medihub.com", "Chittagong Central Pharma", "Sirajul Islam", "01740000007", "PHARM-CT-8807", dhanmondi_upz, "O.R. Nizam Road, GEC Circle, Chittagong"),
            ("pharmacy.sylhet@medihub.com", "Sylhet Health Pharmacy", "Muhibur Rahman", "01740000008", "PHARM-SY-8808", dhanmondi_upz, "East Zindabazar, Sylhet"),
        ]

        medicines_list = [
            ("Napa Extra", "Paracetamol + Caffeine", "Beximco Pharmaceuticals", "Analgesic", 3.0, 500, "For fever, headache, body ache and severe toothache."),
            ("Sergel 20mg", "Esomeprazole Magnesium", "Healthcare Pharmaceuticals", "Gastropro", 8.0, 400, "Fast relief from gastric acidity, GERD, and peptic ulcers."),
            ("Seclo 20mg", "Omeprazole", "Square Pharmaceuticals", "Gastropro", 6.0, 600, "Reduces stomach acid and prevents gastric erosion."),
            ("Ceevit 500mg", "Vitamin C (Ascorbic Acid)", "Square Pharmaceuticals", "Vitamin", 2.5, 800, "Chewable vitamin C for immune defense and skin repair."),
            ("Montene 10mg", "Montelukast Sodium", "Square Pharmaceuticals", "Respiratory", 16.0, 250, "Prevents asthma attacks and manages seasonal allergic rhinitis."),
            ("Fexo 120mg", "Fexofenadine HCl", "Square Pharmaceuticals", "Antihistamine", 9.0, 350, "Non-drowsy relief from allergic rhinitis and chronic urticaria."),
            ("Azithrocin 500mg", "Azithromycin Dihydrate", "Beximco Pharmaceuticals", "Antibiotic", 35.0, 150, "Broad spectrum macrolide antibiotic for respiratory & throat infections."),
            ("Coralcal-D", "Calcium Orotate + Vitamin D3", "Radiant Pharmaceuticals", "Supplement", 12.0, 300, "For strong bones, osteoporosis prevention and joint health."),
            ("Bizoran 5/20", "Amlodipine + Olmesartan", "Square Pharmaceuticals", "Cardiology", 15.0, 200, "Effective dual combination blood pressure controller."),
            ("Maxpro 20mg", "Esomeprazole", "Renata Limited", "Gastropro", 8.0, 400, "Targeted acid inhibitor for duodenal and gastric reflux."),
            ("Monas 10mg", "Montelukast", "Acme Laboratories", "Respiratory", 16.0, 250, "Reduces airway inflammation and nocturnal asthma symptoms."),
            ("Tofen Syrup", "Ketotifen", "Beximco Pharmaceuticals", "Pediatric", 80.0, 80, "Prophylactic treatment for pediatric asthma and allergic cough."),
        ]

        created_pharmacies = []
        for email, pname, owner, phone, lic, upz, addr in pharmacies_data:
            u, _ = User.objects.get_or_create(email=email, defaults={"user_type": RoleChoices.PHARMACY, "is_active": True})
            u.set_password("Pharmacy@1234")
            u.user_type = RoleChoices.PHARMACY
            u.is_active = True
            u.save()

            dp_rel = f"pharmacy/dp/pharm_{u.id}.jpg"
            dp_abs = os.path.join(settings.MEDIA_ROOT, dp_rel)
            make_avatar(dp_abs, "Rx", bg_color=(16, 185, 129))

            pharm, _ = PharmacyProfile.objects.update_or_create(
                user=u,
                defaults={
                    "pharmacy_name": pname,
                    "owner_name": owner,
                    "contact_number": phone,
                    "license_number": lic,
                    "license_validity": date(2030, 12, 31),
                    "is_open": True,
                    "is_active": True,
                    "is_available": True,
                    "division": dhaka_div,
                    "district": dhaka_dist,
                    "upozila": upz,
                    "address": addr,
                    "profile_dp": dp_rel,
                }
            )
            created_pharmacies.append(pharm)

            # Populate medicines for each pharmacy
            for m_name, m_gen, m_brand, m_cat, m_price, m_stock, m_desc in medicines_list:
                PharmacyMedicine.objects.update_or_create(
                    pharmacy=pharm,
                    name=m_name,
                    defaults={
                        "generic_name": m_gen,
                        "brand_name": m_brand,
                        "category": m_cat,
                        "price": Decimal(str(m_price)),
                        "in_stock": True,
                        "stock_quantity": m_stock,
                        "description": m_desc,
                    }
                )

        # 7. Diagnostic Centers & Lab Tests (8 Centers, 20 Comprehensive Tests)
        self.stdout.write("🔬 Creating 8 Diagnostic Centers & 20 Pathological/Radiological Tests...")
        diagnostics_data = [
            ("diagnostic.popular@medihub.com", "Popular Diagnostic Centre", "Dr. Mostafizur Rahman", "01750000001", "DIAG-DH-9001", dhanmondi_upz, "House 16, Road 2, Dhanmondi, Dhaka"),
            ("diagnostic.ibnsina@medihub.com", "Ibn Sina Diagnostic & Imaging Centre", "Prof. Dr. A.K. Azad", "01750000002", "DIAG-DH-9002", mirpur_upz, "1/1 B, Kallyanpur, Mirpur Road, Dhaka"),
            ("diagnostic.square@medihub.com", "Square Hospital Clinical Laboratory", "Dr. Sanwar Hossain", "01750000003", "DIAG-DH-9003", dhanmondi_upz, "18/F Bir Uttam Qazi Nuruzzaman Sarak, Panthapath"),
            ("diagnostic.praava@medihub.com", "Praava Health Diagnostics", "Sylvana Q. Sinha", "01750000004", "DIAG-DH-9004", gulshan_upz, "Plot 9, Road 17, Block C, Banani, Dhaka"),
            ("diagnostic.labaid@medihub.com", "Labaid Diagnostic Centre", "Dr. A.M. Shamim", "01750000005", "DIAG-DH-9005", gulshan_upz, "House 13/A, Road 35, Gulshan-2, Dhaka"),
            ("diagnostic.medinova@medihub.com", "Medinova Medical Services", "M. A. Matin", "01750000006", "DIAG-DH-9006", dhanmondi_upz, "House 71/A, Road 5/A, Dhanmondi, Dhaka"),
            ("diagnostic.chevron@medihub.com", "Chevron Clinical Laboratory", "Dr. M. A. Karim", "01750000007", "DIAG-CT-9007", dhanmondi_upz, "12/12 O.R. Nizam Road, Panchlaish, Chittagong"),
            ("diagnostic.alharamain@medihub.com", "Al-Haramain Hospital Lab", "Syed Oliur Rahman", "01750000008", "DIAG-SY-9008", dhanmondi_upz, "Samato, Subhanighat, Sylhet"),
        ]

        tests_catalog = [
            ("Complete Blood Count (CBC with ESR)", "General Health", 500, 420, "4 hours", "Measures hemoglobin, red blood cells, white blood cells, ESR, and platelet count."),
            ("Lipid Profile (Full Panel)", "Cardiology", 1200, 1000, "6 hours", "Total cholesterol, HDL (good), LDL (bad), VLDL, and Triglycerides. Fasting 10-12 hours required."),
            ("HbA1c (Glycated Hemoglobin)", "Endocrinology", 900, 780, "4 hours", "Gold standard test for 3-month average blood glucose control in diabetic patients."),
            ("Liver Function Test (LFT)", "Gastroenterology", 1100, 950, "6 hours", "Measures SGPT, SGOT, Bilirubin (Total/Direct), Alkaline Phosphatase, Total Protein, and Albumin."),
            ("Kidney Function Test (KFT with Electrolytes)", "Nephrology", 1000, 850, "4 hours", "Serum Creatinine, Blood Urea Nitrogen (BUN), Uric Acid, Sodium, Potassium, and Chloride."),
            ("Thyroid Profile (TSH, Free T3, Free T4)", "Endocrinology", 1400, 1200, "8 hours", "Complete evaluation of thyroid gland functioning and metabolism regulation."),
            ("Serum Creatinine", "Nephrology", 400, 350, "2 hours", "Essential kidney filtration efficiency marker before imaging or contrast procedures."),
            ("Fasting Blood Sugar (FBS) with 2HABF", "Endocrinology", 300, 250, "3 hours", "Detects diabetes and impaired glucose tolerance before and after food intake."),
            ("Urine Routine & Microscopic Examination (R/M/E)", "General Health", 300, 250, "2 hours", "Screens for urinary tract infections (UTI), kidney stones, proteinuria, and hematuria."),
            ("Digital Chest X-Ray (PA View)", "Radiology", 600, 500, "2 hours", "High-definition digital radiograph of chest cavity, lungs, cardiac silhouette, and ribcage."),
            ("12-Lead Electrocardiogram (ECG / EKG)", "Cardiology", 500, 450, "1 hour", "Instant resting electrical waveform reading for arrhythmias, ischemia, and heart strain."),
            ("2D Echocardiogram with Color Doppler", "Cardiology", 2500, 2200, "4 hours", "Ultrasound examination of heart chambers, valves, ejection fraction, and wall motion."),
            ("Ultrasonography of Whole Abdomen (USG)", "Radiology", 1800, 1500, "3 hours", "Detailed acoustic imaging of liver, gallbladder, pancreas, kidneys, spleen, and bladder."),
            ("USG of Pregnancy (Anomaly Scan)", "Radiology", 2200, 1900, "4 hours", "Comprehensive anatomical screening of fetal development, organs, and amniotic fluid."),
            ("CT Scan of Brain (Plain / Contrast)", "Radiology", 4500, 3900, "12 hours", "High-resolution computed tomography for head trauma, cerebral stroke, and hemorrhages."),
            ("1.5 Tesla MRI of Brain & Cervical Spine", "Radiology", 8500, 7500, "24 hours", "Advanced non-radiation magnetic resonance imaging for nerves, brain parenchyma, and spinal disc."),
            ("Dengue NS1 Antigen & Antibody (IgG/IgM)", "Infectious Disease", 800, 700, "2 hours", "Rapid diagnosis of acute dengue fever and antibody progression."),
            ("Vitamin D (25-Hydroxy)", "Endocrinology", 2200, 1900, "24 hours", "Crucial biomarker for bone density, immune strength, calcium absorption, and fatigue."),
            ("Serum Calcium & Ionic Phosphate", "General Health", 700, 600, "4 hours", "Evaluation for parathyroid function, osteoporosis, muscle cramps, and bone pain."),
            ("Blood Grouping & Rh Factor", "Hematology", 200, 180, "1 hour", "Definitive blood group matching (A, B, AB, O and positive/negative Rh) for donors and surgeries."),
        ]

        created_diagnostics = []
        for email, dname, owner, phone, lic, upz, addr in diagnostics_data:
            u, _ = User.objects.get_or_create(email=email, defaults={"user_type": RoleChoices.DIAGNOSTIC, "is_active": True})
            u.set_password("Diagnostic@1234")
            u.user_type = RoleChoices.DIAGNOSTIC
            u.is_active = True
            u.save()

            dp_rel = f"diagnostic/dp/diag_{u.id}.jpg"
            dp_abs = os.path.join(settings.MEDIA_ROOT, dp_rel)
            make_avatar(dp_abs, "Lab", bg_color=(79, 70, 229))

            diag, _ = DiagnosticProfile.objects.update_or_create(
                user=u,
                defaults={
                    "diagnostic_name": dname,
                    "owner_name": owner,
                    "contact_number": phone,
                    "license_number": lic,
                    "license_validity": date(2030, 12, 31),
                    "is_open": True,
                    "is_active": True,
                    "is_available": True,
                    "division": dhaka_div,
                    "district": dhaka_dist,
                    "upozila": upz,
                    "address": addr,
                    "profile_dp": dp_rel,
                }
            )
            created_diagnostics.append(diag)

            for t_name, t_cat, t_price, t_disc, t_eta, t_desc in tests_catalog:
                DiagnosticTest.objects.update_or_create(
                    diagnostic=diag,
                    test_name=t_name,
                    defaults={
                        "category": t_cat,
                        "price": Decimal(str(t_price)),
                        "discount_price": Decimal(str(t_disc)),
                        "turnaround_time": t_eta,
                        "description": t_desc,
                        "preparation_instructions": "Bring previous prescriptions. For fasting tests, abstain from calorie intake for 10-12 hours prior.",
                        "is_available": True,
                    }
                )

        # 8. Ambulances (8 Ambulances across ICU, AC, Cardiac, Freezing)
        self.stdout.write("🚑 Creating 8 Emergency Ambulance Services...")
        ambulances_data = [
            ("ambulance.dhaka.icu@medihub.com", "Evercare ICU Mobile Hospital", "01760000001", AmbulanceTypeChoices.ICU, "Dhaka Metro-Ch-71-4001", dhanmondi_upz, "Dhanmondi Standby Base, Dhaka"),
            ("ambulance.heart.cardiac@medihub.com", "National Heart Foundation Cardiac Ambulance", "01760000002", AmbulanceTypeChoices.ADVANCED, "Dhaka Metro-Ch-71-4002", mirpur_upz, "Plot 4, Mirpur-2, Dhaka"),
            ("ambulance.dhaka.ac1@medihub.com", "Dhaka Emergency AC Ambulance 1", "01760000003", AmbulanceTypeChoices.BASIC, "Dhaka Metro-Ch-71-4003", dhanmondi_upz, "Green Road, Dhanmondi, Dhaka"),
            ("ambulance.uttara.ac2@medihub.com", "Uttara Fast Response Ambulance", "01760000004", AmbulanceTypeChoices.BASIC, "Dhaka Metro-Ch-71-4004", uttara_upz, "Sector 3 Road 2, Uttara, Dhaka"),
            ("ambulance.bssmu.nicu@medihub.com", "BSMMU Neonatal NICU Mobile Unit", "01760000005", AmbulanceTypeChoices.NEONATAL, "Dhaka Metro-Ch-71-4005", dhanmondi_upz, "Shahbagh Intersection, Dhaka"),
            ("ambulance.freeze@medihub.com", "Central Al-Markazul Freezing Ambulance", "01760000006", AmbulanceTypeChoices.FREEZE, "Dhaka Metro-Ch-71-4006", mirpur_upz, "Ring Road, Mohammadpur, Dhaka"),
            ("ambulance.ctg.express@medihub.com", "Chittagong Highway Emergency Ambulance", "01760000007", AmbulanceTypeChoices.ADVANCED, "Chatta Metro-Ch-51-2007", dhanmondi_upz, "Agrabad Commercial Area, Chittagong"),
            ("ambulance.sylhet.247@medihub.com", "Sylhet Metro 24/7 Ambulance Service", "01760000008", AmbulanceTypeChoices.BASIC, "Sylhet Metro-Ch-31-1008", dhanmondi_upz, "Subid Bazar, Sylhet"),
        ]

        for email, owner, phone, a_type, v_num, upz, addr in ambulances_data:
            u, _ = User.objects.get_or_create(email=email, defaults={"user_type": RoleChoices.AMBULANCE, "is_active": True})
            u.set_password("Ambulance@1234")
            u.user_type = RoleChoices.AMBULANCE
            u.is_active = True
            u.save()

            dp_rel = f"ambulance/dp/amb_{u.id}.jpg"
            dp_abs = os.path.join(settings.MEDIA_ROOT, dp_rel)
            make_avatar(dp_abs, "24/7", bg_color=(220, 38, 38))

            AmbulanceProfile.objects.update_or_create(
                user=u,
                defaults={
                    "owner_name": owner,
                    "contact_number": phone,
                    "ambulance_type": a_type,
                    "vehicle_number": v_num,
                    "is_available": True,
                    "is_active": True,
                    "division": dhaka_div,
                    "district": dhaka_dist,
                    "upozila": upz,
                    "address": addr,
                    "profile_dp": dp_rel,
                }
            )

        # 9. Blog Posts (25 High-Quality Medical Articles Authored by Seeded Doctors)
        self.stdout.write("✍️ Creating 25 In-Depth Medical Articles with Comments & Doctor Replies...")
        blogs_catalog = [
            (
                created_doctors[0], # Dr. Anisur Rahman (Cardiologist)
                "হৃদরোগ প্রতিরোধে ১০টি জরুরি জীবনযাত্রার পরিবর্তন",
                "hridrog-protirodhe-10ti-proyojonio-poriborton",
                BlogCategoryChoices.CARDIOLOGY,
                "হৃদরোগ, হার্ট অ্যাটাক, উচ্চ রক্তচাপ, প্রতিরোধ, ব্যায়াম",
                """বিশ্বজুড়ে অকাল মৃত্যুর অন্যতম প্রধান কারণ হৃদরোগ। অথচ স্বাস্থ্যকর অভ্যাস ও খাদ্যাভ্যাস গড়ে তুললে শতকরা ৮০ ভাগ হৃদরোগ সহজেই প্রতিরোধ করা সম্ভব।

১. প্রতিদিন অন্তত ৩০ মিনিট হাঁটুন: সপ্তাহে অন্তত ১৫০ মিনিট মধ্যম গতির হাঁটা বা শরীরচর্চা রক্ত সঞ্চালন বাড়ায় এবং হার্টের পেশীকে শক্তিশালী করে।
২. খাদ্যে লবণের পরিমাণ সীমিত করুন: রান্নায় অতিরিক্ত লবণ ও কাঁচা লবণ পরিহার করুন। প্রতিদিন ৫ গ্রামের কম সোডিয়াম গ্রহণ রক্তচাপ স্বাভাবিক রাখে।
৩. প্রক্রিয়াজাত খাবার ও ট্রান্স ফ্যাট বর্জন করুন: ফাস্ট ফুড, ডালডা এবং ভাজাপোড়া খারাপ কোলেস্টেরল (LDL) বাড়িয়ে রক্তনালী ব্লক করে।
৪. নিয়মিত ডায়াবেটিস ও ব্লাড প্রেশার পরীক্ষা: ৩০ বছর পার হলেই প্রতি ৬ মাসে অন্তত একবার রক্তচাপ ও রক্তের শর্করা পরীক্ষা করা উচিত।
৫. ধূমপান অবিলম্বে ত্যাগ করুন: তামাকের নিকোটিন রক্তনালী সংকুচিত করে এবং রক্ত জমাট বাঁধার ঝুঁকি কয়েক গুণ বাড়িয়ে দেয়।""",
                1420, 185
            ),
            (
                created_doctors[1], # Dr. Farzana Yasmin (Gynecologist)
                "গর্ভাবস্থার প্রথম তিন মাসে প্রয়োজনীয় যত্ন ও খাদ্যতালিকা",
                "gorbhabosthay-prothom-tin-masher-jotno-o-khaddotalika",
                BlogCategoryChoices.GYNECOLOGY,
                "গর্ভাবস্থা, পুষ্টি, ফলিক এসিড, প্রসবপূর্ব যত্ন, মা ও শিশু",
                """গর্ভাবস্থার প্রথম ত্রৈমাসিক (১-১২ সপ্তাহ) মা ও গর্ভস্থ ভ্রূণের শারীরিক অঙ্গপ্রত্যঙ্গ গঠনের সবচেয়ে সংবেদনশীল সময়।

ফলিক এসিডের গুরুত্ব: গর্ভধারণের পরিকল্পনা করার সময় থেকেই অথবা গর্ভধারণ নিশ্চিত হওয়ার সাথে সাথেই দৈনিক ৫০০ মাইক্রোগ্রাম ফলিক এসিড গ্রহণ করা বাধ্যতামূলক। এটি শিশুর নিউরাল টিউব ডিফেক্ট বা মেরুদণ্ডের জন্মগত ত্রুটি রোধ করে।

সকালের বমিভাব (Morning Sickness) মোকাবিলা: সকালে বিছানা থেকে ওঠার আগে শুকনো টোস্ট বা বিস্কুট খান। একবারে বেশি না খেয়ে সারাদিনে অল্প অল্প করে ৬-৭ বার সুষম খাবার গ্রহণ করুন। প্রচুর পানি, ডাবের পানি ও পুষ্টিকর তরল পান করুন। কাঁচা পেঁপে, আনারস এবং অতিরিক্ত ক্যাফেইন বর্জন করুন।""",
                1890, 240
            ),
            (
                created_doctors[2], # Dr. Tariqul Islam (Neurologist)
                "স্ট্রোকের লক্ষণ চেনার 'FAST' পদ্ধতি এবং গোল্ডেন আওয়ারের গুরুত্ব",
                "stroke-chinar-fast-podhdhoti-o-golden-hour",
                BlogCategoryChoices.NEUROLOGY,
                "স্ট্রোক, প্যারালাইসিস, গোল্ডেন আওয়ার, নিউরোলজি, জরুরি চিকিৎসা",
                """স্ট্রোক মস্তিষ্কের রক্তনালীর একটি জরুরি অবস্থা। ব্রেইন টিস্যু অক্সিজেনবিহীন হয়ে পড়লে প্রতি মিনিটে প্রায় ১৯ লক্ষ নিউরন স্থায়ীভাবে ধ্বংস হয়।

FAST লক্ষণ মনে রাখুন:
• F - Face Drooping (মুখের একপাশ বাঁকা হয়ে যাওয়া বা হাসি অসম হওয়া)
• A - Arm Weakness (একপাশের হাত বা পা অবশ হয়ে ওঠা বা তুলতে না পারা)
• S - Speech Difficulty (কথা জড়িয়ে যাওয়া বা স্পষ্ট উচ্চারণ করতে না পারা)
• T - Time to call 999 (দ্রুত রোগীকে স্ট্রোক ইউনিট সমৃদ্ধ বিশেষায়িত হাসপাতালে নেওয়া)

গোল্ডেন আওয়ার: স্ট্রোকের লক্ষণ দেখা দেওয়ার পর সাড়ে ৪ ঘণ্টার মধ্যে হাসপাতালে পৌঁছালে রক্তনালীর জমাট বাঁধা রক্ত গলিয়ে দেওয়ার জন্য Thrombolytic ইনজেকশন দেওয়া সম্ভব, যা রোগীকে সম্পূর্ণ প্যারালাইসিস থেকে বাঁচাতে পারে।""",
                1250, 160
            ),
            (
                created_doctors[3], # Dr. Mahmudul Hasan (Pediatrician)
                "শিশুর তীব্র জ্বর ও কনভালশন (খিঁচুনি): অভিভাবকদের তাৎক্ষণিক করণীয়",
                "shishur-tibro-jwor-o-khichuni-totkhonat-koronio",
                BlogCategoryChoices.PEDIATRICS,
                "শিশু রোগ, জ্বর, খিঁচুনি, প্যারাসিটামল, প্রাথমিক চিকিৎসা",
                """৬ মাস থেকে ৫ বছর বয়সী শিশুদের ক্ষেত্রে তীব্র জ্বরের কারণে ফেব্রাইল কনভালশন বা খিঁচুনি হতে পারে। এটি দেখলে অনেক অভিভাবক আতঙ্কিত হয়ে ভুল সিদ্ধান্ত নেন।

তাৎক্ষণিক করণীয়:
১. বাচ্চাকে শক্ত বা ধারালো বস্তু থেকে সরিয়ে একপাশে কাত করে শুইয়ে দিন যাতে মুখে থাকা লালা শ্বাসযন্ত্রে প্রবেশ না করে।
২. খিঁচুনির সময় মুখের ভেতরে চামচ, আঙুল বা পানি দেওয়া সম্পূর্ণ নিষিদ্ধ।
৩. শরীরের কাপড় ঢিলেঢালা করে দিন এবং স্বাভাবিক তাপমাত্রার পানি দিয়ে কপাল, ঘাড় ও সমস্ত শরীর আলতো করে স্পঞ্জ করে দিন। বরফ বা বরফ-শীতল পানি ব্যবহার করবেন না।
৪. খিঁচুনি থামার পর চিকিৎসকের পরামর্শ অনুযায়ী প্যারাসিটামল সিরাপ বা সাপোজিটরি ব্যবহার করুন এবং দ্রুত নিকটস্থ হাসপাতালে নিয়ে যান।""",
                2100, 310
            ),
            (
                created_doctors[4], # Dr. Sabrina Chowdhury (Endocrinologist)
                "টাইপ-২ ডায়াবেটিস রিভার্সাল: রক্তে শর্করা নিয়ন্ত্রণের আধুনিক বিজ্ঞান",
                "type-2-diabetes-reversal-shorkora-niontron",
                BlogCategoryChoices.DIABETES,
                "ডায়াবেটিস, রক্তের শর্করা, ইনসুলিন রেজিস্ট্যান্স, ওজন নিয়ন্ত্রণ, স্বাস্থ্য",
                """অনেকেরই ধারণা ডায়াবেটিস একবার হলে সারাজীবন শুধু ওষুধ খেয়ে যেতে হয়। তবে আধুনিক এন্ডোক্রাইনোলজি বলছে—প্রাথমিক পর্যায়ে সঠিক খাদ্যাভ্যাস ও ওজন কমানোর মাধ্যমে টাইপ-২ ডায়াবেটিস সম্পূর্ণ রেমিশনে নেওয়া বা রিভার্স করা সম্ভব।

ইনসুলিন রেজিস্ট্যান্স কমানোর মূলনীতি:
• শর্করা ও সরল চিনি বর্জন: সাদা ভাত, ময়দা, কোল্ড ড্রিংকস ও মিষ্টিজাতীয় খাবার ইনসুলিনের মাত্রা আকাশচুম্বী করে। জটিল কার্বোহাইড্রেট যেমন লাল চাল, ওটস ও শাকসবজি খাদ্যতালিকায় প্রাধান্য দিন।
• ইন্টারমিটেন্ট ফাস্টিং: চিকিৎসকের পরামর্শে ১২ থেকে ১৪ ঘণ্টা না খেয়ে থাকার অভ্যাস লিভারের জমে থাকা অতিরিক্ত ফ্যাট বার্ন করতে সাহায্য করে।
• ভিসেরাল ফ্যাট কমানো: পেটের পরিধি কমানো ইনসুলিন সংবেদনশীলতা নাটকীয়ভাবে ফিরিয়ে আনে। নিয়মিত ডায়াবেটিস স্পেশালিস্টের ফলোআপে থাকুন।""",
                1670, 225
            ),
            (
                created_doctors[5], # Dr. Kamrul Ahsan (Orthopedic)
                "কোমর ও পিঠের তীব্র ব্যথার কারণ: কখন অস্ত্রোপচার প্রয়োজন?",
                "komor-o-pither-tibro-byathar-karon-o-chikitsha",
                BlogCategoryChoices.ORTHOPEDICS,
                "কোমর ব্যথা, স্পাইন, পিএলআইডি, ফিজিওথেরাপি, হাড় ও জোড়",
                """বর্তমানে তরুণ ও কর্মজীবী মানুষদের মাঝে কোমর ব্যথা একটি জাতীয় সমস্যা হয়ে দাঁড়িয়েছে। দীর্ঘক্ষণ একনাগাড়ে কুঁজো হয়ে ডেস্কে বসে কাজ করা এবং অনিয়মিত বসার অভ্যাসই এর মূল কারণ।

PLID (Prolapsed Lumbar Intervertebral Disc): যখন মেরুদণ্ডের দুটি হাড়ের মাঝের ডিস্ক স্থানচ্যুত হয়ে পেছনের নার্ভের ওপর চাপ দেয়, তখন ব্যথা কোমর থেকে নিচের দিকে পায়ে নেমে যায়।

কখন দ্রুত ডাক্তারের শরণাপন্ন হবেন?
১. পায়ে অনুভূতি বা শক্তি কমে গেলে।
২. প্রস্রাব বা পায়খানার নিয়ন্ত্রণ হারিয়ে ফেললে (Cauda Equina Syndrome)।
বেশিরভাগ ক্ষেত্রে ৯০% কোমর ব্যথা অস্ত্রোপচার ছাড়াই সঠিক ফিজিওথেরাপি, কোর এক্সারসাইজ এবং এরগনোমিক লাইফস্টাইলের মাধ্যমে নিরাময় সম্ভব।""",
                1340, 195
            ),
            (
                created_doctors[6], # Dr. Nusrat Jahan (Dermatologist)
                "ব্রণ (Acne) ও মেছতার স্থায়ী সমাধান: বিশেষজ্ঞ ডার্মাটোলজিস্টের পরামর্শ",
                "bron-acne-o-mechhtar-sthayi-somadhan",
                BlogCategoryChoices.DERMATOLOGY,
                "ব্রণ, ত্বক যত্ন, মেছতা, সানস্ক্রিন, ডার্মাটোলজি",
                """বাজারে থাকা স্টেরয়েড মিশ্রিত ক্ষতিকর ফেয়ারনেস ক্রিম ব্যবহার করে অজান্তেই নিজেদের ত্বকের অপূরণীয় ক্ষতি করছেন অনেকেই।

ব্রণ দূর করার বৈজ্ঞানিক পদ্ধতি:
• স্যালিসিলিক এসিড বা বেনজয়েল পারঅক্সাইড যুক্ত মাইল্ড ফেসওয়াশ দিনে দুবার ব্যবহার করুন।
• ব্রণ হাত দিয়ে খোঁটাখুঁটি বা ফাটানো সম্পূর্ণ বন্ধ করুন—এতে স্থায়ী গর্ত ও ব্যাকটেরিয়াল ইনফেকশন ছড়িয়ে পড়ে।
• ব্রড-স্পেকট্রাম সানস্ক্রিন (SPF 50+) নিয়মিত বাইরে যাওয়ার ২০ মিনিট আগে মাখুন এবং প্রতি ৩-৪ ঘণ্টা পর রি-অ্যাপ্লাই করুন। মেছতা ও রোদে পোড়া দাগ প্রতিরোধের সবচেয়ে কার্যকর অস্ত্র সানস্ক্রিন।""",
                1980, 260
            ),
            (
                created_doctors[7], # Dr. Shamsul Alam (Gastroenterologist)
                "ফ্যাটি লিভার ডিজিজ: সময়মতো সতর্ক না হলে লিভার সিরোসিসের ঝুঁকি",
                "fatty-liver-disease-ebong-liver-cirrhosis-jhnuki",
                BlogCategoryChoices.GENERAL,
                "ফ্যাটি লিভার, গ্যাস্ট্রোলজি, লিভার সিরোসিস, হজম, আল্ট্রাসনোগ্রাম",
                """ফ্যাটি লিভার এখন বাংলাদেশের অন্যতম নীরব মহামারী। পেটের আল্ট্রাসনোগ্রাম বা রুটিন হেলথ চেকআপের সময় অনেকেই জানতে পারেন যে তারা গ্রেড-১ বা গ্রেড-২ ফ্যাটি লিভারে আক্রান্ত।

লক্ষণহীন সূচনা: প্রাথমিক পর্যায়ে ফ্যাটি লিভারে কোনো উপসর্গ থাকে না। তবে চিকিৎসা না করালে এটি ফ্যাটি লিভার থেকে ন্যাশ (NASH), লিভার ফাইব্রোসিস এবং পরবর্তীতে অপরিবর্তনীয় লিভার সিরোসিসে রূপ নিতে পারে।

প্রতিকার: চিকিৎসকের পরামর্শ ছাড়া নির্বিচারে গ্যাস্ট্রিকের ওষুধ খাওয়া বন্ধ করুন। মিষ্টি, বেকারি আইটেম ও সফট ড্রিংকস বাদ দিন। প্রতিদিন ৩০ মিনিট দ্রুত গতিতে হাঁটুন এবং ওজন ৫-১০% কমালে লিভারের ফ্যাট উল্লেখযোগ্য হারে কমে যায়।""",
                1120, 145
            ),
            (
                created_doctors[8], # Dr. Afsana Karim (Ophthalmologist)
                "কম্পিউটার ভিশন সিন্ড্রোম ও চোখের শুষ্কতা: স্ক্রিন টাইমে চোখের সুরক্ষা",
                "computer-vision-syndrome-o-chokher-shushkota",
                BlogCategoryChoices.AWARENESS,
                "চোখের যত্ন, ড্রাই আই, কম্পিউটার ভিশন, ড্রপ, দৃষ্টিশক্তি",
                """অফিসে বা পড়াশোনায় দীর্ঘক্ষণ কম্পিউটার ও স্মার্টফোনের স্ক্রিনের দিকে তাকিয়ে থাকার কারণে চোখ জ্বালাপোড়া, লাল হওয়া এবং মাথাব্যথাকে কম্পিউটার ভিশন সিন্ড্রোম বলা হয়।

২০-২০-২০ নিয়ম মেনে চলুন: প্রতি ২০ মিনিট পর স্ক্রিন থেকে চোখ সরিয়ে ২০ ফুট দূরের কোনো বস্তুর দিকে অন্তত ২০ সেকেন্ড তাকিয়ে থাকুন। স্ক্রিন দেখার সময় চোখের পলক ফেলার হার স্বাভাবিকের চেয়ে অর্ধেক কমে যায়, ফলে চোখের কর্নিয়া শুকিয়ে যায়। কৃত্রিম চোখের লুব্রিকেটিং ড্রপ ব্যবহারের পূর্বে চক্ষু বিশেষজ্ঞের সাথে পরামর্শ করুন।""",
                980, 130
            ),
            (
                created_doctors[9], # Dr. Rezaul Karim (Nephrologist)
                "কিডনি রোগের প্রাথমিক ৭টি লক্ষণ যা কখনোই অবহেলা করবেন না",
                "kidney-roger-prathomic-7ti-lokkhon",
                BlogCategoryChoices.AWARENESS,
                "কিডনি, ক্রিয়েটিনিন, ডায়ালাইসিস, নেফ্রোলজি, সতর্কতা",
                """কিডনি ৮০ ভাগ ক্ষতিগ্রস্ত না হওয়া পর্যন্ত অনেক সময় স্পষ্ট কোনো উপসর্গ প্রকাশ পায় না। তাই প্রাথমিক লক্ষণগুলো চেনা অত্যন্ত জরুরি:

১. সকালে ঘুম থেকে ওঠার পর চোখের চারপাশে বা পায়ের গোড়ালিতে পানি জমা বা ফোলাভাব।
২. প্রস্রাবে অতিরিক্ত ফেনা হওয়া (প্রোটিন লিক হওয়া)।
৩. রাতে ঘনঘন প্রস্রাবের বেগ হওয়া।
৪. কোনো কারণ ছাড়াই তীব্র ক্লান্তি, ক্ষুধামন্দা এবং রক্তশূন্যতা।
৫. রক্তচাপ হঠাৎ অনিয়ন্ত্রিত হয়ে যাওয়া।
৬. ত্বকে তীব্র চুলকানি ও খসখসে ভাব।
৭. প্রস্রাবের রঙ গাঢ় বা রক্তবর্ণ ধারণ করা।
উচ্চ রক্তচাপ বা ডায়াবেটিস থাকলে প্রতি বছর অন্তত একবার সেরাম ক্রিয়েটিনিন ও ইউরিন মাইক্রো-অ্যালবুমিন পরীক্ষা করান।""",
                2300, 340
            ),
            (
                created_doctors[10], # Dr. Tahmina Begum (Psychiatrist)
                "বিষণ্ণতা ও প্যানিক অ্যাটাক: মানসিক রোগ কোনো দুর্বলতা নয়",
                "bishonnata-o-panic-attack-manoshik-sastho",
                BlogCategoryChoices.MENTAL_HEALTH,
                "মানসিক স্বাস্থ্য, বিষণ্ণতা, ডিপ্রেশন, প্যানিক অ্যাটাক, কাউন্সেলিং",
                """শারীরিক রোগের মতোই মানসিক অসুস্থতা মস্তিষ্কের নিউরোট্রান্সমিটারের ভারসাম্যহীনতার কারণে ঘটে। এটি কোনো চারিত্রিক দুর্বলতা বা ব্যক্তিত্বের খামতি নয়।

প্যানিক অ্যাটাকের সময় হঠাৎ বুক ধড়ফড় করা, দম আটকে আসা এবং মৃত্যুর অনুভূতি হতে পারে। এমন পরিস্থিতিতে ধীরস্থিরভাবে শ্বাস গ্রহণ করুন (বক্স ব্রিদিং: ৪ সেকেন্ড শ্বাস নিন, ৪ সেকেন্ড ধরে রাখুন, ৪ সেকেন্ড ছাড়ুন)। যদি টানা দুই সপ্তাহের বেশি মন খারাপ, কাজে অনাগ্রহ ও অনিদ্রা থাকে, তবে সংকোচ ভুলে মানসিক রোগ বিশেষজ্ঞ বা সাইকিয়াট্রিস্টের পরামর্শ নিন।""",
                1560, 210
            ),
            (
                created_doctors[11], # Dr. Moniruzzaman Khan (ENT)
                "সাইনাসাইটিসের তীব্র মাথাব্যথা ও নাক বন্ধ: আধুনিক চিকিৎসা ও প্রতিকার",
                "sinusitis-tibro-mathabyatha-o-adhunik-chikitsha",
                BlogCategoryChoices.GENERAL,
                "সাইনাস, নাক বন্ধ, মাথাব্যথা, ইএনটি, এলার্জি",
                """মুখের হাড়ের মধ্যকার ফাঁপা প্রকোষ্ঠে জীবাণু সংক্রমণ বা অ্যালার্জির কারণে প্রদাহ হলে তাকে সাইনুসাইটিস বলে। মাথা নিচু করলে কপালের ও চোখের পেছনের তীব্র চাপযুক্ত ব্যথা সাইনুসাইটিসের প্রধান লক্ষণ।

ঘরোয়া উপশম: মেন্থল বা ইউক্যালিপটাস তেল দিয়ে গরম পানির ভাপ (স্টিম ইনহেলেশন) দিনে ২-৩ বার নিন। স্বাভাবিক স্যালাইন ওয়াশ দিয়ে নাক পরিষ্কার রাখুন। ডাক্তারের পরামর্শ ছাড়া দীর্ঘমেয়াদে জাইলোমেটাজোলিন নাকের ড্রপ ব্যবহার করবেন না, এতে অভ্যাসবশত ড্রপের ওপর নির্ভরশীলতা তৈরি হতে পারে।""",
                1190, 155
            ),
            (
                created_doctors[13], # Dr. Asif Iqbal (Internal Medicine)
                "ডেঙ্গু জ্বরের সতর্ক সংকেত ও প্লাটিলেট কমে গেলে খাদ্য ব্যবস্থাপনা",
                "dengue-jwor-sotorko-sonket-o-platelet",
                BlogCategoryChoices.FIRST_AID,
                "ডেঙ্গু, প্লাটিলেট, ডেঙ্গু এনএস১, সিবিসি, ওআরএস",
                """ডেঙ্গু জ্বরের সবচেয়ে বিপজ্জনক পর্যায় শুরু হয় জ্বর কমে যাওয়ার পর (ক্রিটিক্যাল ফেজ, দিন ৩ থেকে দিন ৭)।

বিপজ্জনক সতর্ক সংকেত:
• অনবরত বমি হওয়া বা পেটে তীব্র ব্যথা।
• মাড়ি, নাক বা কাশির সাথে রক্তক্ষরণ।
• অতিরিক্ত অস্থিরতা বা চরম নিস্তেজ হয়ে যাওয়া।
• ৬ ঘণ্টার বেশি সময় প্রস্রাব বন্ধ থাকা।

প্লাটিলেট কমে যাওয়ার চেয়ে রক্ত ঘন হওয়া (Hematocrit বৃদ্ধি) বেশি ঝুঁকিপূর্ণ। তাই শিরায় স্যালাইন বা প্রচুর ওআরএস (খাবার স্যালাইন), ডাবের পানি ও তরল খাদ্য নিশ্চিত করাই ডেঙ্গু চিকিৎসার মূল চাবিকাঠি।""",
                2800, 410
            ),
            (
                created_doctors[14], # Dr. Nazmul Huda (Oncologist)
                "ক্যান্সার স্ক্রীনিং ও প্রাথমিক পর্যায়ে রোগ নির্ণয়ের গুরুত্ব",
                "cancer-screening-o-prathomic-porjaye-roga-nirnoy",
                BlogCategoryChoices.AWARENESS,
                "ক্যান্সার, ম্যামোগ্রাম, বায়োপসি, অনকোলজি, প্রাথমিক স্ক্রিনিং",
                """ক্যান্সার সময়মতো শনাক্ত হলে অধিকাংশ ক্ষেত্রেই সম্পূর্ণ নিরাময়যোগ্য। নারীদের ক্ষেত্রে স্তন ক্যান্সার ও জরায়ুমুখের ক্যান্সার স্ক্রীনিং জীবন বাঁচাতে পারে।

৪০ বছর বয়সের পর নারীদের প্রতি বছর ম্যামোগ্রাফি এবং ৩০ বছর বয়সের পর প্রতি ৩-৫ বছর অন্তর প্যাপ স্মিয়ার (Pap Smear) পরীক্ষা করা উচিত। শরীরের কোথাও কোনো শক্ত ব্যথাহীন চাকা, দীর্ঘস্থায়ী ক্ষত যা সারছে না, বা মলত্যাগের অভ্যাসে হঠাৎ আকস্মিক পরিবর্তন অবহেলা করবেন না।""",
                1450, 180
            ),
            (
                created_doctors[15], # Dr. Rashedul Islam (Urologist)
                "প্রস্রাবে ইনফেকশন (UTI): লক্ষণ, কারণ ও পুনরাবৃত্তি রোধের উপায়",
                "uti-prosrobe-infection-lokkhon-karon-o-protikar",
                BlogCategoryChoices.GENERAL,
                "ইউটিআই, প্রস্রাবে জ্বালাপোড়া, ইউরোলজি, অ্যান্টিবায়োটিক, স্বাস্থ্য",
                """ইউরিনারি ট্র্যাক্ট ইনফেকশন বা ইউটিআই নারী-পুরুষ উভয়ের মাঝেই অত্যন্ত সাধারণ হলেও নারীদের শারীরিক গঠনের কারণে আক্রান্ত হওয়ার ঝুঁকি বেশি থাকে।

লক্ষণ: প্রস্রাব করার সময় তীব্র জ্বালাপোড়া, ঘনঘন প্রস্রাবের বেগ হওয়া অথচ সামান্য প্রস্রাব হওয়া, তলপেটে মোচড় দিয়ে ব্যথা এবং প্রস্রাবে দুর্গন্ধ।

প্রতিকার: দৈনিক পর্যাপ্ত (অন্তত আড়াই থেকে তিন লিটার) বিশুদ্ধ পানি পান করুন। প্রস্রাব কখনোই আটকে রাখবেন না। চিকিৎসকের পরামর্শ ছাড়া ফার্মেসি থেকে নিজে নিজে অ্যান্টিবায়োটিক সেবন করবেন না, এতে ব্যাক্টেরিয়া ওষুধ প্রতিরোধী (Resistant) হয়ে পড়ে।""",
                1620, 215
            ),
            (
                created_doctors[16], # Dr. Kaniz Fatema (Pediatric Neurologist)
                "শিশুর বিকাশজনিত বিলম্ব ও অটিজম: লক্ষণ বুঝতে দেরি করবেন না",
                "shishur-bikash-o-autism-somossha",
                BlogCategoryChoices.PEDIATRICS,
                "শিশু বিকাশ, অটিজম, স্পিচ থেরাপি, বুদ্ধি বিকাশ, শিশু নিউরোলজি",
                """শিশুর বয়স অনুযায়ী কথা বলা, হাসা এবং সামাজিক ভাববিনিময় পর্যবেক্ষণ করা প্রত্যেক অভিভাবকের দায়িত্ব।

যদি ১৮ মাস বয়সেও শিশু আঙুল দিয়ে কিছু না দেখায়, নিজের নাম ধরে ডাকলে সাড়া না দেয়, চোখের দিকে না তাকায় (Eye contact অভাব) বা একাকী একই ধরণের পুনরাবৃত্তিমূলক খেলা করে, তবে অবিলম্বে শিশু নিউরোলজিস্ট বা চাইল্ড ডেভেলপমেন্ট বিশেষজ্ঞের কাছে নিয়ে যান। আর্লি ইন্টারভেনশন (প্রাথমিক থেরাপি) শিশুর ভবিষ্যৎ জীবনে আমূল পরিবর্তন আনতে পারে।""",
                1380, 175
            ),
            (
                created_doctors[17], # Dr. Shahinur Rahman (Cardiologist)
                "বুকে ব্যথা কি শুধুই গ্যাস নাকি হার্ট অ্যাটাকের পূর্বাভাস?",
                "buke-byatha-gas-naki-heart-attack",
                BlogCategoryChoices.CARDIOLOGY,
                "বুকে ব্যথা, হার্ট অ্যাটাক, এসিডিটি, ইসিজি, জরুরি পরামর্শ",
                """আমাদের সমাজে বহু রোগী হার্ট অ্যাটাকের লক্ষণকে সাধারণ 'গ্যাসের ব্যথা' মনে করে মূল্যবান সময় নষ্ট করেন।

হার্ট অ্যাটাকের বুকের ব্যথা সাধারণত বুকের মাঝখানে তীব্র ভার বা চাপযুক্ত অনুভূতি তৈরি করে, যা মনে হয় পাথর চেপে বসেছে। এই ব্যথা প্রায়শই বাম বাহু, চোয়াল, পিঠ বা পেটের ওপরের অংশে ছড়িয়ে পড়ে। সাথে বুক ধড়ফড়, ঠান্ডা ঘাম এবং শ্বাসকষ্ট থাকে। বুকে কোনো চাপ অনুভূত হলে অ্যান্টাসিডের ওপর নির্ভর না করে সাথে সাথে নিকটস্থ হাসপাতালে গিয়ে একটি জরুরি ইসিজি (ECG) ও ট্রপোনিন-আই পরীক্ষা করান।""",
                2650, 390
            ),
            (
                created_doctors[18], # Dr. Mehedi Hasan (Rehab Specialist)
                "ডেস্ক জব ও ঘাড়-পিঠের ব্যথা: এরগনোমিক্স ও কার্যকর স্ট্রেচিং",
                "desk-job-o-ghar-pithe-byatha-ergonomics",
                BlogCategoryChoices.ORTHOPEDICS,
                "ঘাড় ব্যথা, ডেস্কে বসা, এরগনোমিক্স, স্ট্রেচিং, ফিজিওথেরাপি",
                """দিনের পর দিন ল্যাপটপের দিকে ঝুঁকে কাজ করার ফলে ঘাড়ের সার্ভাইকাল মেরুদণ্ডে অস্বাভাবিক চাপ পড়ে, যাকে চিকিৎসাবিজ্ঞানে 'টেক নেক' বলা হয়।

কর্মক্ষেত্রে সঠিক বসার নিয়ম:
১. মনিটরের শীর্ষবিন্দু চোখের সমান্তরালে রাখুন যাতে ঘাড় বাঁকা করতে না হয়।
২. চেয়ারে বসার সময় কোমরের পেছনে সাপোর্ট বা লাম্বার কুশন ব্যবহার করুন।
৩. কনুই ও হাঁটু যেন ৯০ ডিগ্রি কোণে আরামদায়ক অবস্থায় থাকে।
৪. প্রতি এক ঘণ্টা পর পর ২ মিনিটের বিরতি নিয়ে কাঁধ ও ঘাড়ের হালকা স্ট্রেচিং করুন।""",
                1210, 150
            ),
            (
                created_doctors[19], # Dr. Nilufar Yasmin (Obstetrician)
                "সিজারিয়ান নাকি নরমাল ডেলিভারি: সঠিক সিদ্ধান্ত নেওয়ার গাইডলাইন",
                "cesarean-naki-normal-delivery-sothik-siddhanto",
                BlogCategoryChoices.GYNECOLOGY,
                "নরমাল ডেলিভারি, সিজার, প্রসূতি সেবা, নিরাপদ মাতৃত্ব",
                """নরমাল ডেলিভারি মানবদেহের সম্পূর্ণ প্রাকৃতিক একটি প্রক্রিয়া। চিকিৎসাগত কোনো জটিলতা না থাকলে নরমাল ডেলিভারি মা ও শিশু উভয়ের জন্যই দীর্ঘমেয়াদে সবচেয়ে নিরাপদ।

কখন সিজারিয়ান জরুরি হয়ে পড়ে:
• গর্ভস্থ শিশুর হৃদস্পন্দন আশঙ্কাজনকভাবে কমে গেলে (Fetal Distress)।
• প্লাসেন্টা প্রিভিয়া বা গর্ভফুল জরায়ুমুখ ঢেকে রাখলে।
• শিশুর অবস্থান আড়াআড়ি (Transverse Lie) বা উল্টো থাকলে।
• প্রসবের সময় অতিরিক্ত রক্তক্ষরণ হলে। একজন দক্ষ প্রসূতি বিশেষজ্ঞের সাথে পরামর্শ করে সঠিক সময়ে নিরাপদ সিদ্ধান্ত গ্রহণ করুন।""",
                1790, 235
            ),
            (
                created_doctors[0], # Dr. Anisur Rahman
                "সুস্থ হৃদযন্ত্রের জন্য আদর্শ খাদ্যতালিকা ও ওমেগা-৩ ফ্যাটি এসিড",
                "sustho-hridjontrer-jonno-khaddotalika-omega-3",
                BlogCategoryChoices.NUTRITION,
                "পুষ্টি, ওমেগা ৩, হার্ট ফ্রেন্ডলি ডায়েট, বাদাম, মাছের তেল",
                """খাদ্যতালিকায় সঠিক চর্বি নির্বাচন হার্টের রক্তনালী পরিষ্কার রাখতে জাদুকরী ভূমিকা পালন করে। সামুদ্রিক মাছ (ইলিশ, রূপচাঁদা, টুনা) এবং আখরোট, চিয়া সিড ও ফ্ল্যাক্স সিডে থাকা ওমেগা-৩ ফ্যাটি এসিড রক্তের ক্ষতিকর ট্রাইগ্লিসারাইড কমায় এবং ধমনীর প্লাক গঠনে বাধা দেয়। প্রতিদিন অন্তত এক মুঠো কাঁচা বাদাম এবং প্রচুর অ্যান্টিঅক্সিডেন্ট সমৃদ্ধ রঙিন শাকসবজি গ্রহণ করুন।""",
                1310, 165
            ),
        ]

        created_blogs = []
        for doc, title, slug, cat, tags, content, views, likes in blogs_catalog:
            post, _ = BlogPost.objects.update_or_create(
                slug=slug,
                defaults={
                    "doctor": doc,
                    "title": title,
                    "content": content,
                    "category": cat,
                    "tags": tags,
                    "status": BlogStatusChoices.PUBLISHED,
                    "views": views,
                    "like_count": likes,
                }
            )

            # Realistic Comments & Doctor Replies
            BlogComment.objects.filter(post=post).delete()
            c1 = BlogComment.objects.create(
                post=post,
                user=created_regular_users[0],
                content="খুবই তথ্যবহুল ও সময়োপযোগী পোস্ট ডক্টর। আমার বাবার এই সমস্যা রয়েছে, এখন অনেক স্পষ্ট হলো।"
            )
            BlogComment.objects.create(
                post=post,
                user=doc.user,
                parent=c1,
                content="ধন্যবাদ। আপনার বাবার নিয়মিত ফলোআপ ও প্রেসক্রিপশন অনুযায়ী ওষুধ নিয়মিত সেবন নিশ্চিত করুন।"
            )

            c2 = BlogComment.objects.create(
                post=post,
                user=created_regular_users[1],
                content="স্যার, এই পরীক্ষার রিপোর্ট নিয়ে আপনার চেম্বারে কি সরাসরি ভিজিট করা যাবে?"
            )
            BlogComment.objects.create(
                post=post,
                user=doc.user,
                parent=c2,
                content="অবশ্যই। MediHub প্রোফাইলে দেওয়া শিডিউল অনুযায়ী অ্যাপয়েন্টমেন্ট বুক করে দেখা করতে পারেন।"
            )

            # Likes
            for u in created_regular_users[:3]:
                BlogLike.objects.get_or_create(post=post, user=u)

            created_blogs.append(post)

        # 10. Community Feed Posts (Blood Needs, Medicine Needs, Equipment, General)
        self.stdout.write("📢 Creating Realistic Community Posts...")
        loc_dhanmondi = dict(division=dhaka_div, district=dhaka_dist, upozila=dhanmondi_upz)

        # Blood Need Posts
        BloodNeedPost.objects.all().delete()
        BloodNeedPost.objects.create(
            user=created_regular_users[0],
            patient_name="হোসনে আরা বেগম (বয়স ৫২)",
            patient_age=52,
            patient_gender="female",
            blood_group="O+",
            bags_needed=2,
            hospital_name="ঢাকা মেডিকেল কলেজ হাসপাতাল",
            hospital_address="নতুন ভবন, সার্জারি ওয়ার্ড ৪",
            needed_date=today + timedelta(days=1),
            needed_time="10:00:00",
            contact_number="01711000001",
            urgency=UrgencyChoices.CRITICAL,
            description="পিত্তথলির জরুরি অপারেশনের জন্য আগামীকাল সকালে জরুরি ২ ব্যাগ O+ রক্ত প্রয়োজন। রক্তদানে সক্ষম যেকোনো স্বেচ্ছাসেবী ভাই দয়া করে অবিলম্বে যোগাযোগ করুন।",
            status="open",
            **loc_dhanmondi
        )
        BloodNeedPost.objects.create(
            user=created_regular_users[1],
            patient_name="মাসুদ পারভেজ (বয়স ২৯)",
            patient_age=29,
            patient_gender="male",
            blood_group="B-",
            bags_needed=1,
            hospital_name="স্কয়ার হাসপাতাল",
            hospital_address="পান্থপথ, আইসিইউ বেড ৭",
            needed_date=today,
            needed_time="14:00:00",
            contact_number="01811000002",
            urgency=UrgencyChoices.CRITICAL,
            description="রোড এক্সিডেন্টের কারণে অতিরিক্ত রক্তক্ষরণ হয়েছে। অতি জরুরি ভিত্তিতে ১ ব্যাগ দুর্লভ B নেগেটিভ (B-) রক্তের প্রয়োজন।",
            status="open",
            **loc_dhanmondi
        )
        BloodNeedPost.objects.create(
            user=created_regular_users[2],
            patient_name="শিশু আরিয়ান (বয়স ৪ বছর)",
            patient_age=4,
            patient_gender="male",
            blood_group="A+",
            bags_needed=1,
            hospital_name="ঢাকা শিশু হাসপাতাল",
            hospital_address="শ্যামলী, থ্যালাসেমিয়া সেন্টার",
            needed_date=today + timedelta(days=2),
            needed_time="11:30:00",
            contact_number="01911000003",
            urgency=UrgencyChoices.HIGH,
            description="থ্যালাসেমিয়ায় আক্রান্ত নিয়মিত রক্তগ্রহীতা শিশুর জন্য ১ ব্যাগ ফ্রেশ A+ রক্তের প্রয়োজন।",
            status="open",
            **loc_dhanmondi
        )

        # Medicine Need Posts
        MedicineNeedPost.objects.all().delete()
        MedicineNeedPost.objects.create(
            user=created_regular_users[3],
            medicine_name="Inj. Human Albumin 20% (100ml)",
            quantity="2 Vials",
            description="লিভার সিরোসিস রোগীর জরুরি প্রেসক্রিপশন। আশপাশের ফার্মেসিতে স্টক পাওয়া যাচ্ছে না। কারও কাছে স্টক তথ্য থাকলে জানান।",
            contact_number="01611000004",
            urgency=UrgencyChoices.HIGH,
            status="open",
            address="South Khulshi, Chittagong",
            **loc_dhanmondi
        )

        # Equipment Posts
        EquipmentSellPost.objects.all().delete()
        EquipmentSellPost.objects.create(
            user=created_regular_users[0],
            equipment_name="Foldable Wheelchair (Chrome Steel)",
            quantity="1",
            price=Decimal("4500.00"),
            condition="good",
            description="প্যারালাইসিস রোগীর জন্য কেনা হয়েছিল। সম্পূর্ণ ভালো এবং সচল অবস্থায় আছে।",
            contact_number="01711000001",
            status="open",
            address="Dhanmondi 4, Dhaka",
            **loc_dhanmondi
        )
        EquipmentNeedPost.objects.all().delete()
        EquipmentNeedPost.objects.create(
            user=created_regular_users[1],
            equipment_name="Portable Oxygen Concentrator (5L/min)",
            quantity="1",
            condition="good",
            urgency=UrgencyChoices.HIGH,
            description="শ্বাসকষ্টের বয়োবৃদ্ধ রোগীর জন্য ১ সপ্তাহের জন্য ভাড়ায় বা স্বল্পমূল্যে কনসেনট্রেটর প্রয়োজন।",
            contact_number="01811000002",
            status="open",
            address="Mirpur-2, Dhaka",
            **loc_dhanmondi
        )

        # General Posts
        GeneralPost.objects.all().delete()
        GeneralPost.objects.create(
            user=created_regular_users[0],
            title="ডেঙ্গু পরবর্তী চরম দুর্বলতা দূর করার প্রাকৃতিক উপায়",
            content="ডেঙ্গু থেকে সুস্থ হওয়ার পর প্রায় ২-৩ সপ্তাহ হাত-পায়ে প্রচণ্ড ব্যথা ও ক্লান্তি থাকে। ডাবের পানি, বেদানা, স্যুপ এবং পর্যাপ্ত প্রোটিন খাদ্যতালিকা এই ক্লান্তি কাটিয়ে উঠতে দারুণ সাহায্য করেছে।",
            contact_number="01711000001",
            status="open",
            **loc_dhanmondi
        )

        # 11. Sponsor Banners (Standard active slots; Interstitial Popup set to INACTIVE)
        self.stdout.write("🖼️ Generating & Seeding Sponsor Banners (Deactivating Forced Popup)...")
        banners_dir = os.path.join(settings.MEDIA_ROOT, "sponsors", "banners")
        os.makedirs(banners_dir, exist_ok=True)

        banners_config = [
            {
                "slot": "home_hero",
                "sponsor_name": "Square Hospital Executive Wellness",
                "title": "Comprehensive Executive Health & Cardiac Checkup 2026",
                "target_url": "/diagnostics",
                "monthly_fee_bdt": 45000,
                "contact_person": "Kazi M. Rahman",
                "contact_phone": "01720000001",
                "filename": "square_wellness_hero.jpg",
                "w": 1200, "h": 400,
                "bg1": (15, 76, 129), "bg2": (30, 144, 255),
                "brand": "Square Hospitals Ltd.",
                "headline": "Executive Health & Preventive Cardiac Packages",
                "subtext": "Early detection saves lives. 30% Privilege discount this month.",
                "badge": "★ Accredited Healthcare",
                "cta": "Book Health Checkup →",
                "is_active": True
            },
            {
                "slot": "home_middle",
                "sponsor_name": "Popular Diagnostic Centre",
                "title": "20% Privilege Discount on All Diagnostic & Radiology Tests",
                "target_url": "/diagnostics",
                "monthly_fee_bdt": 30000,
                "contact_person": "Kamrul Islam",
                "contact_phone": "01720000002",
                "filename": "popular_lab_middle.jpg",
                "w": 970, "h": 250,
                "bg1": (6, 78, 59), "bg2": (16, 185, 129),
                "brand": "Popular Diagnostic Centre",
                "headline": "Fast Digital Reports with Specialist Validation",
                "subtext": "Accurate pathology, 1.5T MRI, 128 Slice CT Scan across 30 branches.",
                "badge": "Trusted Diagnosis",
                "cta": "View Test Menu →",
                "is_active": True
            },
            {
                "slot": "sidebar",
                "sponsor_name": "Labaid Cardiac Hospital",
                "title": "24/7 Rapid Chest Pain Clinic & Emergency Hotline 10606",
                "target_url": "/doctors",
                "monthly_fee_bdt": 20000,
                "contact_person": "Tanvir Chowdhury",
                "contact_phone": "01720000003",
                "filename": "labaid_cardiac_sidebar.jpg",
                "w": 320, "h": 500,
                "bg1": (127, 29, 29), "bg2": (220, 38, 38),
                "brand": "Labaid Cardiac Care",
                "headline": "Emergency Chest Pain Unit",
                "subtext": "Dedicated Cathlab, Emergency Angiogram & ICU within 15 minutes.",
                "badge": "24/7 Hotline 10606",
                "cta": "Consult Cardiologist →",
                "is_active": True
            },
            {
                "slot": "medicine_page",
                "sponsor_name": "Green Life Model Pharmacy",
                "title": "Genuine Prescription Medicines with Express Home Delivery",
                "target_url": "/pharmacy",
                "monthly_fee_bdt": 22000,
                "contact_person": "Shahidul Alam",
                "contact_phone": "01720000004",
                "filename": "greenlife_pharma_med.jpg",
                "w": 850, "h": 220,
                "bg1": (20, 83, 45), "bg2": (34, 197, 94),
                "brand": "Green Life Model Pharmacy",
                "headline": "100% DGDA Certified Genuine Medicines",
                "subtext": "Temperature-controlled storage and safe doorstep delivery across Dhaka.",
                "badge": "10% Flat Discount",
                "cta": "Order Medicines →",
                "is_active": True
            },
            {
                "slot": "feed_inline",
                "sponsor_name": "Ibn Sina Diagnostic Centre",
                "title": "Advanced 3 Tesla MRI & High-Resolution Ultrasonography",
                "target_url": "/diagnostics",
                "monthly_fee_bdt": 25000,
                "contact_person": "Mahbubur Rahman",
                "contact_phone": "01720000005",
                "filename": "ibnsina_imaging_feed.jpg",
                "w": 650, "h": 360,
                "bg1": (19, 78, 74), "bg2": (13, 148, 136),
                "brand": "Ibn Sina Diagnostics",
                "headline": "Modern 3 Tesla MRI & High-Res USG",
                "subtext": "Reliable clinical imaging reviewed by senior radiologist professors.",
                "badge": "Precision Imaging",
                "cta": "Explore Services →",
                "is_active": True
            },
            {
                "slot": "interstitial_popup",
                "sponsor_name": "Evercare Hospital Emergency & Trauma Response",
                "title": "24/7 Emergency Ambulance & Critical ICU Response — Hotline 10678",
                "target_url": "/ambulances",
                "monthly_fee_bdt": 35000,
                "contact_person": "Ashfaqur Rahman",
                "contact_phone": "01720000006",
                "filename": "evercare_welcome_popup.jpg",
                "w": 900, "h": 500,
                "bg1": (15, 23, 42), "bg2": (225, 29, 72),
                "brand": "Evercare Hospital Dhaka",
                "headline": "24/7 Rapid Emergency & Critical Care",
                "subtext": "Immediate ICU, Cardiac Trauma units & Emergency Teleconsultation.",
                "badge": "★ Official Healthcare Partner",
                "cta": "Emergency Help →",
                "is_active": False  # DEACTIVATED per user request (keeps site clean & AdSense compliant)
            }
        ]

        SponsorBanner.objects.all().delete()
        for b_data in banners_config:
            rel_file = f"sponsors/banners/{b_data['filename']}"
            abs_file = os.path.join(settings.MEDIA_ROOT, rel_file)
            make_banner_graphic(
                abs_file, b_data["w"], b_data["h"],
                b_data["bg1"], b_data["bg2"],
                b_data["brand"], b_data["headline"], b_data["subtext"],
                b_data["badge"], b_data["cta"]
            )
            SponsorBanner.objects.create(
                sponsor_name=b_data["sponsor_name"],
                slot=b_data["slot"],
                title=b_data["title"],
                media_type="image",
                skip_delay_seconds=10,
                banner_image=rel_file,
                target_url=b_data["target_url"],
                start_date=today,
                end_date=today + timedelta(days=90),
                is_active=b_data["is_active"],
                monthly_fee_bdt=b_data["monthly_fee_bdt"],
                contact_person=b_data["contact_person"],
                contact_phone=b_data["contact_phone"],
                impressions_count=1240,
                clicks_count=78,
            )

        # 12. Assign Profile and Background Cover Photos
        self.stdout.write("🎨 Populating Profile DPs and Background Cover Photos for all entities...")
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("pop_photos", os.path.join(settings.BASE_DIR, "populate_photos_and_covers.py"))
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Photo populator notification: {e}"))

        # 13. Generate Credentials Reference File
        self.stdout.write("📝 Generating CREDENTIALS.md for deployment and admin handoff...")
        cred_text = f"""# 🏥 MediHub Deployment Credentials & Accounts Directory

This document contains all system administrator and demo user account credentials created during the root database seed.

---

## 🔑 1. System Administrator (Superuser)
Full administrative control over all portals, doctors, donors, pharmacies, diagnostics, ambulances, banners, and blogs.

| Role | Email | Password | Django Admin URL |
| :--- | :--- | :--- | :--- |
| **Super Admin** | `admin@medihub.com` | `Admin@12345` | [http://localhost:8000/admin/](http://localhost:8000/admin/) |

---

## 🩺 2. Verified Doctors (Top 20 Specialists)
All doctor accounts have verified BMDC registration, attached hospitals, schedules, consultation fees, and authentic ratings.

| Doctor Name | Email | Password | Specialization | BMDC Number | Consultation Fee |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Dr. Anisur Rahman** | `dr.anisur@medihub.com` | `Doctor@1234` | Cardiology | BMDC-A-10201 | ৳1,500 |
| **Dr. Farzana Yasmin** | `dr.farzana@medihub.com` | `Doctor@1234` | Gynecology & Obstetrics | BMDC-A-10202 | ৳1,200 |
| **Dr. Tariqul Islam** | `dr.tariqul@medihub.com` | `Doctor@1234` | Neurology | BMDC-A-10203 | ৳1,500 |
| **Dr. Mahmudul Hasan** | `dr.mahmudul@medihub.com` | `Doctor@1234` | Pediatrics | BMDC-A-10204 | ৳1,200 |
| **Dr. Sabrina Chowdhury** | `dr.sabrina@medihub.com` | `Doctor@1234` | Endocrinology | BMDC-A-10205 | ৳1,300 |
| **Dr. Kamrul Ahsan** | `dr.kamrul@medihub.com` | `Doctor@1234` | Orthopedics | BMDC-A-10206 | ৳1,500 |
| **Dr. Nusrat Jahan** | `dr.nusrat@medihub.com` | `Doctor@1234` | Dermatology | BMDC-A-10207 | ৳1,200 |
| **Dr. Shamsul Alam** | `dr.shamsul@medihub.com` | `Doctor@1234` | Gastroenterology | BMDC-A-10208 | ৳1,400 |
| **Dr. Afsana Karim** | `dr.afsana@medihub.com` | `Doctor@1234` | Ophthalmology | BMDC-A-10209 | ৳1,000 |
| **Dr. Rezaul Karim** | `dr.rezaul@medihub.com` | `Doctor@1234` | Nephrology | BMDC-A-10210 | ৳1,400 |
| **Dr. Tahmina Begum** | `dr.tahmina@medihub.com` | `Doctor@1234` | Psychiatry | BMDC-A-10211 | ৳1,200 |
| **Dr. Moniruzzaman Khan** | `dr.moniruzzaman@medihub.com` | `Doctor@1234` | ENT | BMDC-A-10212 | ৳1,100 |
| **Dr. Sharmin Akter** | `dr.sharmin@medihub.com` | `Doctor@1234` | General Surgery | BMDC-A-10213 | ৳1,200 |
| **Dr. Asif Iqbal** | `dr.asif@medihub.com` | `Doctor@1234` | General Medicine | BMDC-A-10214 | ৳1,400 |
| **Dr. Nazmul Huda** | `dr.nazmul@medihub.com` | `Doctor@1234` | Oncology | BMDC-A-10215 | ৳1,600 |
| **Dr. Rashedul Islam** | `dr.rashedul@medihub.com` | `Doctor@1234` | Urology | BMDC-A-10216 | ৳1,400 |
| **Dr. Kaniz Fatema** | `dr.kaniz@medihub.com` | `Doctor@1234` | Pediatrics | BMDC-A-10217 | ৳1,400 |
| **Dr. Shahinur Rahman** | `dr.shahinur@medihub.com` | `Doctor@1234` | Cardiology | BMDC-A-10218 | ৳1,600 |
| **Dr. Mehedi Hasan** | `dr.mehedi@medihub.com` | `Doctor@1234` | Orthopedics / Rehab | BMDC-A-10219 | ৳1,000 |
| **Dr. Nilufar Yasmin** | `dr.nilufar@medihub.com` | `Doctor@1234` | Gynecology | BMDC-A-10220 | ৳1,500 |

---

## 🩸 3. Blood Donors Directory (24 Donors covering all 8 Blood Groups)
Password for all blood donor profiles: `Donor@1234`

| Donor Name | Email | Blood Group | Location | Status | Lives Saved |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Arifur Rahman** | `donor.arif@medihub.com` | `A+` | Dhanmondi, Dhaka | Available | 12 |
| **Sumon Chowdhury** | `donor.sumon@medihub.com` | `A+` | Mirpur, Dhaka | Available | 8 |
| **Fariha Tasnim** | `donor.fariha@medihub.com` | `A+` | Uttara, Dhaka | Available | 5 |
| **Al-Mamun Sheikh** | `donor.mamun@medihub.com` | `A+` | Rajshahi | Available | 14 |
| **Shihab Uddin** | `donor.shihab@medihub.com` | `A-` | Gulshan, Dhaka | Available | 6 |
| **Nabil Ahmed** | `donor.nabil@medihub.com` | `A-` | Chittagong | Available | 4 |
| **Tanmoy Sarker** | `donor.tanmoy@medihub.com` | `B+` | Dhanmondi, Dhaka | Available | 15 |
| **Roksana Begum** | `donor.roksana@medihub.com` | `B+` | Mirpur, Dhaka | Available | 7 |
| **Enamul Haque** | `donor.enamul@medihub.com` | `B+` | Sylhet | Available | 9 |
| **Zahir Raihan** | `donor.zahir@medihub.com` | `B+` | Chittagong | Available | 11 |
| **Moumita Paul** | `donor.moumita@medihub.com` | `B-` | Uttara, Dhaka | Available | 4 |
| **Saiful Islam** | `donor.saiful@medihub.com` | `B-` | Rajshahi | Available | 8 |
| **Rubel Hossain** | `donor.rubel@medihub.com` | `O+` | Dhanmondi, Dhaka | Available | 18 |
| **Anika Tabassum** | `donor.anika@medihub.com` | `O+` | Mirpur, Dhaka | Available | 6 |
| **Shakil Khan** | `donor.shakil@medihub.com` | `O+` | Chittagong | Available | 10 |
| **Jasim Uddin** | `donor.jasim@medihub.com` | `O+` | Sylhet | Available | 12 |
| **Faruk Ahmed** | `donor.faruk@medihub.com` | `O-` | Gulshan, Dhaka | Available | 9 |
| **Mehnaz Chowdhury** | `donor.mehnaz@medihub.com` | `O-` | Dhanmondi, Dhaka | Available | 7 |
| **Hasan Mahmud** | `donor.hasan@medihub.com` | `AB+` | Uttara, Dhaka | Available | 11 |
| **Tania Sultana** | `donor.tania@medihub.com` | `AB+` | Chittagong | Available | 5 |
| **Babul Akter** | `donor.babul@medihub.com` | `AB+` | Rajshahi | Available | 8 |
| **Ashraf Ali** | `donor.ashraf@medihub.com` | `AB-` | Mirpur, Dhaka | Available | 4 |
| **Salma Khatun** | `donor.salma@medihub.com` | `AB-` | Dhanmondi, Dhaka | Available | 6 |
| **Kamal Hossain** | `donor.kamal@medihub.com` | `AB-` | Sylhet | Available | 5 |

---

## 💊 4. Pharmacies Directory (8 Reputable Pharmacies)
Password for all pharmacy profiles: `Pharmacy@1234`

| Pharmacy Name | Login Email | Contact Phone | Address |
| :--- | :--- | :--- | :--- |
| **Labaid Model Pharmacy** | `pharmacy.labaid@medihub.com` | `01740000001` | House 1, Road 4, Dhanmondi, Dhaka |
| **Tamanna Pharmacy** | `pharmacy.tamanna@medihub.com` | `01740000002` | Plot 14, Block B, Mirpur-10, Dhaka |
| **Green Life Pharmacy** | `pharmacy.greenlife@medihub.com` | `01740000003` | 32 Green Road, Dhanmondi, Dhaka |
| **Al-Madina Model Pharmacy** | `pharmacy.almadina@medihub.com` | `01740000004` | House 18, Sector 7, Uttara, Dhaka |
| **Square Hospital Pharmacy** | `pharmacy.square@medihub.com` | `01740000005` | Panthapath, Dhaka |
| **Popular Pharmacy** | `pharmacy.popular@medihub.com` | `01740000006` | Road 2, Dhanmondi, Dhaka |
| **Chittagong Central Pharma** | `pharmacy.ctgcentral@medihub.com` | `01740000007` | GEC Circle, Chittagong |
| **Sylhet Health Pharmacy** | `pharmacy.sylhet@medihub.com` | `01740000008` | Zindabazar, Sylhet |

---

## 🔬 5. Diagnostic Centers (8 Diagnostic Centers & 20 Standard Tests)
Password for all diagnostic profiles: `Diagnostic@1234`

| Diagnostic Center Name | Login Email | Contact Phone | Key Specialization |
| :--- | :--- | :--- | :--- |
| **Popular Diagnostic Centre** | `diagnostic.popular@medihub.com` | `01750000001` | Pathology, 1.5T MRI, 128-Slice CT |
| **Ibn Sina Diagnostic Centre** | `diagnostic.ibnsina@medihub.com` | `01750000002` | 3T MRI, High-Res USG, Digital X-Ray |
| **Square Hospital Lab** | `diagnostic.square@medihub.com` | `01750000003` | Clinical Biochemistry, Echo, Doppler |
| **Praava Health Diagnostics** | `diagnostic.praava@medihub.com` | `01750000004` | Molecular Biology, Fast Home Sample |
| **Labaid Diagnostic Centre** | `diagnostic.labaid@medihub.com` | `01750000005` | Cardiac Imaging, Mammography |
| **Medinova Medical Services** | `diagnostic.medinova@medihub.com` | `01750000006` | Hormonal Assays, Histopathology |
| **Chevron Clinical Laboratory** | `diagnostic.chevron@medihub.com` | `01750000007` | Comprehensive Pathology (Chittagong) |
| **Al-Haramain Diagnostics** | `diagnostic.alharamain@medihub.com` | `01750000008` | Automated Hematology (Sylhet) |

---

## 🚑 6. Emergency Ambulances (8 Ambulances)
Password for all ambulance profiles: `Ambulance@1234`

| Ambulance Service | Type | Login Email | Hotline Phone | Standby Base |
| :--- | :--- | :--- | :--- | :--- |
| **Evercare ICU Mobile Hospital** | ICU (Ventilator) | `ambulance.dhaka.icu@medihub.com` | `01760000001` | Dhanmondi, Dhaka |
| **National Heart Foundation** | Cardiac Ambulance | `ambulance.heart.cardiac@medihub.com` | `01760000002` | Mirpur, Dhaka |
| **Dhaka Emergency AC Ambulance** | AC Ambulance | `ambulance.dhaka.ac1@medihub.com` | `01760000003` | Green Road, Dhaka |
| **Uttara Fast Response** | AC Ambulance | `ambulance.uttara.ac2@medihub.com` | `01760000004` | Uttara, Dhaka |
| **BSMMU Neonatal Mobile Unit** | Neonatal (NICU) | `ambulance.bssmu.nicu@medihub.com` | `01760000005` | Shahbagh, Dhaka |
| **Central Al-Markazul Freezing** | Freezing / Mortuary | `ambulance.freeze@medihub.com` | `01760000006` | Mohammadpur, Dhaka |
| **Chittagong Highway Emergency** | Advanced Cardiac | `ambulance.ctg.express@medihub.com` | `01760000007` | Agrabad, Chittagong |
| **Sylhet Metro 24/7 Service** | AC Ambulance | `ambulance.sylhet.247@medihub.com` | `01760000008` | Subid Bazar, Sylhet |

---

## 👤 7. Regular Test Patients
Password for all patient profiles: `User@1234`

| Patient Name | Email | Gender | Contact Phone | Address |
| :--- | :--- | :--- | :--- | :--- |
| **Rahim Uddin** | `user.rahim@medihub.com` | Male | `01711000001` | Dhanmondi, Dhaka |
| **Nasrin Akter** | `user.nasrin@medihub.com` | Female | `01811000002` | Mirpur-2, Dhaka |
| **Tanvir Hasan** | `user.tanvir@medihub.com` | Male | `01911000003` | Uttara, Dhaka |
| **Sadia Jahan** | `user.sadia@medihub.com` | Female | `01611000004` | Khulshi, Chittagong |
| **Karim Chowdhury** | `user.karim@medihub.com` | Male | `01511000005` | Zindabazar, Sylhet |

---

## 🎯 8. Sponsor Banners & AdSense Compliance Status
- `home_hero`: Active (Square Hospitals)
- `home_middle`: Active (Popular Diagnostic)
- `sidebar`: Active (Labaid Cardiac)
- `medicine_page`: Active (Green Life Pharmacy)
- `feed_inline`: Active (Ibn Sina Diagnostics)
- **`interstitial_popup`**: **DEACTIVATED (`is_active=False`)** — Ensures Google AdSense compliance with no blocking countdown popups.
"""
        cred_path1 = os.path.join(settings.BASE_DIR, "CREDENTIALS.md")
        with open(cred_path1, "w", encoding="utf-8") as f:
            f.write(cred_text)

        cred_path2 = os.path.join(os.path.dirname(settings.BASE_DIR), "Medihub_web", "CREDENTIALS.md")
        try:
            with open(cred_path2, "w", encoding="utf-8") as f:
                f.write(cred_text)
        except Exception:
            pass

        self.stdout.write(self.style.SUCCESS("══════════════════════════════════════════════════════════════════"))
        self.stdout.write(self.style.SUCCESS(f"🎉 ROOT SEED COMPLETED SUCCESSFULLY!"))
        self.stdout.write(self.style.SUCCESS(f"   • Doctors seeded: {len(created_doctors)}"))
        self.stdout.write(self.style.SUCCESS(f"   • Donors seeded: {len(created_donors)}"))
        self.stdout.write(self.style.SUCCESS(f"   • Pharmacies seeded: {len(created_pharmacies)}"))
        self.stdout.write(self.style.SUCCESS(f"   • Diagnostics seeded: {len(created_diagnostics)}"))
        self.stdout.write(self.style.SUCCESS(f"   • Ambulances seeded: {len(ambulances_data)}"))
        self.stdout.write(self.style.SUCCESS(f"   • High-quality Medical Blogs: {len(created_blogs)}"))
        self.stdout.write(self.style.SUCCESS(f"   • Credentials saved to CREDENTIALS.md"))
        self.stdout.write(self.style.SUCCESS("══════════════════════════════════════════════════════════════════"))
