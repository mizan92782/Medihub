# 🏥 MediHub Deployment Credentials & Accounts Directory

This document contains all system administrator and demo user account credentials created during the root database seed.

---

## 🔑 1. System Administrator (Superuser)
Full administrative control over all portals, doctors, donors, pharmacies, diagnostics, ambulances, banners, and blogs.

| Role | Email | Password | Django Admin URL |
| :--- | :--- | :--- | :--- |
| **Super Admin** | `admin@medihub.com` | `Admin@12345` | [http://localhost:8000/admin/](http://localhost:8000/admin/) |

---

## 🩺 2. Verified Doctors (Top 20 Specialists)
All doctor accounts have verified BMDC registration, attached hospitals, schedules, consultation fees, and authentic ratings.

| Doctor Name | Email | Password | Specialization | BMDC Number | Consultation Fee |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Dr. Anisur Rahman** | `dr.anisur@medihub.com` | `Doctor@1234` | Cardiology | BMDC-A-10201 | ৳1,500 |
| **Dr. Farzana Yasmin** | `dr.farzana@medihub.com` | `Doctor@1234` | Gynecology & Obstetrics | BMDC-A-10202 | ৳1,200 |
| **Dr. Tariqul Islam** | `dr.tariqul@medihub.com` | `Doctor@1234` | Neurology | BMDC-A-10203 | ৳1,500 |
| **Dr. Mahmudul Hasan** | `dr.mahmudul@medihub.com` | `Doctor@1234` | Pediatrics | BMDC-A-10204 | ৳1,200 |
| **Dr. Sabrina Chowdhury** | `dr.sabrina@medihub.com` | `Doctor@1234` | Endocrinology | BMDC-A-10205 | ৳1,300 |
| **Dr. Kamrul Ahsan** | `dr.kamrul@medihub.com` | `Doctor@1234` | Orthopedics | BMDC-A-10206 | ৳1,500 |
| **Dr. Nusrat Jahan** | `dr.nusrat@medihub.com` | `Doctor@1234` | Dermatology | BMDC-A-10207 | ৳1,200 |
| **Dr. Shamsul Alam** | `dr.shamsul@medihub.com` | `Doctor@1234` | Gastroenterology | BMDC-A-10208 | ৳1,400 |
| **Dr. Afsana Karim** | `dr.afsana@medihub.com` | `Doctor@1234` | Ophthalmology | BMDC-A-10209 | ৳1,000 |
| **Dr. Rezaul Karim** | `dr.rezaul@medihub.com` | `Doctor@1234` | Nephrology | BMDC-A-10210 | ৳1,400 |
| **Dr. Tahmina Begum** | `dr.tahmina@medihub.com` | `Doctor@1234` | Psychiatry | BMDC-A-10211 | ৳1,200 |
| **Dr. Moniruzzaman Khan** | `dr.moniruzzaman@medihub.com` | `Doctor@1234` | ENT | BMDC-A-10212 | ৳1,100 |
| **Dr. Sharmin Akter** | `dr.sharmin@medihub.com` | `Doctor@1234` | General Surgery | BMDC-A-10213 | ৳1,200 |
| **Dr. Asif Iqbal** | `dr.asif@medihub.com` | `Doctor@1234` | General Medicine | BMDC-A-10214 | ৳1,400 |
| **Dr. Nazmul Huda** | `dr.nazmul@medihub.com` | `Doctor@1234` | Oncology | BMDC-A-10215 | ৳1,600 |
| **Dr. Rashedul Islam** | `dr.rashedul@medihub.com` | `Doctor@1234` | Urology | BMDC-A-10216 | ৳1,400 |
| **Dr. Kaniz Fatema** | `dr.kaniz@medihub.com` | `Doctor@1234` | Pediatrics | BMDC-A-10217 | ৳1,400 |
| **Dr. Shahinur Rahman** | `dr.shahinur@medihub.com` | `Doctor@1234` | Cardiology | BMDC-A-10218 | ৳1,600 |
| **Dr. Mehedi Hasan** | `dr.mehedi@medihub.com` | `Doctor@1234` | Orthopedics / Rehab | BMDC-A-10219 | ৳1,000 |
| **Dr. Nilufar Yasmin** | `dr.nilufar@medihub.com` | `Doctor@1234` | Gynecology | BMDC-A-10220 | ৳1,500 |

---

## 🩸 3. Blood Donors Directory (24 Donors covering all 8 Blood Groups)
Password for all blood donor profiles: `Donor@1234`

| Donor Name | Email | Blood Group | Location | Status | Lives Saved |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Arifur Rahman** | `donor.arif@medihub.com` | `A+` | Dhanmondi, Dhaka | Available | 12 |
| **Sumon Chowdhury** | `donor.sumon@medihub.com` | `A+` | Mirpur, Dhaka | Available | 8 |
| **Fariha Tasnim** | `donor.fariha@medihub.com` | `A+` | Uttara, Dhaka | Available | 5 |
| **Al-Mamun Sheikh** | `donor.mamun@medihub.com` | `A+` | Rajshahi | Available | 14 |
| **Shihab Uddin** | `donor.shihab@medihub.com` | `A-` | Gulshan, Dhaka | Available | 6 |
| **Nabil Ahmed** | `donor.nabil@medihub.com` | `A-` | Chittagong | Available | 4 |
| **Tanmoy Sarker** | `donor.tanmoy@medihub.com` | `B+` | Dhanmondi, Dhaka | Available | 15 |
| **Roksana Begum** | `donor.roksana@medihub.com` | `B+` | Mirpur, Dhaka | Available | 7 |
| **Enamul Haque** | `donor.enamul@medihub.com` | `B+` | Sylhet | Available | 9 |
| **Zahir Raihan** | `donor.zahir@medihub.com` | `B+` | Chittagong | Available | 11 |
| **Moumita Paul** | `donor.moumita@medihub.com` | `B-` | Uttara, Dhaka | Available | 4 |
| **Saiful Islam** | `donor.saiful@medihub.com` | `B-` | Rajshahi | Available | 8 |
| **Rubel Hossain** | `donor.rubel@medihub.com` | `O+` | Dhanmondi, Dhaka | Available | 18 |
| **Anika Tabassum** | `donor.anika@medihub.com` | `O+` | Mirpur, Dhaka | Available | 6 |
| **Shakil Khan** | `donor.shakil@medihub.com` | `O+` | Chittagong | Available | 10 |
| **Jasim Uddin** | `donor.jasim@medihub.com` | `O+` | Sylhet | Available | 12 |
| **Faruk Ahmed** | `donor.faruk@medihub.com` | `O-` | Gulshan, Dhaka | Available | 9 |
| **Mehnaz Chowdhury** | `donor.mehnaz@medihub.com` | `O-` | Dhanmondi, Dhaka | Available | 7 |
| **Hasan Mahmud** | `donor.hasan@medihub.com` | `AB+` | Uttara, Dhaka | Available | 11 |
| **Tania Sultana** | `donor.tania@medihub.com` | `AB+` | Chittagong | Available | 5 |
| **Babul Akter** | `donor.babul@medihub.com` | `AB+` | Rajshahi | Available | 8 |
| **Ashraf Ali** | `donor.ashraf@medihub.com` | `AB-` | Mirpur, Dhaka | Available | 4 |
| **Salma Khatun** | `donor.salma@medihub.com` | `AB-` | Dhanmondi, Dhaka | Available | 6 |
| **Kamal Hossain** | `donor.kamal@medihub.com` | `AB-` | Sylhet | Available | 5 |

---

## 💊 4. Pharmacies Directory (8 Reputable Pharmacies)
Password for all pharmacy profiles: `Pharmacy@1234`

| Pharmacy Name | Login Email | Contact Phone | Address |
| :--- | :--- | :--- | :--- |
| **Labaid Model Pharmacy** | `pharmacy.labaid@medihub.com` | `01740000001` | House 1, Road 4, Dhanmondi, Dhaka |
| **Tamanna Pharmacy** | `pharmacy.tamanna@medihub.com` | `01740000002` | Plot 14, Block B, Mirpur-10, Dhaka |
| **Green Life Pharmacy** | `pharmacy.greenlife@medihub.com` | `01740000003` | 32 Green Road, Dhanmondi, Dhaka |
| **Al-Madina Model Pharmacy** | `pharmacy.almadina@medihub.com` | `01740000004` | House 18, Sector 7, Uttara, Dhaka |
| **Square Hospital Pharmacy** | `pharmacy.square@medihub.com` | `01740000005` | Panthapath, Dhaka |
| **Popular Pharmacy** | `pharmacy.popular@medihub.com` | `01740000006` | Road 2, Dhanmondi, Dhaka |
| **Chittagong Central Pharma** | `pharmacy.ctgcentral@medihub.com` | `01740000007` | GEC Circle, Chittagong |
| **Sylhet Health Pharmacy** | `pharmacy.sylhet@medihub.com` | `01740000008` | Zindabazar, Sylhet |

---

## 🔬 5. Diagnostic Centers (8 Diagnostic Centers & 20 Standard Tests)
Password for all diagnostic profiles: `Diagnostic@1234`

| Diagnostic Center Name | Login Email | Contact Phone | Key Specialization |
| :--- | :--- | :--- | :--- |
| **Popular Diagnostic Centre** | `diagnostic.popular@medihub.com` | `01750000001` | Pathology, 1.5T MRI, 128-Slice CT |
| **Ibn Sina Diagnostic Centre** | `diagnostic.ibnsina@medihub.com` | `01750000002` | 3T MRI, High-Res USG, Digital X-Ray |
| **Square Hospital Lab** | `diagnostic.square@medihub.com` | `01750000003` | Clinical Biochemistry, Echo, Doppler |
| **Praava Health Diagnostics** | `diagnostic.praava@medihub.com` | `01750000004` | Molecular Biology, Fast Home Sample |
| **Labaid Diagnostic Centre** | `diagnostic.labaid@medihub.com` | `01750000005` | Cardiac Imaging, Mammography |
| **Medinova Medical Services** | `diagnostic.medinova@medihub.com` | `01750000006` | Hormonal Assays, Histopathology |
| **Chevron Clinical Laboratory** | `diagnostic.chevron@medihub.com` | `01750000007` | Comprehensive Pathology (Chittagong) |
| **Al-Haramain Diagnostics** | `diagnostic.alharamain@medihub.com` | `01750000008` | Automated Hematology (Sylhet) |

---

## 🚑 6. Emergency Ambulances (8 Ambulances)
Password for all ambulance profiles: `Ambulance@1234`

| Ambulance Service | Type | Login Email | Hotline Phone | Standby Base |
| :--- | :--- | :--- | :--- | :--- |
| **Evercare ICU Mobile Hospital** | ICU (Ventilator) | `ambulance.dhaka.icu@medihub.com` | `01760000001` | Dhanmondi, Dhaka |
| **National Heart Foundation** | Cardiac Ambulance | `ambulance.heart.cardiac@medihub.com` | `01760000002` | Mirpur, Dhaka |
| **Dhaka Emergency AC Ambulance** | AC Ambulance | `ambulance.dhaka.ac1@medihub.com` | `01760000003` | Green Road, Dhaka |
| **Uttara Fast Response** | AC Ambulance | `ambulance.uttara.ac2@medihub.com` | `01760000004` | Uttara, Dhaka |
| **BSMMU Neonatal Mobile Unit** | Neonatal (NICU) | `ambulance.bssmu.nicu@medihub.com` | `01760000005` | Shahbagh, Dhaka |
| **Central Al-Markazul Freezing** | Freezing / Mortuary | `ambulance.freeze@medihub.com` | `01760000006` | Mohammadpur, Dhaka |
| **Chittagong Highway Emergency** | Advanced Cardiac | `ambulance.ctg.express@medihub.com` | `01760000007` | Agrabad, Chittagong |
| **Sylhet Metro 24/7 Service** | AC Ambulance | `ambulance.sylhet.247@medihub.com` | `01760000008` | Subid Bazar, Sylhet |

---

## 👤 7. Regular Test Patients
Password for all patient profiles: `User@1234`

| Patient Name | Email | Gender | Contact Phone | Address |
| :--- | :--- | :--- | :--- | :--- |
| **Rahim Uddin** | `user.rahim@medihub.com` | Male | `01711000001` | Dhanmondi, Dhaka |
| **Nasrin Akter** | `user.nasrin@medihub.com` | Female | `01811000002` | Mirpur-2, Dhaka |
| **Tanvir Hasan** | `user.tanvir@medihub.com` | Male | `01911000003` | Uttara, Dhaka |
| **Sadia Jahan** | `user.sadia@medihub.com` | Female | `01611000004` | Khulshi, Chittagong |
| **Karim Chowdhury** | `user.karim@medihub.com` | Male | `01511000005` | Zindabazar, Sylhet |

---

## 🎯 8. Sponsor Banners & AdSense Compliance Status
- `home_hero`: Active (Square Hospitals)
- `home_middle`: Active (Popular Diagnostic)
- `sidebar`: Active (Labaid Cardiac)
- `medicine_page`: Active (Green Life Pharmacy)
- `feed_inline`: Active (Ibn Sina Diagnostics)
- **`interstitial_popup`**: **DEACTIVATED (`is_active=False`)** — Ensures Google AdSense compliance with no blocking countdown popups.
