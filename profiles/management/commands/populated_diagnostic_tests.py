from django.core.management.base import BaseCommand
from profiles.models.diagnostic_prof_mod import DiagnosticProfile, DiagnosticTest


TESTS = [
    ('Complete Blood Count (CBC)', 'General Health', 600, 480, 'Measures red/white blood cells and platelets.'),
    ('Lipid Profile Screen', 'Cardiology', 1200, 950, 'Checks cholesterol and triglyceride levels.'),
    ('HbA1c Diabetes Profile', 'Endocrinology', 900, 750, 'Measures average blood sugar over 3 months.'),
    ('Thyroid Function Test (TFT)', 'Endocrinology', 1100, 880, 'Checks T3, T4, TSH hormone levels.'),
    ('Liver Function Test (LFT)', 'Gastroenterology', 800, 640, 'Evaluates liver enzyme and protein levels.'),
    ('Kidney Function Test (KFT)', 'Nephrology', 850, 680, 'Checks creatinine, urea, and electrolytes.'),
    ('Chest X-Ray', 'Radiology', 500, 400, 'Imaging of lungs and chest cavity.'),
    ('ECG / EKG', 'Cardiology', 600, 480, 'Records electrical activity of the heart.'),
    ('Urine Routine Examination', 'General Health', 300, 240, 'Detects infections, kidney issues, diabetes.'),
    ('Blood Glucose Fasting', 'Endocrinology', 200, 160, 'Measures fasting blood sugar level.'),
    ('Dengue NS1 Antigen', 'Infectious Disease', 700, 560, 'Early detection of dengue fever.'),
    ('COVID-19 RT-PCR', 'Infectious Disease', 1500, 1200, 'Detects active COVID-19 infection.'),
]


class Command(BaseCommand):
    help = 'Populate diagnostic tests for existing diagnostic profiles'

    def handle(self, *args, **kwargs):
        if DiagnosticTest.objects.exists():
            self.stdout.write(self.style.SUCCESS('Diagnostic tests already populated'))
            return

        diagnostics = list(DiagnosticProfile.objects.all())
        if not diagnostics:
            self.stdout.write(self.style.ERROR('No diagnostic profiles found. Run populated_diagnostic first.'))
            return

        count = 0
        for i, (name, category, price, disc, desc) in enumerate(TESTS):
            diag = diagnostics[i % len(diagnostics)]
            DiagnosticTest.objects.create(
                diagnostic=diag,
                test_name=name,
                category=category,
                price=price,
                discount_price=disc,
                description=desc,
                is_available=True,
            )
            count += 1

        self.stdout.write(self.style.SUCCESS(f'✅ {count} diagnostic tests populated successfully'))
