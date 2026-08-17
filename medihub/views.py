from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsAdminUser
from core.api_response import APIResponse
from authentication.models import User
from profiles.models import (
    Doctor, RegularUserProfile, BloodDonor, AmbulanceProfile,
    PharmacyProfile, DiagnosticProfile, DoctorBooking
)
from post.models.blood_need_mod import BloodNeedPost
from post.models.medicine_need_mod import MedicineNeedPost
from post.models.equipment_need_mod import EquipmentNeedPost
from post.models.general_post_mod import GeneralPost
from blog.models import BlogPost


class AdminDashboardStatsView(APIView):
    """
    Admin Dashboard Stats API providing aggregate platform analytics.
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        stats = {
            'users': {
                'total': User.objects.count(),
                'doctors': Doctor.objects.count(),
                'regular': RegularUserProfile.objects.count(),
                'blood_donors': BloodDonor.objects.count(),
                'ambulances': AmbulanceProfile.objects.count(),
                'pharmacies': PharmacyProfile.objects.count(),
                'diagnostics': DiagnosticProfile.objects.count(),
            },
            'posts': {
                'blood_need': BloodNeedPost.objects.count(),
                'medicine_need': MedicineNeedPost.objects.count(),
                'equipment_need': EquipmentNeedPost.objects.count(),
                'general': GeneralPost.objects.count(),
                'total': BloodNeedPost.objects.count() + MedicineNeedPost.objects.count() + EquipmentNeedPost.objects.count() + GeneralPost.objects.count()
            },
            'blogs': {
                'total': BlogPost.objects.count(),
                'published': BlogPost.objects.filter(status='published').count(),
                'draft': BlogPost.objects.filter(status='draft').count(),
            },
            'bookings': {
                'total': DoctorBooking.objects.count(),
                'pending': DoctorBooking.objects.filter(status='pending').count(),
                'confirmed': DoctorBooking.objects.filter(status='confirmed').count(),
                'completed': DoctorBooking.objects.filter(status='completed').count(),
            }
        }
        return Response(APIResponse.success("Admin dashboard statistics retrieved successfully", "stats", stats))


def serve_dashboard(request):
    return render(request, 'dashboard.html')
