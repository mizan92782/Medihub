from django.core.management.base import BaseCommand
from authentication.models import User
from profiles.models import Doctor, Specialization, Qualification, Hospital
from blog.models import BlogPost
from core.enum import BlogStatusChoices, BlogCategoryChoices


DOCTOR_EMAIL = "dr.rafiq@medihub.com"
DOCTOR_PASSWORD = "Doctor@1234"


class Command(BaseCommand):
    help = 'Seed a doctor with blog posts'

    def handle(self, *args, **kwargs):
        spec, _ = Specialization.objects.get_or_create(
            name_eng="Cardiology",
            defaults={"name_bn": "কার্ডিওলজি"}
        )
        qual, _ = Qualification.objects.get_or_create(
            name_eng="MBBS",
            defaults={"name_bn": "এমবিবিএস"}
        )
        fcps, _ = Qualification.objects.get_or_create(
            name_eng="FCPS (Cardiology)",
            defaults={"name_bn": "এফসিপিএস (কার্ডিওলজি)"}
        )
        hospital, _ = Hospital.objects.get_or_create(
            name_eng="National Heart Foundation Hospital",
            defaults={"name_bn": "জাতীয় হৃদরোগ হাসপাতাল"}
        )

        user, created = User.objects.get_or_create(
            email=DOCTOR_EMAIL,
            defaults={"user_type": "doctor"}
        )
        if created:
            user.set_password(DOCTOR_PASSWORD)
            user.save()

        doctor, _ = Doctor.objects.get_or_create(
            user=user,
            defaults={
                "first_name": "Rafiqul",
                "last_name": "Islam",
                "gender": "male",
                "contact_number": "+8801711223344",
                "license_number": "BMDC-C-99201",
                "license_validity": "2030-12-31",
                "specialization": spec,
                "years_of_experience": 15,
                "consultation_fee": 800,
                "is_active": True,
                "is_available": True,
            }
        )
        doctor.qualifications.add(qual, fcps)
        doctor.hospital_affiliations.add(hospital)

        posts = [
            {
                "title": "Understanding Heart Disease: Prevention & Early Detection",
                "slug": "understanding-heart-disease-prevention-early-detection",
                "content": "Heart disease is the leading cause of death globally. Early detection through regular checkups, ECG, and echocardiography can save lives. Maintain a healthy diet, exercise regularly, avoid smoking, and manage stress to reduce your risk significantly.",
                "category": BlogCategoryChoices.CARDIOLOGY,
                "tags": "heart,cardiology,prevention",
                "status": BlogStatusChoices.PUBLISHED,
                "views": 540,
                "like_count": 92,
            },
            {
                "title": "High Blood Pressure: The Silent Killer",
                "slug": "high-blood-pressure-silent-killer",
                "content": "Hypertension often has no symptoms but can lead to stroke, heart attack, and kidney failure. Monitor your blood pressure regularly, reduce salt intake, stay active, and take prescribed medications consistently.",
                "category": BlogCategoryChoices.CARDIOLOGY,
                "tags": "hypertension,blood pressure,awareness",
                "status": BlogStatusChoices.PUBLISHED,
                "views": 310,
                "like_count": 65,
            },
            {
                "title": "When to See a Cardiologist",
                "slug": "when-to-see-a-cardiologist",
                "content": "Chest pain, shortness of breath, irregular heartbeat, or a family history of heart disease are all reasons to consult a cardiologist. Don't ignore warning signs — early intervention is key.",
                "category": BlogCategoryChoices.CARDIOLOGY,
                "tags": "cardiology,consultation,symptoms",
                "status": BlogStatusChoices.PUBLISHED,
                "views": 210,
                "like_count": 44,
            },
        ]

        for post_data in posts:
            BlogPost.objects.get_or_create(
                slug=post_data["slug"],
                defaults={**post_data, "doctor": doctor}
            )

        self.stdout.write(self.style.SUCCESS(
            f"\n✅ Doctor seeded successfully!\n"
            f"   Email    : {DOCTOR_EMAIL}\n"
            f"   Password : {DOCTOR_PASSWORD}\n"
            f"   Name     : Dr. Rafiqul Islam\n"
            f"   Blog Posts: {len(posts)} published\n"
        ))
