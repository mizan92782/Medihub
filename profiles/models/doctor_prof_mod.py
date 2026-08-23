from django.db import models
from django.conf import settings
from location.models import District, Division, Union, Upozila
from core.enum import GenderChoices, DayChoices


class Specialization(models.Model):
    name_eng = models.CharField(max_length=200, unique=True)
    name_bn = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name_eng


class SubSpecialization(models.Model):
    specialization = models.ForeignKey(Specialization, on_delete=models.CASCADE, related_name='sub_specializations')
    name_eng = models.CharField(max_length=200, unique=True)
    name_bn = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name_eng


class Qualification(models.Model):
    name_eng = models.CharField(max_length=200, unique=True)
    name_bn = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name_eng


class Hospital(models.Model):
    name_eng = models.CharField(max_length=200, unique=True)
    name_bn = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name_eng


class Doctor(models.Model):

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='doctor')
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GenderChoices.choices)
    profile_dp = models.ImageField(upload_to='doctor/dp/', blank=True, null=True)
    contact_number = models.CharField(max_length=15)

    division = models.ForeignKey(Division, on_delete=models.SET_NULL, null=True)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True)
    upozila = models.ForeignKey(Upozila, on_delete=models.SET_NULL, null=True)
    union = models.ForeignKey(Union, on_delete=models.SET_NULL, null=True)
    
    specialization = models.ForeignKey(Specialization, on_delete=models.SET_NULL, null=True)
    sub_specialization = models.ForeignKey(SubSpecialization, on_delete=models.SET_NULL, null=True, blank=True)
    qualifications = models.ManyToManyField(Qualification, related_name='doctors', blank=True)
    hospital_affiliations = models.ManyToManyField(Hospital, related_name='doctors', blank=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    license_number = models.CharField(max_length=100, unique=True)
    license_validity = models.DateField()

    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    address = models.TextField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'Dr. {self.first_name} {self.last_name}'


class DoctorDetails(models.Model):
    doctor = models.OneToOneField(Doctor, on_delete=models.CASCADE, related_name='details')
    website = models.URLField(blank=True, null=True)
    social_link = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    language = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f'{self.doctor} - Details'


class DoctorEducation(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='educations')
    institution = models.CharField(max_length=200)
    degree = models.CharField(max_length=200)
    start_at = models.DateField()
    end_at = models.DateField(blank=True, null=True)
    place = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='doctor/education/', blank=True, null=True)

    def __str__(self):
        return f'{self.doctor} - {self.degree}'


class DoctorWorkingExperience(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='experiences')
    institution = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    starting_at = models.DateField()
    end_at = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.doctor} - {self.position}'


class PracticeLocation(models.Model):
    class LocationType(models.TextChoices):
        HOSPITAL = "hospital", "Hospital"
        CLINIC = "clinic", "Clinic"
        DIAGNOSTIC_CENTER = "diagnostic_center", "Diagnostic Center"
        CHAMBER = "chamber", "Chamber"
        OTHER = "other", "Other"

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="practice_locations")
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=30, choices=LocationType.choices, default=LocationType.HOSPITAL)
    address = models.CharField(max_length=300, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"


class ScheduleInstanceStatus(models.TextChoices):
    OPEN = "open", "Open"
    PAUSED = "paused", "Paused"
    CANCELLED = "cancelled", "Cancelled"
    COMPLETED = "completed", "Completed"


class DoctorScheduling(models.Model):

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='schedules')
    day = models.CharField(max_length=10, choices=DayChoices.choices)
    start = models.TimeField()
    end = models.TimeField()
    hospital = models.ForeignKey(Hospital, on_delete=models.SET_NULL, null=True, blank=True, related_name='schedules')
    practice_location = models.ForeignKey(PracticeLocation, on_delete=models.CASCADE, null=True, blank=True, related_name='schedules')
    max_patients = models.PositiveIntegerField(default=30)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateField(blank=True, null=True)
    valid_until = models.DateField(blank=True, null=True)

    def __str__(self):
        return f'{self.doctor} - {self.day} ({self.start}-{self.end}) at {self.hospital.name_eng if self.hospital else "N/A"}'


class DoctorDateSlot(models.Model):
    schedule = models.ForeignKey(DoctorScheduling, on_delete=models.CASCADE, related_name='date_slots')
    date = models.DateField()
    is_approved = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=ScheduleInstanceStatus.choices, default=ScheduleInstanceStatus.OPEN)
    max_patients = models.PositiveIntegerField(default=30)
    bookings_count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('schedule', 'date')

    def __str__(self):
        return f'{self.schedule.doctor} on {self.date} ({self.schedule.start}-{self.schedule.end})'


