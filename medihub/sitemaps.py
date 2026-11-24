import xml.etree.ElementTree as ET
from datetime import datetime
from django.http import HttpResponse
from django.views import View
from django.utils.timezone import now

from profiles.models.doctor_prof_mod import Doctor
from profiles.models.diagnostic_prof_mod import DiagnosticProfile
from profiles.models.pharmacy_prof_mod import PharmacyProfile
from profiles.models.ambulance_prof_mod import AmbulanceProfile
from profiles.models.blood_donor_mod import BloodDonor
from blog.models.blog_post_mod import BlogPost


class SitemapXMLView(View):
    """
    Dynamically generates standard sitemap.xml for Google, Bing, and other search engines.
    Covers:
      - Static high-priority pages (home, doctors, diagnostics, pharmacies, ambulances, donors, blogs)
      - Dynamic active Doctor profiles (/doctor-profile/<id>)
      - Dynamic active Diagnostic profiles (/diagnostic-profile/<id>)
      - Dynamic active Pharmacy profiles (/pharmacy-profile/<id>)
      - Dynamic active Ambulance profiles (/ambulance-profile/<id>)
      - Dynamic active Donor profiles (/donor-profile/<id>)
      - Dynamic published Blog posts (/blog/<id>)
    """

    def get(self, request, *args, **kwargs):
        # Determine host protocol and domain
        host = request.get_host()
        scheme = 'https' if request.is_secure() or 'https' in request.META.get('HTTP_X_FORWARDED_PROTO', '') else 'http'
        base_url = f"{scheme}://{host}"

        urlset = ET.Element('urlset', xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')

        today_str = now().strftime('%Y-%m-%d')

        def add_url(loc, changefreq='weekly', priority='0.8', lastmod=None):
            url_elem = ET.SubElement(urlset, 'url')
            loc_elem = ET.SubElement(url_elem, 'loc')
            loc_elem.text = loc
            if lastmod:
                mod_elem = ET.SubElement(url_elem, 'lastmod')
                mod_elem.text = str(lastmod)[:10]
            freq_elem = ET.SubElement(url_elem, 'changefreq')
            freq_elem.text = changefreq
            pri_elem = ET.SubElement(url_elem, 'priority')
            pri_elem.text = str(priority)

        # 1. Main Static / Portal Pages
        static_pages = [
            ('/', 'daily', '1.0'),
            ('/doctors', 'daily', '0.9'),
            ('/diagnostics', 'daily', '0.9'),
            ('/pharmacies', 'daily', '0.9'),
            ('/medicines', 'daily', '0.9'),
            ('/ambulances', 'weekly', '0.8'),
            ('/donors', 'daily', '0.8'),
            ('/blogs', 'daily', '0.8'),
            ('/community', 'hourly', '0.7'),
            ('/about', 'monthly', '0.5'),
            ('/contact', 'monthly', '0.5'),
            ('/privacy-policy', 'monthly', '0.3'),
            ('/terms-of-service', 'monthly', '0.3'),
        ]
        for path, freq, pri in static_pages:
            add_url(f"{base_url}{path}", changefreq=freq, priority=pri, lastmod=today_str)

        # 2. Doctors
        try:
            doctors = Doctor.objects.filter(is_active=True).values('id', 'updated')
            for doc in doctors:
                doc_lastmod = doc['updated'].strftime('%Y-%m-%d') if doc.get('updated') else today_str
                add_url(f"{base_url}/doctor-profile/{doc['id']}", changefreq='weekly', priority='0.8', lastmod=doc_lastmod)
        except Exception:
            pass

        # 3. Diagnostic Centers
        try:
            diagnostics = DiagnosticProfile.objects.filter(is_active=True).values('id')
            for diag in diagnostics:
                add_url(f"{base_url}/diagnostic-profile/{diag['id']}", changefreq='weekly', priority='0.8', lastmod=today_str)
        except Exception:
            pass

        # 4. Pharmacies
        try:
            pharmacies = PharmacyProfile.objects.filter(is_active=True).values('id', 'updated')
            for pharm in pharmacies:
                pharm_lastmod = pharm['updated'].strftime('%Y-%m-%d') if pharm.get('updated') else today_str
                add_url(f"{base_url}/pharmacy-profile/{pharm['id']}", changefreq='weekly', priority='0.8', lastmod=pharm_lastmod)
        except Exception:
            pass

        # 5. Ambulances
        try:
            ambulances = AmbulanceProfile.objects.filter(is_active=True).values('id')
            for amb in ambulances:
                add_url(f"{base_url}/ambulance-profile/{amb['id']}", changefreq='weekly', priority='0.7', lastmod=today_str)
        except Exception:
            pass

        # 6. Blood Donors
        try:
            donors = BloodDonor.objects.filter(is_active=True).values('id')
            for donor in donors:
                add_url(f"{base_url}/donor-profile/{donor['id']}", changefreq='weekly', priority='0.7', lastmod=today_str)
        except Exception:
            pass

        # 7. Published Blogs
        try:
            blogs = BlogPost.objects.filter(status='published').values('id', 'updated')
            for post in blogs:
                blog_lastmod = post['updated'].strftime('%Y-%m-%d') if post.get('updated') else today_str
                add_url(f"{base_url}/blog/{post['id']}", changefreq='monthly', priority='0.7', lastmod=blog_lastmod)
        except Exception:
            pass

        xml_content = ET.tostring(urlset, encoding='utf-8', xml_declaration=True)
        return HttpResponse(xml_content, content_type='application/xml; charset=utf-8')


class RobotsTxtView(View):
    """
    Dynamically serves robots.txt referencing the correct sitemap host.
    """

    def get(self, request, *args, **kwargs):
        host = request.get_host()
        scheme = 'https' if request.is_secure() or 'https' in request.META.get('HTTP_X_FORWARDED_PROTO', '') else 'http'
        lines = [
            "User-agent: *",
            "Allow: /",
            "Disallow: /admin/",
            "Disallow: /api/",
            "Disallow: /dashboard/",
            "Disallow: /profile/",
            f"Sitemap: {scheme}://{host}/sitemap.xml",
        ]
        return HttpResponse("\n".join(lines), content_type="text/plain; charset=utf-8")
