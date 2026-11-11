"""AapadaOps Database Seeding and Initial Reference Data."""

import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.alert import AlertBroadcast, AlertHazard, AlertSeverity
from app.models.district import Block, District
from app.models.incident import (
    Incident,
    IncidentCategory,
    IncidentSeverity,
    IncidentStatus,
)
from app.models.resource import Resource, ResourceStatus, ResourceType
from app.models.shelter import CycloneShelter, ShelterStatus
from app.models.team import ResponseTeam, TeamStatus
from app.models.user import User, UserRole

logger = logging.getLogger("AapadaOps.DatabaseInit")

# 30 Odisha Districts Reference Data
ODISHA_DISTRICTS_DATA = [
    {"code": "KND", "name": "Kendrapara", "name_odia": "କେନ୍ଦ୍ରାପଡ଼ା", "headquarters": "Kendrapara", "population": 1440218, "coastal_zone": True, "vulnerability_tier": 5, "center_lat": 20.5014, "center_lng": 86.4225},
    {"code": "BHK", "name": "Bhadrak", "name_odia": "ଭଦ୍ରକ", "headquarters": "Bhadrak", "population": 1506522, "coastal_zone": True, "vulnerability_tier": 5, "center_lat": 21.0544, "center_lng": 86.4962},
    {"code": "BLS", "name": "Balasore", "name_odia": "ବାଲେଶ୍ୱର", "headquarters": "Balasore", "population": 2317419, "coastal_zone": True, "vulnerability_tier": 5, "center_lat": 21.4934, "center_lng": 86.9135},
    {"code": "JAG", "name": "Jagatsinghpur", "name_odia": "ଜଗତସିଂହପୁର", "headquarters": "Jagatsinghpur", "population": 1136971, "coastal_zone": True, "vulnerability_tier": 5, "center_lat": 20.2667, "center_lng": 86.1667},
    {"code": "PUR", "name": "Puri", "name_odia": "ପୁରୀ", "headquarters": "Puri", "population": 1698730, "coastal_zone": True, "vulnerability_tier": 5, "center_lat": 19.8135, "center_lng": 85.8312},
    {"code": "GNJ", "name": "Ganjam", "name_odia": "ଗଞ୍ଜାମ", "headquarters": "Chhatrapur", "population": 3529031, "coastal_zone": True, "vulnerability_tier": 4, "center_lat": 19.3500, "center_lng": 85.0000},
    {"code": "CUT", "name": "Cuttack", "name_odia": "କଟକ", "headquarters": "Cuttack", "population": 2624470, "coastal_zone": False, "vulnerability_tier": 4, "center_lat": 20.4625, "center_lng": 85.8828},
    {"code": "KHO", "name": "Khordha", "name_odia": "ଖୋର୍ଦ୍ଧା", "headquarters": "Bhubaneswar", "population": 2251673, "coastal_zone": False, "vulnerability_tier": 3, "center_lat": 20.2961, "center_lng": 85.8245},
    {"code": "JAJ", "name": "Jajpur", "name_odia": "ଯାଜପୁର", "headquarters": "Panikoili", "population": 1826275, "coastal_zone": False, "vulnerability_tier": 4, "center_lat": 20.8500, "center_lng": 86.3333},
    {"code": "MAY", "name": "Mayurbhanj", "name_odia": "ମୟୂରଭଞ୍ଜ", "headquarters": "Baripada", "population": 2519738, "coastal_zone": False, "vulnerability_tier": 3, "center_lat": 21.9333, "center_lng": 86.7333},
    {"code": "ANG", "name": "Angul", "name_odia": "ଅନୁଗୋଳ", "headquarters": "Angul", "population": 1273821, "coastal_zone": False, "vulnerability_tier": 2, "center_lat": 20.8400, "center_lng": 85.1000},
    {"code": "BOL", "name": "Balangir", "name_odia": "ବଲାଙ୍ଗୀର", "headquarters": "Balangir", "population": 1648997, "coastal_zone": False, "vulnerability_tier": 2, "center_lat": 20.7200, "center_lng": 83.4800},
    {"code": "BRG", "name": "Bargarh", "name_odia": "ବରଗଡ଼", "headquarters": "Bargarh", "population": 1481255, "coastal_zone": False, "vulnerability_tier": 2, "center_lat": 21.3300, "center_lng": 83.6200},
    {"code": "BDH", "name": "Boudh", "name_odia": "ବୌଦ୍ଧ", "headquarters": "Boudh", "population": 441162, "coastal_zone": False, "vulnerability_tier": 2, "center_lat": 20.8400, "center_lng": 84.3200},
    {"code": "DEO", "name": "Deogarh", "name_odia": "ଦେବଗଡ଼", "headquarters": "Deogarh", "population": 312520, "coastal_zone": False, "vulnerability_tier": 1, "center_lat": 21.5300, "center_lng": 84.7300},
    {"code": "DHN", "name": "Dhenkanal", "name_odia": "ଢେଙ୍କାନାଳ", "headquarters": "Dhenkanal", "population": 1192811, "coastal_zone": False, "vulnerability_tier": 2, "center_lat": 20.6700, "center_lng": 85.6000},
    {"code": "GAJ", "name": "Gajapati", "name_odia": "ଗଜପତି", "headquarters": "Paralakhemundi", "population": 577817, "coastal_zone": False, "vulnerability_tier": 3, "center_lat": 18.8100, "center_lng": 84.0900},
    {"code": "JHS", "name": "Jharsuguda", "name_odia": "ଝାରସୁଗୁଡ଼ା", "headquarters": "Jharsuguda", "population": 579505, "coastal_zone": False, "vulnerability_tier": 1, "center_lat": 21.8500, "center_lng": 84.0100},
    {"code": "KAH", "name": "Kalahandi", "name_odia": "କଳାହାଣ୍ଡି", "headquarters": "Bhawanipatna", "population": 1576869, "coastal_zone": False, "vulnerability_tier": 2, "center_lat": 19.9000, "center_lng": 83.1600},
    {"code": "KDM", "name": "Kandhamal", "name_odia": "କନ୍ଧମାଳ", "headquarters": "Phulbani", "population": 733110, "coastal_zone": False, "vulnerability_tier": 2, "center_lat": 20.4700, "center_lng": 84.2300},
    {"code": "KRP", "name": "Koraput", "name_odia": "କୋରାପୁଟ", "headquarters": "Koraput", "population": 1379647, "coastal_zone": False, "vulnerability_tier": 2, "center_lat": 18.8100, "center_lng": 82.7100},
    {"code": "MLK", "name": "Malkangiri", "name_odia": "ମାଲକାନଗିରି", "headquarters": "Malkangiri", "population": 613192, "coastal_zone": False, "vulnerability_tier": 3, "center_lat": 18.3500, "center_lng": 81.9000},
    {"code": "NAB", "name": "Nabarangpur", "name_odia": "ନବରଙ୍ଗପୁର", "headquarters": "Nabarangpur", "population": 1220946, "coastal_zone": False, "vulnerability_tier": 2, "center_lat": 19.2300, "center_lng": 82.5500},
    {"code": "NAY", "name": "Nayagarh", "name_odia": "ନୟାଗଡ଼", "headquarters": "Nayagarh", "population": 962789, "coastal_zone": False, "vulnerability_tier": 2, "center_lat": 20.1200, "center_lng": 85.1000},
    {"code": "NUA", "name": "Nuapada", "name_odia": "ନୂଆପଡ଼ା", "headquarters": "Nuapada", "population": 610382, "coastal_zone": False, "vulnerability_tier": 1, "center_lat": 20.8300, "center_lng": 82.5200},
    {"code": "RAY", "name": "Rayagada", "name_odia": "ରାୟଗଡ଼ା", "headquarters": "Rayagada", "population": 967911, "coastal_zone": False, "vulnerability_tier": 2, "center_lat": 19.1700, "center_lng": 83.4100},
    {"code": "SAM", "name": "Sambalpur", "name_odia": "ସମ୍ବଲପୁର", "headquarters": "Sambalpur", "population": 1041099, "coastal_zone": False, "vulnerability_tier": 2, "center_lat": 21.4600, "center_lng": 83.9700},
    {"code": "SUB", "name": "Subarnapur", "name_odia": "ସୁବର୍ଣ୍ଣପୁର", "headquarters": "Sonepur", "population": 610183, "coastal_zone": False, "vulnerability_tier": 2, "center_lat": 20.8300, "center_lng": 83.9100},
    {"code": "SUN", "name": "Sundargarh", "name_odia": "ସୁନ୍ଦରଗଡ଼", "headquarters": "Sundargarh", "population": 2093437, "coastal_zone": False, "vulnerability_tier": 1, "center_lat": 22.1200, "center_lng": 84.0300},
    {"code": "KEN", "name": "Kendujhar", "name_odia": "କେନ୍ଦୁଝର", "headquarters": "Kendujhar", "population": 1801733, "coastal_zone": False, "vulnerability_tier": 2, "center_lat": 21.6300, "center_lng": 85.5800},
]


