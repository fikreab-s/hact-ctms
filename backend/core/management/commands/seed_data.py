"""
seed_data — Management command to populate the database with sample data
==========================================================================
Creates a realistic HACT clinical trial dataset for development and testing.

Usage: python manage.py seed_data
       python manage.py seed_data --flush   (wipes existing data first)
"""

from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Seed the database with sample HACT CTMS data for development"

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete all existing HACT data before seeding",
        )

    def handle(self, *args, **options):
        if options["flush"]:
            self._flush_data()

        self.stdout.write(self.style.HTTP_INFO("\n" + "=" * 60))
        self.stdout.write(self.style.HTTP_INFO("  HACT CTMS — Seeding Sample Data"))
        self.stdout.write(self.style.HTTP_INFO("=" * 60 + "\n"))

        admin_user = self._ensure_admin()
        roles = self._create_roles()
        users = self._create_users(roles)
        study = self._create_study(admin_user)
        sites = self._create_sites(study, admin_user)
        self._assign_site_staff(users, sites)
        subjects = self._create_subjects(study, sites, admin_user)
        visits = self._create_visits(study, admin_user)
        self._create_subject_visits(subjects, visits, admin_user)
        self._create_forms(study, admin_user)
        self._create_adverse_events(study, subjects, users, admin_user)
        self._create_lab_data(study, subjects, admin_user)
        self._create_ops_data(study, sites, admin_user)

        self.stdout.write(self.style.SUCCESS("\n✅ Seed data created successfully!\n"))

    def _flush_data(self):
        from audit.models import AuditLog
        from clinical.models import (
            FormInstance, ItemResponse, Query, Item, Form,
            SubjectVisit, Visit, Subject, Site, Study,
        )
        from safety.models import SafetyReview, CiomsForm, AdverseEvent
        from lab.models import SampleCollection, LabResult, ReferenceRange
        from ops.models import Milestone, TrainingRecord, Contract
        from outputs.models import DataQualityReport, DatasetSnapshot
        from accounts.models import SiteStaff, UserRole, ExternalSystemIdentity

        self.stdout.write("  Flushing existing data...")
        for model in [
            AuditLog, DataQualityReport, DatasetSnapshot,
            Milestone, TrainingRecord, Contract,
            SampleCollection, LabResult, ReferenceRange,
            SafetyReview, CiomsForm, AdverseEvent,
            Query, ItemResponse, FormInstance, Item, Form,
            SubjectVisit, Visit, Subject,
            SiteStaff, ExternalSystemIdentity, UserRole,
            Site, Study,
        ]:
            count = model.objects.all().delete()[0]
            if count:
                self.stdout.write(f"    Deleted {count} {model.__name__} records")

    def _ensure_admin(self):
        user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@hact.gov.et",
                "first_name": "System",
                "last_name": "Admin",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            user.set_password("Admin@2026!")
            user.save()
            self.stdout.write(self.style.SUCCESS("  ✓ Created admin superuser"))
        else:
            self.stdout.write("  • Admin superuser already exists")
        return user

    def _create_roles(self):
        from accounts.models import Role

        role_data = [
            ("admin", "Full system administrator"),
            ("study_admin", "Study-level administrator"),
            ("data_manager", "Forms, queries, subjects, data quality"),
            ("site_coordinator", "Data entry at assigned sites"),
            ("monitor", "Read-only clinical data monitoring (CRA)"),
            ("safety_officer", "AE/SAE and safety reporting"),
            ("lab_manager", "Lab data and sample tracking"),
            ("ops_manager", "Contracts, training, milestones"),
            ("auditor", "Read-only audit trail access"),
        ]

        roles = {}
        for name, desc in role_data:
            role, created = Role.objects.get_or_create(
                name=name, defaults={"description": desc},
            )
            roles[name] = role
            if created:
                self.stdout.write(f"  ✓ Created role: {name}")

        self.stdout.write(self.style.SUCCESS(f"  ✓ {len(roles)} roles ready"))
        return roles

    def _create_users(self, roles):
        from accounts.models import UserRole

        user_data = [
            ("dr.turemo", "turemo@hact.gov.et", "Turemo", "Bedaso", ["study_admin"]),
            ("dm.sarah", "sarah@hact.gov.et", "Sarah", "Bekele", ["data_manager"]),
            ("sc.nurse.addis", "nurse.addis@hact.gov.et", "Almaz", "Tadesse", ["site_coordinator"]),
            ("sc.nurse.hawassa", "nurse.hawassa@hact.gov.et", "Fatima", "Mohammed", ["site_coordinator"]),
            ("cra.monitor", "monitor@hact.gov.et", "Daniel", "Abebe", ["monitor"]),
            ("safety.officer", "safety@hact.gov.et", "Helen", "Girma", ["safety_officer"]),
            ("lab.manager", "lab@hact.gov.et", "Solomon", "Tekle", ["lab_manager"]),
            ("ops.manager", "ops@hact.gov.et", "Meron", "Haile", ["ops_manager"]),
            ("auditor", "auditor@hact.gov.et", "Yonas", "Wolde", ["auditor"]),
        ]

        users = {}
        for username, email, first, last, role_names in user_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": email, "first_name": first,
                    "last_name": last, "is_active": True,
                },
            )
            if created:
                user.set_password("Test@2026!")
                user.save()
            for role_name in role_names:
                UserRole.objects.get_or_create(user=user, role=roles[role_name])
            users[username] = user

        self.stdout.write(self.style.SUCCESS(f"  ✓ {len(users)} users created with roles"))
        return users

    def _create_study(self, admin_user):
        from clinical.models import Study

        study, _ = Study.objects.get_or_create(
            protocol_number="HACT-2026-001",
            defaults={
                "name": "Phase III RCT of Antimalarial Compound X",
                "phase": "III",
                "status": "active",
                "sponsor": "Horn of Africa Clinical Trials",
                "start_date": date(2026, 1, 15),
                "end_date": date(2027, 6, 30),
                "created_by": admin_user,
                "updated_by": admin_user,
            },
        )
        self.stdout.write(self.style.SUCCESS(f"  ✓ Study: {study.protocol_number}"))
        return study

    def _create_sites(self, study, admin_user):
        from clinical.models import Site

        site_data = [
            ("ETH-001", "Tikur Anbessa Specialized Hospital", "Addis Ababa, Ethiopia", "Ethiopia", "Dr. Turemo Bedaso", True),
            ("ETH-002", "Hawassa University Referral Hospital", "Hawassa, Ethiopia", "Ethiopia", "Dr. Abebe Kebede", True),
            ("KEN-001", "Kenyatta National Hospital", "Nairobi, Kenya", "Kenya", "Dr. James Ochieng", False),
        ]

        sites = []
        for code, name, addr, country, pi, is_active in site_data:
            site, _ = Site.objects.get_or_create(
                site_code=code, study=study,
                defaults={
                    "name": name, "address": addr, "country": country,
                    "principal_investigator": pi,
                    "status": "active" if is_active else "pending",
                    "activation_date": date(2026, 2, 1) if is_active else None,
                    "created_by": admin_user, "updated_by": admin_user,
                },
            )
            sites.append(site)

        self.stdout.write(self.style.SUCCESS(f"  ✓ {len(sites)} sites created"))
        return sites

    def _assign_site_staff(self, users, sites):
        from accounts.models import SiteStaff

        assignments = [
            ("sc.nurse.addis", sites[0], "Site Coordinator"),
            ("sc.nurse.hawassa", sites[1], "Site Coordinator"),
            ("dr.turemo", sites[0], "Principal Investigator"),
            ("dm.sarah", sites[0], "Data Manager"),
            ("dm.sarah", sites[1], "Data Manager"),
        ]
        for username, site, role in assignments:
            user = users.get(username)
            if user:
                SiteStaff.objects.get_or_create(
                    user=user, site=site,
                    defaults={"role_at_site": role, "start_date": date(2026, 2, 1)},
                )
        self.stdout.write(self.style.SUCCESS(f"  ✓ {len(assignments)} site staff assignments"))

    def _create_subjects(self, study, sites, admin_user):
        from clinical.models import Subject

        subjects = []
        subject_data = [
            ("HACT-001-001", "SCR-001", sites[0], "enrolled"),
            ("HACT-001-002", "SCR-002", sites[0], "enrolled"),
            ("HACT-001-003", "SCR-003", sites[0], "enrolled"),
            ("HACT-001-004", "SCR-004", sites[0], "screened"),
            ("HACT-001-005", "SCR-005", sites[0], "screen_failed"),
            ("HACT-001-006", "SCR-006", sites[0], "enrolled"),
            ("HACT-002-001", "SCR-101", sites[1], "enrolled"),
            ("HACT-002-002", "SCR-102", sites[1], "enrolled"),
            ("HACT-002-003", "SCR-103", sites[1], "screened"),
            ("HACT-002-004", "SCR-104", sites[1], "discontinued"),
        ]

        for subj_id, scr_num, site, status in subject_data:
            enroll_date = date(2026, 3, 1) if status == "enrolled" else None
            subj, _ = Subject.objects.get_or_create(
                subject_identifier=subj_id, study=study,
                defaults={
                    "screening_number": scr_num, "site": site,
                    "status": status, "enrollment_date": enroll_date,
                    "consent_signed_date": date(2026, 2, 20),
                    "created_by": admin_user, "updated_by": admin_user,
                },
            )
            subjects.append(subj)

        self.stdout.write(self.style.SUCCESS(f"  ✓ {len(subjects)} subjects created"))
        return subjects

    def _create_visits(self, study, admin_user):
        from clinical.models import Visit

        visit_data = [
            ("Screening", 1, -14, True, False, False),
            ("Baseline / Day 0", 2, 0, False, True, False),
            ("Day 3", 3, 3, False, False, True),
            ("Day 7", 4, 7, False, False, True),
            ("Day 14", 5, 14, False, False, True),
            ("Day 28", 6, 28, False, False, True),
            ("Day 42 (End of Study)", 7, 42, False, False, True),
        ]

        visits = []
        for name, order, day, is_scr, is_bl, is_fu in visit_data:
            visit, _ = Visit.objects.get_or_create(
                visit_name=name, study=study,
                defaults={
                    "visit_order": order, "planned_day": day,
                    "is_screening": is_scr, "is_baseline": is_bl,
                    "is_follow_up": is_fu,
                    "created_by": admin_user, "updated_by": admin_user,
                },
            )
            visits.append(visit)

        self.stdout.write(self.style.SUCCESS(f"  ✓ {len(visits)} visits created"))
        return visits

    def _create_subject_visits(self, subjects, visits, admin_user):
        from clinical.models import SubjectVisit

        count = 0
        enrolled = [s for s in subjects if s.status == "enrolled"]
        for subj in enrolled:
            for visit in visits[:4]:
                SubjectVisit.objects.get_or_create(
                    subject=subj, visit=visit,
                    defaults={
                        "scheduled_date": date(2026, 3, 1) + timedelta(days=max(visit.planned_day, 0)),
                        "actual_date": date(2026, 3, 1) + timedelta(days=max(visit.planned_day, 0)),
                        "status": "completed",
                        "created_by": admin_user, "updated_by": admin_user,
                    },
                )
                count += 1

        self.stdout.write(self.style.SUCCESS(f"  ✓ {count} subject visits created"))

    def _create_forms(self, study, admin_user):
        from clinical.models import Form, Item

        form_data = [
            ("Demographics", "1.0", [
                ("weight_kg", "Weight (kg)", "decimal", True),
                ("height_cm", "Height (cm)", "decimal", True),
            ]),
            ("Vital Signs", "1.0", [
                ("systolic_bp", "Systolic BP (mmHg)", "integer", True),
                ("diastolic_bp", "Diastolic BP (mmHg)", "integer", True),
                ("heart_rate", "Heart Rate (bpm)", "integer", True),
                ("temperature", "Temperature (°C)", "decimal", True),
            ]),
            ("Medical History", "1.0", [
                ("condition", "Condition/Diagnosis", "text", True),
                ("ongoing", "Currently Ongoing?", "boolean", True),
            ]),
            ("Adverse Event Form", "1.0", [
                ("ae_term", "AE Term", "text", True),
                ("onset_date", "Onset Date", "date", True),
                ("severity", "Severity", "select", True),
                ("outcome", "Outcome", "select", True),
            ]),
        ]

        forms = []
        for form_name, version, items in form_data:
            form, _ = Form.objects.get_or_create(
                name=form_name, study=study,
                defaults={
                    "version": version, "is_active": True,
                    "created_by": admin_user, "updated_by": admin_user,
                },
            )
            forms.append(form)
            for order, (field_name, label, field_type, required) in enumerate(items, 1):
                Item.objects.get_or_create(
                    form=form, field_name=field_name,
                    defaults={
                        "field_label": label, "field_type": field_type,
                        "required": required, "order": order,
                        "created_by": admin_user, "updated_by": admin_user,
                    },
                )

        self.stdout.write(self.style.SUCCESS(f"  ✓ {len(forms)} forms with items created"))

    def _create_adverse_events(self, study, subjects, users, admin_user):
        from safety.models import AdverseEvent

        enrolled = [s for s in subjects if s.status == "enrolled"]
        safety_user = users.get("safety.officer", admin_user)

        ae_data = [
            (enrolled[0], "Mild headache", "mild", False, "possible", "recovered"),
            (enrolled[1], "Nausea", "mild", False, "probable", "recovered"),
            (enrolled[2], "Elevated liver enzymes (Grade 2)", "moderate", True, "possible", "recovering"),
        ]

        for subj, term, sev, serious, caus, outcome in ae_data:
            AdverseEvent.objects.get_or_create(
                subject=subj, ae_term=term, study=study,
                defaults={
                    "severity": sev, "serious": serious,
                    "causality": caus, "outcome": outcome,
                    "start_date": date(2026, 3, 10),
                    "reported_by": safety_user,
                    "created_by": admin_user, "updated_by": admin_user,
                },
            )

        self.stdout.write(self.style.SUCCESS(f"  ✓ {len(ae_data)} adverse events created"))

    def _create_lab_data(self, study, subjects, admin_user):
        from lab.models import LabResult, ReferenceRange

        ref_data = [
            ("Hemoglobin", 12.0, 17.5, "M"),
            ("Hemoglobin", 11.0, 15.5, "F"),
            ("WBC Count", 4.0, 11.0, "all"),
            ("Platelet Count", 150.0, 400.0, "all"),
            ("ALT", 7.0, 56.0, "all"),
            ("Parasitemia", 0.0, 0.0, "all"),
        ]

        for test, low, high, gender in ref_data:
            ReferenceRange.objects.get_or_create(
                test_name=test, study=study, gender=gender,
                defaults={
                    "range_low": Decimal(str(low)),
                    "range_high": Decimal(str(high)),
                    "created_by": admin_user, "updated_by": admin_user,
                },
            )

        enrolled = [s for s in subjects if s.status == "enrolled"][:3]
        count = 0
        for subj in enrolled:
            for test, value, unit, flag in [
                ("Hemoglobin", "14.2", "g/dL", "N"),
                ("WBC Count", "6.5", "x10^9/L", "N"),
                ("Platelet Count", "250", "x10^9/L", "N"),
                ("ALT", "32", "U/L", "N"),
                ("Parasitemia", "12500", "parasites/uL", "H"),
            ]:
                LabResult.objects.get_or_create(
                    subject=subj, test_name=test, result_date=date(2026, 3, 1),
                    defaults={
                        "result_value": value, "unit": unit, "flag": flag,
                        "created_by": admin_user, "updated_by": admin_user,
                    },
                )
                count += 1

        self.stdout.write(self.style.SUCCESS(
            f"  ✓ {len(ref_data)} reference ranges + {count} lab results created"
        ))

    def _create_ops_data(self, study, sites, admin_user):
        from ops.models import Contract, TrainingRecord, Milestone

        for i, site in enumerate(sites):
            Contract.objects.get_or_create(
                contract_number=f"HACT-CTR-2026-{i+1:03d}", site=site,
                defaults={
                    "status": "active", "start_date": date(2026, 1, 1),
                    "end_date": date(2027, 6, 30),
                    "budget_amount": Decimal("150000.00"),
                    "created_by": admin_user, "updated_by": admin_user,
                },
            )

        for site in sites[:2]:
            for tt in ["GCP Training", "Protocol Training", "eCRF Training", "Safety SOP"]:
                TrainingRecord.objects.get_or_create(
                    site=site, staff_name=f"Staff at {site.site_code}",
                    training_type=tt,
                    defaults={
                        "training_date": date(2026, 2, 15),
                        "created_by": admin_user, "updated_by": admin_user,
                    },
                )

        milestones = [
            ("Site Initiation Visit", "completed", date(2026, 2, 1), date(2026, 2, 3)),
            ("First Patient In", "completed", date(2026, 3, 1), date(2026, 3, 1)),
            ("50% Enrollment", "in_progress", date(2026, 6, 1), None),
            ("Last Patient Last Visit", "planned", date(2027, 3, 1), None),
            ("Database Lock", "planned", date(2027, 4, 1), None),
        ]
        for ms_type, status, planned, actual in milestones:
            Milestone.objects.get_or_create(
                study=study, milestone_type=ms_type,
                defaults={
                    "site": sites[0], "status": status,
                    "planned_date": planned, "actual_date": actual,
                    "created_by": admin_user, "updated_by": admin_user,
                },
            )

        self.stdout.write(self.style.SUCCESS(
            f"  ✓ {len(sites)} contracts, 8 training records, {len(milestones)} milestones created"
        ))
