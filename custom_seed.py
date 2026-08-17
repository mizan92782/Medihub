import json
from django.conf import settings
from authentication.models import User
from post.models import BloodNeedPost, MedicineNeedPost, EquipmentNeedPost, GeneralPost
from blog.models import BlogPost
from blog.models.blog_media_mod import BlogMedia
from blog.models.blog_like_mod import BlogLike
from blog.models.blog_comment_mod import BlogComment
from profiles.models import Doctor
from location.models import Division, District, Upozila

def get_user_by_pattern(email):
    u = User.objects.filter(email=email).first()
    if u: return u
    prefix = email.split('@')[0]
    u = User.objects.filter(email__startswith=prefix).first()
    if u: return u
    role = 'dr' if prefix.startswith('dr') else 'donor' if prefix.startswith('donor') else 'diagnostic' if prefix.startswith('diagnostic') else 'pharmacy' if prefix.startswith('pharmacy') else 'ambulance' if prefix.startswith('ambulance') else 'user'
    u = User.objects.filter(email__startswith=role).first()
    return u or User.objects.first()

def get_doctor_by_user(user):
    doc = Doctor.objects.filter(user=user).first()
    if doc: return doc
    return Doctor.objects.first()

def get_location(item):
    return {
        'division': Division.objects.filter(division_name_bn=item['division']).first() or Division.objects.first(),
        'district': District.objects.filter(district_name_bn=item['district']).first() or District.objects.first(),
        'upozila': Upozila.objects.filter(upoila_name_bn=item.get('upozila')).first() or Upozila.objects.first(),
    }

# 1. Seed Blog Posts
blog_data = []
with open(settings.BASE_DIR / 'dataset' / 'blog_post.json', 'r', encoding='utf-8') as f:
    blog_data = json.load(f)

BlogPost.objects.all().delete()
for item in blog_data:
    user = get_user_by_pattern(item['doctor_email'])
    doctor = get_doctor_by_user(user)
    if not doctor: continue
    post = BlogPost.objects.create(
        doctor=doctor,
        title=item['title'],
        slug=item['slug'],
        content=item['content'],
        category=item['category'],
        tags=item.get('tags', ''),
        status=item['status'],
    )
    BlogMedia.objects.bulk_create([
        BlogMedia(
            post=post,
            media_type=media['media_type'],
            file=media['file'],
            caption=media.get('caption', ''),
            order=media.get('order', 0),
        ) for media in item.get('media', [])
    ])
    for like_email in item.get('likes', []):
        like_user = get_user_by_pattern(like_email)
        if like_user:
            BlogLike.add_like(post=post, user=like_user)
    for comment_data in item.get('comments', []):
        comment_user = get_user_by_pattern(comment_data['user'])
        if not comment_user: continue
        comment = BlogComment.add_comment(post=post, user=comment_user, content=comment_data['content'])
        for reply_data in comment_data.get('replies', []):
            reply_user = get_user_by_pattern(reply_data['user'])
            if reply_user:
                BlogComment.add_comment(post=post, user=reply_user, content=reply_data['content'], parent=comment)

print("Seeded BlogPosts:", BlogPost.objects.count())

# 2. Seed Posts (Blood Need)
blood_data = []
with open(settings.BASE_DIR / 'dataset' / 'blood_need_post.json', 'r', encoding='utf-8') as f:
    blood_data = json.load(f)

BloodNeedPost.objects.all().delete()
for item in blood_data:
    user = get_user_by_pattern(item['user'])
    if not user: continue
    loc = get_location(item)
    BloodNeedPost.objects.create(
        user=user,
        patient_name=item['patient_name'],
        patient_age=item['patient_age'],
        patient_gender=item['patient_gender'],
        blood_group=item['blood_group'],
        bags_needed=item['bags_needed'],
        division=loc['division'],
        district=loc['district'],
        upozila=loc['upozila'],
        hospital_name=item['hospital_name'],
        hospital_address=item.get('hospital_address'),
        needed_date=item['needed_date'],
        needed_time=item['needed_time'],
        contact_number=item['contact_number'],
        urgency=item['urgency'],
        description=item.get('description'),
        status=item['status'],
    )
print("Seeded BloodNeedPost:", BloodNeedPost.objects.count())

# 3. Seed Posts (Medicine Need)
med_data = []
with open(settings.BASE_DIR / 'dataset' / 'medicine_need_post.json', 'r', encoding='utf-8') as f:
    med_data = json.load(f)

MedicineNeedPost.objects.all().delete()
for item in med_data:
    user = get_user_by_pattern(item['user'])
    if not user: continue
    loc = get_location(item)
    MedicineNeedPost.objects.create(
        user=user,
        medicine_name=item['medicine_name'],
        quantity=item['quantity'],
        description=item.get('description'),
        division=loc['division'],
        district=loc['district'],
        upozila=loc['upozila'],
        address=item.get('address'),
        contact_number=item['contact_number'],
        urgency=item['urgency'],
        status=item['status'],
    )
print("Seeded MedicineNeedPost:", MedicineNeedPost.objects.count())

# 4. Seed Posts (Equipment Need)
eq_data = []
with open(settings.BASE_DIR / 'dataset' / 'equipment_need_post.json', 'r', encoding='utf-8') as f:
    eq_data = json.load(f)

EquipmentNeedPost.objects.all().delete()
for item in eq_data:
    user = get_user_by_pattern(item['user'])
    if not user: continue
    loc = get_location(item)
    EquipmentNeedPost.objects.create(
        user=user,
        equipment_name=item['equipment_name'],
        quantity=item['quantity'],
        condition=item['condition'],
        image=item.get('image'),
        description=item.get('description'),
        division=loc['division'],
        district=loc['district'],
        upozila=loc['upozila'],
        address=item.get('address'),
        contact_number=item['contact_number'],
        urgency=item['urgency'],
        status=item['status'],
    )
print("Seeded EquipmentNeedPost:", EquipmentNeedPost.objects.count())

# 5. Seed Posts (General)
gen_data = []
with open(settings.BASE_DIR / 'dataset' / 'general_post.json', 'r', encoding='utf-8') as f:
    gen_data = json.load(f)

GeneralPost.objects.all().delete()
for item in gen_data:
    user = get_user_by_pattern(item['user'])
    if not user: continue
    loc = get_location(item)
    GeneralPost.objects.create(
        user=user,
        title=item['title'],
        content=item['content'],
        image=item.get('image'),
        division=loc['division'],
        district=loc['district'],
        upozila=loc['upozila'],
        contact_number=item.get('contact_number'),
        status=item['status'],
    )
print("Seeded GeneralPost:", GeneralPost.objects.count())
