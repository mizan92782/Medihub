from django.core.management.base import BaseCommand
from datetime import date
from authentication.models import User
from location.models import Division, District
from profiles.models import (
    Doctor, Specialization, Hospital, Qualification,
    BloodDonor, PharmacyProfile, PharmacyMedicine,
    DiagnosticProfile, DiagnosticTest, AmbulanceProfile
)
from blog.models import BlogPost

class Command(BaseCommand):
    help = 'Seed initial database records'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding initial Medihub data...")

        # Create Location
        dhaka_div, _ = Division.objects.get_or_create(
            division_id=1,
            defaults={"division_name_eng": "Dhaka", "division_name_bn": "ঢাকা"}
        )
        dhaka_dist, _ = District.objects.get_or_create(
            district_id=1,
            defaults={
                "division": dhaka_div,
                "district_name_eng": "Dhaka",
                "district_name_bn": "ঢাকা",
                "lattitude": 23.8103,
                "logitude": 90.4125
            }
        )

        # Create Specializations
        cardio, _ = Specialization.objects.get_or_create(name_eng="Cardiology", defaults={"name_bn": "কার্ডিওলজি"})
        pedia, _ = Specialization.objects.get_or_create(name_eng="Pediatrics", defaults={"name_bn": "শিশু রোগ"})
        neuro, _ = Specialization.objects.get_or_create(name_eng="Neurology", defaults={"name_bn": "নিউরোলেজি"})

        # Create Qualifications
        mbbs, _ = Qualification.objects.get_or_create(name_eng="MBBS", defaults={"name_bn": "এমবিবিএস"})
        fcps, _ = Qualification.objects.get_or_create(name_eng="FCPS (Cardiology)", defaults={"name_bn": "এফসিপিএস"})

        # Create Hospital
        dmc, _ = Hospital.objects.get_or_create(name_eng="Dhaka Medical College Hospital", defaults={"name_bn": "ঢাকা মেডিকেল কলেজ হাসপাতাল"})
        sqh, _ = Hospital.objects.get_or_create(name_eng="Square Hospital", defaults={"name_bn": "স্কয়ার হাসপাতাল"})

        # Seed Doctor User
        doc_user, _ = User.objects.get_or_create(
            email="anisur@medihub.com",
            defaults={"user_type": "doctor"}
        )
        if hasattr(doc_user, 'doctor'):
            doctor = doc_user.doctor
        else:
            doctor = Doctor.objects.create(
                user=doc_user,
                first_name="Anisur",
                last_name="Rahman",
                license_number="BMDC-A-48920",
                license_validity=date(2030, 12, 31),
                specialization=cardio,
                years_of_experience=12,
                contact_number="+8801711000111",
                division=dhaka_div,
                district=dhaka_dist,
                gender="male"
            )
            doctor.qualifications.add(mbbs, fcps)
            doctor.hospital_affiliations.add(sqh)

        # Seed Blood Donor User
        donor_user, _ = User.objects.get_or_create(
            email="donor1@medihub.com",
            defaults={"user_type": "blood_donor", "is_blood_donor": True}
        )
        if not hasattr(donor_user, 'blood_donor'):
            BloodDonor.objects.create(
                user=donor_user,
                first_name="Tanvir",
                last_name="Hassan",
                gender="male",
                date_of_birth=date(1995, 5, 15),
                blood_group="O+",
                contact_number="+8801819000222",
                availability="available",
                division=dhaka_div,
                district=dhaka_dist,
                lives_saved_count=8
            )

        # Seed Pharmacy User
        pharm_user, _ = User.objects.get_or_create(
            email="pharmacy@medihub.com",
            defaults={"user_type": "pharmacy"}
        )
        if not hasattr(pharm_user, 'pharmacy_profile'):
            pharm = PharmacyProfile.objects.create(
                user=pharm_user,
                pharmacy_name="Lazz Pharma (Dhanmondi Branch)",
                license_number="DL-1092-DHA",
                contact_number="+8801730000333",
                division=dhaka_div,
                district=dhaka_dist
            )
            PharmacyMedicine.objects.create(
                pharmacy=pharm,
                name="Napa Extra 500mg",
                generic_name="Paracetamol + Caffeine",
                brand_name="Beximco Pharmaceuticals",
                price=25.00,
                stock_quantity=500,
                description="Pain reliever and fever reducer"
            )

        # Seed Ambulance User
        amb_user, _ = User.objects.get_or_create(
            email="ambulance@medihub.com",
            defaults={"user_type": "ambulance"}
        )
        if not hasattr(amb_user, 'ambulance_profile'):
            AmbulanceProfile.objects.create(
                user=amb_user,
                owner_name="DMC Cardiac Ambulance Service",
                vehicle_number="DHAKA-CHA-11-4092",
                ambulance_type="icu",
                contact_number="+8801911000444",
                address="Dhaka Medical College Gate 2"
            )

        # Seed Diagnostic User
        diag_user, _ = User.objects.get_or_create(
            email="popular@medihub.com",
            defaults={"user_type": "diagnostic"}
        )
        if not hasattr(diag_user, 'diagnostic_profile'):
            diag = DiagnosticProfile.objects.create(
                user=diag_user,
                center_name="Popular Diagnostic Center",
                license_number="DIAG-8840",
                contact_number="+8801552000555",
                division=dhaka_div,
                district=dhaka_dist
            )
            DiagnosticTest.objects.create(
                diagnostic=diag,
                test_name="Echocardiogram (Color Doppler)",
                category="Cardiology",
                price=3000.00,
                discount_price=2500.00,
                preparation_instructions="No prior fasting required."
            )

        # Seed Blog Post
        BlogPost.objects.get_or_create(
            doctor=doctor,
            title="Recognizing Early Signs of Heart Attack & Emergency Steps",
            defaults={
                "content": "Heart disease remains the leading cause of sudden emergency hospital admissions in Bangladesh. Common symptoms include severe chest pressure, pain radiating to the left arm or jaw, shortness of breath, and cold sweats. Emergency first-aid steps: Keep the patient calm in a seated position, call 999 or Medihub emergency ambulance immediately, and if available, administer chewable aspirin.",
                "category": "Cardiology",
                "like_count": 48,
                "views": 320
            }
        )

        self.stdout.write(self.style.SUCCESS("Successfully seeded initial Medihub records!"))