class DoctorRating(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='given_ratings')
    rating = models.PositiveSmallIntegerField(default=1)
    review = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('doctor', 'user')

    def __str__(self):
        return f'{self.doctor} - {self.rating} stars'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_doctor_stats()

    def update_doctor_stats(self):
        from django.db.models import Avg, Count
        stats, _ = DoctorStats.objects.get_or_create(doctor=self.doctor)
        res = DoctorRating.objects.filter(doctor=self.doctor).aggregate(avg=Avg('rating'), count=Count('id'))
        stats.avg_rating = round(res['avg'] or 0, 2)
        stats.total_rating = res['count'] or 0
        stats.save()


class DoctorBookingStatusChoices(models.TextChoices):
    PENDING = 'pending', 'Pending'
    CONFIRMED = 'confirmed', 'Confirmed'
    COMPLETED = 'completed', 'Completed'
    CANCELLED = 'cancelled', 'Cancelled'
    CANCELLED_BY_DOCTOR = 'cancelled_by_doctor', 'Cancelled by Doctor'


class DoctorBooking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='doctor_bookings')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='bookings')
    schedule = models.ForeignKey(DoctorScheduling, on_delete=models.SET_NULL, null=True, blank=True)
    date_slot = models.ForeignKey(DoctorDateSlot, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    appointment_date = models.DateField()
    patient_name = models.CharField(max_length=200)
    contact_number = models.CharField(max_length=15)
    problem_description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=25, choices=DoctorBookingStatusChoices.choices, default=DoctorBookingStatusChoices.PENDING)
    practice_location = models.ForeignKey(PracticeLocation, on_delete=models.SET_NULL, null=True, blank=True, related_name="bookings")
    appointment_number = models.PositiveIntegerField(default=1)
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-appointment_date', '-created']

    def __str__(self):
        return f'Booking for {self.patient_name} with {self.doctor} on {self.appointment_date}'

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        from django.db import transaction

        if is_new and self.date_slot:
            # Check slot status
            if self.date_slot.status != "open":
                raise ValueError("Cannot book a paused or cancelled appointment date slot.")
            
            # Atomic capacity check and increment using transaction row-lock
            with transaction.atomic():
                locked_slot = DoctorDateSlot.objects.select_for_update().get(id=self.date_slot.id)
                if locked_slot.bookings_count >= locked_slot.max_patients:
                    raise ValueError("This slot is already fully booked.")
                
                locked_slot.bookings_count += 1
                locked_slot.save()
                
                self.date_slot.bookings_count = locked_slot.bookings_count
                self.appointment_number = locked_slot.bookings_count
            
            # Sync schedule, practice location and date
            self.schedule = self.date_slot.schedule
            self.appointment_date = self.date_slot.date
            if self.schedule:
                self.practice_location = self.schedule.practice_location

        # Handle capacity release when status transitions to cancelled
        if not is_new and self.pk and self.date_slot:
            orig = DoctorBooking.objects.get(pk=self.pk)
            target_cancelled = ["cancelled", "cancelled_by_doctor"]
            if self.status in target_cancelled and orig.status not in target_cancelled:
                with transaction.atomic():
                    locked_slot = DoctorDateSlot.objects.select_for_update().get(id=self.date_slot.id)
                    locked_slot.bookings_count = max(0, locked_slot.bookings_count - 1)
                    locked_slot.save()
                    self.date_slot.bookings_count = locked_slot.bookings_count

        super().save(*args, **kwargs)
        if is_new and hasattr(self.doctor, 'evaluation'):
            DoctorStats.objects.filter(doctor=self.doctor).update(total_booking=models.F('total_booking') + 1)


class DoctorStats(models.Model):
    doctor = models.OneToOneField(Doctor, on_delete=models.CASCADE, related_name='evaluation')
    avg_rating = models.FloatField(default=0)
    total_rating = models.IntegerField(default=0)
    total_profile_views = models.IntegerField(default=0)
    total_followers = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)
    total_feed_impression = models.IntegerField(default=0)
    total_feed_click = models.IntegerField(default=0)
    total_booking = models.IntegerField(default=0)
    feed_score = models.FloatField(default=0)
    is_online = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    last_active = models.DateTimeField(null=True, blank=True)
    profile_completed = models.BooleanField(default=False)
    search_score = models.FloatField(default=0)
    recommendation_score = models.FloatField(default=0)

    def __str__(self):
        return f'{self.doctor} - Evaluation'