async def seed_database(db: AsyncSession):
    """Seed system with default reference data, admin users, and tactical forces."""
    # 1. Seed Districts
    dist_check = await db.execute(select(District).limit(1))
    if not dist_check.scalar_one_or_none():
        logger.info("Seeding 30 Odisha Districts...")
        for d_data in ODISHA_DISTRICTS_DATA:
            district = District(
                code=d_data["code"],
                name=d_data["name"],
                name_odia=d_data["name_odia"],
                headquarters=d_data["headquarters"],
                population=d_data["population"],
                coastal_zone=d_data["coastal_zone"],
                vulnerability_tier=d_data["vulnerability_tier"],
                center_lat=d_data["center_lat"],
                center_lng=d_data["center_lng"],
            )
            db.add(district)
        await db.flush()

        # Seed sample blocks for coastal districts
        knd_res = await db.execute(select(District).where(District.code == "KND"))
        knd = knd_res.scalar_one()
        for b_name in ["Rajnagar", "Mahakalapada", "Pattamundai", "Aul", "Kendrapara"]:
            db.add(Block(district_id=knd.id, name=b_name, gram_panchayats_count=28, is_coastal=True))
        await db.flush()

    # 2. Seed Default Administrative Role Users
    user_check = await db.execute(select(User).limit(1))
    if not user_check.scalar_one_or_none():
        logger.info("Seeding Default Administrative Users...")
        default_pwd = get_password_hash("Password@123")
        users_to_seed = [
            User(
                email="admin@aapadaops.odisha.gov.in",
                hashed_password=default_pwd,
                full_name="Dr. Manojit Jena (SRC/OSDMA)",
                role=UserRole.SUPER_ADMIN,
                phone_number="+91 94370 12345",
                badge_number="OSDMA-SA-01",
                is_active=True,
            ),
            User(
                email="collector.kendrapara@aapadaops.odisha.gov.in",
                hashed_password=default_pwd,
                full_name="Amrit Ruturaj, IAS (Collector)",
                role=UserRole.DISTRICT_COLLECTOR,
                phone_number="+91 94370 54321",
                jurisdiction_district="Kendrapara",
                badge_number="IAS-OD-2016",
                is_active=True,
            ),
            User(
                email="verification.officer@aapadaops.odisha.gov.in",
                hashed_password=default_pwd,
                full_name="Subhashree Mohanty, OAS",
                role=UserRole.INCIDENT_VERIFICATION_OFFICER,
                phone_number="+91 94371 99887",
                jurisdiction_district="Kendrapara",
                badge_number="OAS-IVO-08",
                is_active=True,
            ),
            User(
                email="response.coordinator@aapadaops.odisha.gov.in",
                hashed_password=default_pwd,
                full_name="Commander Bikram Keshari Ray",
                role=UserRole.RESPONSE_COORDINATOR,
                phone_number="+91 94372 11223",
                jurisdiction_district="Khordha",
                badge_number="EOC-RC-04",
                is_active=True,
            ),
            User(
                email="field.worker@aapadaops.odisha.gov.in",
                hashed_password=default_pwd,
                full_name="Havildar Dilip Patnaik",
                role=UserRole.FIELD_WORKER,
                phone_number="+91 94373 44556",
                jurisdiction_district="Kendrapara",
                badge_number="ODRAF-BN4-102",
                is_active=True,
            ),
            User(
                email="observer@aapadaops.odisha.gov.in",
                hashed_password=default_pwd,
                full_name="UNDP Disaster Risk Analyst",
                role=UserRole.OBSERVER,
                phone_number="+91 98110 55667",
                badge_number="OBS-EXT-02",
                is_active=True,
            ),
        ]
        db.add_all(users_to_seed)
        await db.flush()

    # 3. Seed Sample ODRN Resources
    res_check = await db.execute(select(Resource).limit(1))
    if not res_check.scalar_one_or_none():
        logger.info("Seeding ODRN Tactical Resources...")
        sample_resources = [
            Resource(
                code="ODRN-BOAT-KND-01",
                name="Inflatable Motor Power Boat (40 HP OBM)",
                category=ResourceType.POWER_BOAT,
                organization="ODRAF",
                district_name="Kendrapara",
                status=ResourceStatus.AVAILABLE,
                quantity=4,
                unit_of_measure="boats",
                latitude=20.5050,
                longitude=86.4250,
                contact_person="Sub-Inspector M. Behera",
                contact_phone="+91 94371 88881",
            ),
            Resource(
                code="ODRN-JCB-KND-02",
                name="Heavy Tracked Excavator (JCB 220)",
                category=ResourceType.JCB_EXCAVATOR,
                organization="Works Department",
                district_name="Kendrapara",
                status=ResourceStatus.AVAILABLE,
                quantity=2,
                unit_of_measure="machines",
                latitude=20.4980,
                longitude=86.4190,
                contact_person="Er. Prasant Das",
                contact_phone="+91 94371 88882",
            ),
            Resource(
                code="ODRN-PUMP-BHK-01",
                name="High-Capacity Dewatering Pump (500 GPM)",
                category=ResourceType.DEWATERING_PUMP,
                organization="Fire & Emergency Services",
                district_name="Bhadrak",
                status=ResourceStatus.AVAILABLE,
                quantity=6,
                unit_of_measure="pumps",
                latitude=21.0540,
                longitude=86.4950,
                contact_person="Station Officer K. Rout",
                contact_phone="+91 94371 88883",
            ),
        ]
        db.add_all(sample_resources)
        await db.flush()

    # 4. Seed Tactical Response Teams
    team_check = await db.execute(select(ResponseTeam).limit(1))
    if not team_check.scalar_one_or_none():
        logger.info("Seeding Response Teams...")
        teams = [
            ResponseTeam(
                code="NDRF-03-A",
                name="3rd Battalion NDRF (Team Alpha)",
                organization="NDRF",
                battalion="3rd Bn Mundali",
                team_lead_name="Inspector Rajesh Kumar",
                team_lead_phone="+91 94370 77701",
                total_personnel=45,
                current_district_name="Kendrapara",
                latitude=20.5100,
                longitude=86.4300,
                status=TeamStatus.STANDBY,
            ),
            ResponseTeam(
                code="ODRAF-04-B",
                name="4th ODRAF Unit Cuttack",
                organization="ODRAF",
                battalion="4th Bn Cuttack",
                team_lead_name="Deputy Subedar A. Tripathy",
                team_lead_phone="+91 94370 77702",
                total_personnel=30,
                current_district_name="Bhadrak",
                latitude=21.0600,
                longitude=86.5000,
                status=TeamStatus.STANDBY,
            ),
            ResponseTeam(
                code="FIRE-KND-01",
                name="Kendrapara Fire & Emergency Station",
                organization="FIRE_SERVICES",
                battalion="Station Kendrapara",
                team_lead_name="Station Officer B. Nayak",
                team_lead_phone="+91 94370 77703",
                total_personnel=18,
                current_district_name="Kendrapara",
                latitude=20.5000,
                longitude=86.4200,
                status=TeamStatus.STANDBY,
            ),
        ]
        db.add_all(teams)
        await db.flush()

    # 5. Seed Multipurpose Cyclone Shelters (MCS)
    shelter_check = await db.execute(select(CycloneShelter).limit(1))
    if not shelter_check.scalar_one_or_none():
        logger.info("Seeding Cyclone Shelters...")
        shelters = [
            CycloneShelter(
                code="MCS-KND-RAJ-01",
                name="Rajnagar Multipurpose Cyclone Shelter",
                district_name="Kendrapara",
                block_name="Rajnagar",
                village="Dangamal",
                capacity=800,
                current_occupancy=420,
                latitude=20.7380,
                longitude=86.8420,
                has_power_backup=True,
                generator_fuel_hours=48,
                drinking_water_days=6,
                has_medical_kit=True,
                caretaker_name="Pabitra Samal",
                caretaker_phone="+91 94380 11221",
                status=ShelterStatus.ACTIVE,
            ),
            CycloneShelter(
                code="MCS-BHK-DHM-01",
                name="Dhamra Port Coastal Cyclone Shelter",
                district_name="Bhadrak",
                block_name="Chandbali",
                village="Dhamra",
                capacity=1200,
                current_occupancy=750,
                latitude=20.8010,
                longitude=86.9530,
                has_power_backup=True,
                generator_fuel_hours=36,
                drinking_water_days=5,
                has_medical_kit=True,
                caretaker_name="Bibhuti Sethi",
                caretaker_phone="+91 94380 11222",
                status=ShelterStatus.ACTIVE,
            ),
        ]
        db.add_all(shelters)
        await db.flush()

    # 6. Seed Active SATARK Alert
    alert_check = await db.execute(select(AlertBroadcast).limit(1))
    if not alert_check.scalar_one_or_none():
        logger.info("Seeding SATARK Early Warning...")
        now = datetime.now(timezone.utc)
        alert = AlertBroadcast(
            alert_code="SATARK-RED-CYCLONE-01",
            severity=AlertSeverity.RED,
            hazard_type=AlertHazard.CYCLONE,
            headline="Severe Cyclonic Storm Warning for North Odisha Coastal Belt",
            advisory_body="IMD Doppler Radar Paradip confirms cyclonic storm intensifying with wind speeds of 110-120 kmph gusting to 135 kmph. Inundation alert issued for low-lying areas of Kendrapara, Bhadrak, and Balasore. Evacuation to nearest Multipurpose Cyclone Shelters underway.",
            affected_districts_json='["Kendrapara", "Bhadrak", "Balasore", "Jagatsinghpur"]',
            source="IMD_OSDMA_SATARK",
            issued_at=now - timedelta(hours=2),
            valid_until=now + timedelta(hours=36),
            is_active=True,
        )
        db.add(alert)
        await db.flush()

    # 7. Seed Initial Operational Incidents
    inc_check = await db.execute(select(Incident).limit(1))
    if not inc_check.scalar_one_or_none():
        logger.info("Seeding Initial Operational Incidents...")
        inc1 = Incident(
            incident_code="INC-OD-2026-0891",
            title="Brahmani River Embankment Breach at Rajnagar",
            description="Major breach of 15 meters reported in saline embankment of Brahmani river near Dangamal village. Seawater inundating agricultural fields and threatening 120 households. Urgent sandbagging and rescue boats needed.",
            category=IncidentCategory.EMBANKMENT_BREACH,
            reported_severity=IncidentSeverity.CRITICAL,
            verified_priority=IncidentSeverity.CRITICAL,
            status=IncidentStatus.VERIFIED,
            district_name="Kendrapara",
            block_name="Rajnagar",
            village_name="Dangamal",
            latitude=20.7380,
            longitude=86.8420,
            reporter_name="Sarpanch Biswajit Tarai",
            reporter_phone="+91 94371 22334",
            reporter_role="PANCHAYAT_REPRESENTATIVE",
            is_verified=True,
            ai_confidence_score=0.94,
            ai_raw_classification="AI Advisory: Classified as EMBANKMENT_BREACH with CRITICAL urgency (94% confidence).",
            ai_urgency_score=0.96,
            estimated_affected_people=450,
            casualties_reported=0,
            stranded_count=85,
        )
        inc2 = Incident(
            incident_code="INC-OD-2026-0892",
            title="Tree Fall Blocking NH-16 near Chandikhole",
            description="Two massive banyan trees uprooted due to 90 kmph squall winds, blocking both lanes of NH-16 towards Balasore. Emergency relief convoys currently stalled.",
            category=IncidentCategory.TREE_FALL,
            reported_severity=IncidentSeverity.HIGH,
            status=IncidentStatus.NEEDS_VERIFICATION,
            district_name="Jajpur",
            block_name="Dharmasala",
            village_name="Chandikhole",
            latitude=20.7020,
            longitude=86.1540,
            reporter_name="Traffic Patrol Unit 3",
            reporter_phone="+91 94372 33445",
            reporter_role="OFFICIAL",
            is_verified=False,
            ai_confidence_score=0.88,
            ai_raw_classification="AI Advisory: Classified as TREE_FALL with HIGH urgency on critical transport corridor.",
            ai_urgency_score=0.75,
            estimated_affected_people=100,
            casualties_reported=0,
            stranded_count=0,
        )
        db.add_all([inc1, inc2])

    await db.commit()
    logger.info("Database seeding successfully completed.")

