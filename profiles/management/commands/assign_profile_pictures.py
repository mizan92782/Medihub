import os
import urllib.request
from django.core.management.base import BaseCommand
from django.core.files import File
from profiles.models.doctor_prof_mod import Doctor
from profiles.models.user_prof_mod import RegularUserProfile


# Real Unsplash profile photos (direct CDN links, no auth needed)
DOCTOR_MALE_PHOTOS = [
    "https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=300&h=300&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1622253692010-333f2da6031d?w=300&h=300&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=300&h=300&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1537368910025-700350fe46c7?w=300&h=300&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1582750433449-648ed127bb54?w=300&h=300&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1651008376811-b90baee60c1f?w=300&h=300&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1638202993928-7267aad84c31?w=300&h=300&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1607990281513-2c110a25bd8c?w=300&h=300&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1594824813566-82823d5afe4a?w=300&h=300&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=300&h=300&fit=crop&crop=face",
]

DOCTOR_FEMALE_PHOTOS = [
    "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=300&h=300&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1594824813566-82823d5afe4a?w=300&h=300&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1527613426441-4da17471b66d?w=300&h=300&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1614608682850-e0d6ed316d47?w=300&h=300&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1643297654416-05795d62e39c?w=300&h=300&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1651008376811-b90baee60c1f?w=300&h=300&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=300&h=300&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1607990281513-2c110a25bd8c?w=300&h=300&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1638202993928-7267aad84c31?w=300&h=300&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1582750433449-648ed127bb54?w=300&h=300&fit=crop&crop=face",
]

USER_MALE_PHOTOS = [
    "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=300&h=300&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1570295999919-56ceb5ecca61?w=300&h=300&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=300&h=300&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=300&h=300&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=300&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=300&h=300&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=300&h=300&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1463453091185-61582044d556?w=300&h=300&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?w=300&h=300&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?w=300&h=300&fit=crop&crop=face",
]

USER_FEMALE_PHOTOS = [
    "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=300&h=300&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=300&h=300&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=300&h=300&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=300&h=300&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?w=300&h=300&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?w=300&h=300&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=300&h=300&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=300&h=300&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1502823403499-6ccfcf4fb453?w=300&h=300&fit=crop&crop=face",
    "https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?w=300&h=300&fit=crop&crop=face",
]


def download_photo(url, save_path):
    """Download photo from URL to local path, fallback to ui-avatars if fails."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8) as resp:
            with open(save_path, 'wb') as f:
                f.write(resp.read())
        return True
    except Exception:
        return False


def assign_avatar_fallback(name, gender, save_path):
    """Generate avatar using ui-avatars.com as fallback."""
    bg = "0284c7" if gender == "male" else "e11d48"
    encoded = urllib.parse.quote(name)
    url = f"https://ui-avatars.com/api/?name={encoded}&size=300&background={bg}&color=fff&bold=true"
    try:
        import urllib.parse
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8) as resp:
            with open(save_path, 'wb') as f:
                f.write(resp.read())
        return True
    except Exception:
        return False


class Command(BaseCommand):
    help = 'Download and assign profile pictures to doctors and users'

    def handle(self, *args, **kwargs):
        import urllib.parse

        # ── Doctors ──────────────────────────────────────────────
        doctors = Doctor.objects.filter(profile_dp='')
        self.stdout.write(f'Assigning photos to {doctors.count()} doctors...')
        ok = 0
        for i, doctor in enumerate(doctors):
            photos = DOCTOR_FEMALE_PHOTOS if doctor.gender == 'female' else DOCTOR_MALE_PHOTOS
            url = photos[i % len(photos)]
            filename = f"doctor_dp_{doctor.id}.jpg"
            save_path = f"/app/media/doctor/dp/{filename}"

            if download_photo(url, save_path):
                doctor.profile_dp = f"doctor/dp/{filename}"
                doctor.save(update_fields=['profile_dp'])
                ok += 1
            else:
                # fallback to ui-avatars
                name = f"{doctor.first_name}+{doctor.last_name}"
                bg = "0284c7"
                avatar_url = f"https://ui-avatars.com/api/?name={name}&size=300&background={bg}&color=fff&bold=true"
                if download_photo(avatar_url, save_path):
                    doctor.profile_dp = f"doctor/dp/{filename}"
                    doctor.save(update_fields=['profile_dp'])
                    ok += 1

        self.stdout.write(self.style.SUCCESS(f'✅ Doctors: {ok}/{doctors.count()} photos assigned'))

        # ── Regular Users ─────────────────────────────────────────
        users = RegularUserProfile.objects.filter(profile_dp='')
        self.stdout.write(f'Assigning photos to {users.count()} users...')
        ok = 0
        for i, profile in enumerate(users):
            photos = USER_FEMALE_PHOTOS if profile.gender == 'female' else USER_MALE_PHOTOS
            url = photos[i % len(photos)]
            filename = f"user_dp_{profile.id}.jpg"
            save_path = f"/app/media/user/dp/{filename}"

            if download_photo(url, save_path):
                profile.profile_dp = f"user/dp/{filename}"
                profile.save(update_fields=['profile_dp'])
                ok += 1
            else:
                name = f"{profile.first_name}+{profile.last_name}"
                bg = "0d9488"
                avatar_url = f"https://ui-avatars.com/api/?name={name}&size=300&background={bg}&color=fff&bold=true"
                if download_photo(avatar_url, save_path):
                    profile.profile_dp = f"user/dp/{filename}"
                    profile.save(update_fields=['profile_dp'])
                    ok += 1

        self.stdout.write(self.style.SUCCESS(f'✅ Users: {ok}/{users.count()} photos assigned'))
