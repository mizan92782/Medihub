"""Compare serializer output keys against what the frontend's map* functions read."""
import json

from profiles.models import Doctor, BloodDonor, AmbulanceProfile, DiagnosticTest
from profiles.serializers import (
    DoctorProfileSerializer, BloodDonorProfileSerializer,
    AmbulanceProfileSerializer, DiagnosticTestSerializer,
)

FRONTEND_READS = {
    "DOCTOR": [
        "id", "first_name", "last_name", "profile_dp", "specialization_detail",
        "qualifications_detail", "years_of_experience", "evaluation",
        "hospitals_detail", "consultation_fee", "schedules",
        "address", "upozila_name", "district_name", "division_name",
    ],
    "DONOR": [
        "id", "first_name", "last_name", "blood_group", "address",
        "upozila_name", "district_name", "division_name", "last_donated",
        "availability", "contact_number", "lives_saved_count",
    ],
    "AMBULANCE": [
        "id", "owner_name", "contact_number", "ambulance_type", "vehicle_number",
        "is_available", "address", "upozila_name", "district_name", "division_name",
    ],
    "TEST": [
        "id", "test_name", "diagnostic_name", "contact_number", "price",
        "discount_price", "turnaround_time", "category",
    ],
}

CASES = [
    ("DOCTOR", DoctorProfileSerializer, Doctor.objects.first()),
    ("DONOR", BloodDonorProfileSerializer, BloodDonor.objects.first()),
    ("AMBULANCE", AmbulanceProfileSerializer, AmbulanceProfile.objects.first()),
    ("TEST", DiagnosticTestSerializer, DiagnosticTest.objects.first()),
]

for label, ser, obj in CASES:
    print(f"\n===== {label} =====")
    if obj is None:
        print("  !! no rows")
        continue
    data = ser(obj).data
    keys = set(data.keys())
    print("  serializer keys:", sorted(keys))
    for want in FRONTEND_READS[label]:
        if want in keys:
            val = data[want]
            preview = json.dumps(val, default=str)
            if len(preview) > 70:
                preview = preview[:70] + "…"
            state = "OK  " if val not in (None, "", [], 0) else "EMPTY"
            print(f"   {state} {want:<24} = {preview}")
        else:
            print(f"   MISSING {want}")
