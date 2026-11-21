from django.core.management.base import BaseCommand
from authentication.models import User
from location.models import Division, District, Upozila
from post.models import (
    BloodNeedPost, MedicineNeedPost, EquipmentNeedPost,
    EquipmentSellPost, MedicinePost, GeneralPost, AmbulanceNeedPost
)


class Command(BaseCommand):
    help = 'Seed one sample post for every community post type'

    def handle(self, *args, **kwargs):
        user = User.objects.first()
        if not user:
            self.stdout.write(self.style.ERROR('No users found. Run seed_data first.'))
            return

        div = Division.objects.first()
        dist = District.objects.first()
        upz = Upozila.objects.first()

        if not div or not dist:
            self.stdout.write(self.style.ERROR('No location data found. Load location fixtures first.'))
            return

        loc = dict(division=div, district=dist, upozila=upz)

        # 1. Blood Need
        BloodNeedPost.objects.filter(patient_name='Rahim Uddin (Seed)').delete()
        BloodNeedPost.objects.create(
            user=user,
            patient_name='Rahim Uddin (Seed)',
            patient_age=45,
            patient_gender='male',
            blood_group='O+',
            bags_needed=2,
            hospital_name='Dhaka Medical College Hospital',
            hospital_address='Dhaka Medical College Road, Dhaka',
            needed_date='2025-08-10',
            needed_time='09:00:00',
            contact_number='01811000001',
            urgency='critical',
            description='Patient needs O+ blood urgently for surgery. Please contact ASAP.',
            status='open',
            **loc,
        )
        self.stdout.write('✅ BloodNeedPost seeded')

        # 2. Blood Donation (via profiles)
        try:
            from profiles.models.blood_donor_mod import BloodDonor, BloodDonationPost
            donor = BloodDonor.objects.filter(user=user).first()
            if donor:
                BloodDonationPost.objects.filter(donor=donor, medical_facility='Seed Hospital').delete()
                BloodDonationPost.objects.create(
                    donor=donor,
                    bags_donated=1,
                    medical_facility='Seed Hospital',
                    donation_date='2025-07-20',
                    donation_time='11:00:00',
                    patient_description='Donated blood for a road accident victim. Alhamdulillah, patient recovered.',
                    **loc,
                )
                self.stdout.write('✅ BloodDonationPost seeded')
            else:
                self.stdout.write('⚠️  No BloodDonor profile found, skipping BloodDonationPost')
        except Exception as e:
            self.stdout.write(f'⚠️  BloodDonationPost skipped: {e}')

        # 3. Ambulance Need
        AmbulanceNeedPost.objects.filter(address='Mirpur-10, Dhaka (Seed)').delete()
        AmbulanceNeedPost.objects.create(
            user=user,
            ambulance_type='icu',
            address='Mirpur-10, Dhaka (Seed)',
            contact_number='01811000003',
            needed_date='2025-08-11',
            needed_time='08:00:00',
            urgency='critical',
            description='ICU ambulance needed urgently for cardiac patient transfer to NICVD.',
            status='open',
            **loc,
        )
        self.stdout.write('✅ AmbulanceNeedPost seeded')

        # 4. Equipment Sell
        EquipmentSellPost.objects.filter(equipment_name='Oxygen Cylinder (Seed)').delete()
        EquipmentSellPost.objects.create(
            user=user,
            equipment_name='Oxygen Cylinder (Seed)',
            quantity='1',
            condition='good',
            price=3500,
            address='House 5, Road 3, Savar, Dhaka',
            contact_number='01811000004',
            description='Used oxygen cylinder in good condition. Patient has recovered. Comes with regulator.',
            status='open',
            **loc,
        )
        self.stdout.write('✅ EquipmentSellPost seeded')

        # 5. Equipment Need
        EquipmentNeedPost.objects.filter(equipment_name='Wheelchair (Seed)').delete()
        EquipmentNeedPost.objects.create(
            user=user,
            equipment_name='Wheelchair (Seed)',
            quantity='1',
            condition='good',
            address='House 12, Dhanmondi, Dhaka',
            contact_number='01811000005',
            urgency='medium',
            description='Need a wheelchair for elderly patient. Can rent or borrow.',
            status='open',
            **loc,
        )
        self.stdout.write('✅ EquipmentNeedPost seeded')

        # 6. Medicine (sell)
        MedicinePost.objects.filter(medicine_name='Insulin Glargine 100IU (Seed)').delete()
        MedicinePost.objects.create(
            user=user,
            listing_type='sell',
            medicine_name='Insulin Glargine 100IU (Seed)',
            quantity='3 vials',
            price=1200,
            address='House 12, Patiya, Chittagong',
            contact_number='01811000006',
            description='Unused insulin vials, bought extra. Expiry 2026. Selling at low price.',
            status='open',
            **loc,
        )
        self.stdout.write('✅ MedicinePost (sell) seeded')

        # 7. Medicine Need
        MedicineNeedPost.objects.filter(medicine_name='Warfarin 5mg (Seed)').delete()
        MedicineNeedPost.objects.create(
            user=user,
            medicine_name='Warfarin 5mg (Seed)',
            quantity='2 strips',
            address='House 9, Sylhet Sadar',
            contact_number='01811000007',
            urgency='critical',
            description='Heart patient urgently needs Warfarin. Not available in local pharmacy.',
            status='open',
            **loc,
        )
        self.stdout.write('✅ MedicineNeedPost seeded')

        # 8. General Post
        GeneralPost.objects.filter(title='Community Health Awareness (Seed)').delete()
        GeneralPost.objects.create(
            user=user,
            title='Community Health Awareness (Seed)',
            content='Please donate blood regularly. One donation can save up to 3 lives. Visit your nearest blood bank or contact Medihub to find donors near you.',
            contact_number='01811000008',
            status='open',
            **loc,
        )
        self.stdout.write('✅ GeneralPost seeded')

        self.stdout.write(self.style.SUCCESS('\n🎉 All 8 community post types seeded successfully!'))
