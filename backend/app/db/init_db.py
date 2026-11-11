"""AapadaOps Database Seeding and Initial Reference Data."""

import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.alert import AlertBroadcast, AlertHazard, AlertSeverity
from app.models.district import Block, District
from app.models.duplicate import DuplicateCluster, ClusterStatus
from app.models.incident import (
    Incident,
    IncidentCategory,
    IncidentSeverity,
    IncidentStatus,
)
from app.models.resource import Resource, ResourceStatus, ResourceType
from app.models.shelter import CycloneShelter, ShelterStatus
from app.models.task import Task, TaskStatus
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
                email="director@osdma.gov.in",
                hashed_password=default_pwd,
                full_name="Sri Pradeep Kumar Jena, IAS",
                role=UserRole.SUPER_ADMIN,
                phone_number="+91 94370 11111",
                badge_number="OSDMA-DG-01",
                is_active=True,
            ),
            User(
                email="collector.puri@nic.in",
                hashed_password=default_pwd,
                full_name="Dr. Siddharth Shankar Das, IAS",
                role=UserRole.DISTRICT_COLLECTOR,
                jurisdiction_district="Puri",
                phone_number="+91 94370 11223",
                badge_number="IAS-PURI-01",
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
                email="tahasildar.krushnaprasad@nic.in",
                hashed_password=default_pwd,
                full_name="Smt. Ananya Mishra, OAS",
                role=UserRole.INCIDENT_VERIFICATION_OFFICER,
                jurisdiction_district="Puri",
                phone_number="+91 94370 22334",
                badge_number="OAS-PURI-03",
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
                email="bdo.kakatpur@nic.in",
                hashed_password=default_pwd,
                full_name="Sri Rajesh Mohanty, OAS",
                role=UserRole.RESPONSE_COORDINATOR,
                jurisdiction_district="Puri",
                phone_number="+91 94370 33445",
                badge_number="BDO-KAK-02",
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
                email="odraf.unit03@odisha.gov.in",
                hashed_password=default_pwd,
                full_name="Inspector B. K. Nayak",
                role=UserRole.FIELD_WORKER,
                jurisdiction_district="Puri",
                phone_number="+91 94370 44556",
                badge_number="ODRAF-BN3-01",
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
                email="ndma.liaison@nic.in",
                hashed_password=default_pwd,
                full_name="Col. R. S. Rathore",
                role=UserRole.OBSERVER,
                phone_number="+91 98110 55667",
                badge_number="NDMA-LN-01",
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
            User(
                email="citizen@aapadaops.gov.in",
                hashed_password=default_pwd,
                full_name="Public Citizen Reporter",
                role=UserRole.CITIZEN_REPORTER,
                phone_number="+91 94379 99999",
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
        inc3 = Incident(
            incident_code="INC-OD-2026-0893",
            title="Sea Water Inundation in Krushnaprasad Island Sector",
            description="High tidal surge caused 4 feet waterlogging in 3 hamlets. 45 persons including elderly and children stranded on temple roof without food or potable water.",
            category=IncidentCategory.FLOOD,
            reported_severity=IncidentSeverity.CRITICAL,
            status=IncidentStatus.SUBMITTED,
            district_name="Puri",
            block_name="Krushnaprasad",
            village_name="Satapada",
            latitude=19.6730,
            longitude=85.4320,
            reporter_name="Debabrata Jena (Gram Sathi)",
            reporter_phone="+91 94370 22119",
            reporter_role="CITIZEN",
            is_verified=False,
            ai_confidence_score=0.91,
            ai_raw_classification="AI Advisory: Rapid inundation with isolated island population. Immediate rescue boat required.",
            ai_urgency_score=0.95,
            estimated_affected_people=180,
            casualties_reported=0,
            stranded_count=45,
        )
        inc4 = Incident(
            incident_code="INC-OD-2026-0894",
            title="Hospital Emergency Power Failure at Puri DHH",
            description="Substation feeder tripped during squall; primary generator fuel contaminated. ICU and neonatal wing require immediate mobile diesel generator backup.",
            category=IncidentCategory.INFRASTRUCTURE_DAMAGE,
            reported_severity=IncidentSeverity.CRITICAL,
            status=IncidentStatus.NEEDS_VERIFICATION,
            district_name="Puri",
            block_name="Puri Sadar",
            village_name="Puri Town",
            latitude=19.8130,
            longitude=85.8280,
            reporter_name="Medical Officer on Duty",
            reporter_phone="+91 94370 44332",
            reporter_role="OFFICIAL",
            is_verified=False,
            ai_confidence_score=0.97,
            ai_raw_classification="AI Advisory: Critical healthcare lifeline at risk. Urgent 125kVA Genset dispatch.",
            ai_urgency_score=0.98,
            estimated_affected_people=60,
            casualties_reported=0,
            stranded_count=0,
        )
        inc5 = Incident(
            incident_code="INC-OD-2026-0895",
            title="Saline Bundh Washout near Rajnagar Dangamal Primary School",
            description="Flood water entering school premises where 60 villagers took informal shelter. Water rising to 3.5 feet. Need immediate boats.",
            category=IncidentCategory.EMBANKMENT_BREACH,
            reported_severity=IncidentSeverity.CRITICAL,
            status=IncidentStatus.NEEDS_VERIFICATION,
            district_name="Kendrapara",
            block_name="Rajnagar",
            village_name="Dangamal",
            latitude=20.7395,
            longitude=86.8435,
            reporter_name="Ward Member K. Behera",
            reporter_phone="+91 94371 66778",
            reporter_role="CITIZEN",
            is_verified=False,
            ai_confidence_score=0.93,
            ai_raw_classification="AI Advisory: Potential duplicate of INC-OD-2026-0891 (220m distance, same hazard).",
            ai_urgency_score=0.93,
            estimated_affected_people=150,
            casualties_reported=0,
            stranded_count=60,
        )
        inc6 = Incident(
            incident_code="INC-OD-2026-0896",
            title="Mahanadi River Islet Stranded Villagers",
            description="12 farmers cut off on river sandbar near Athagarh as river discharge increased to 8.5 lakh cusecs from Hirakud reservoir.",
            category=IncidentCategory.FLOOD,
            reported_severity=IncidentSeverity.HIGH,
            verified_priority=IncidentSeverity.HIGH,
            status=IncidentStatus.ASSIGNED,
            district_name="Cuttack",
            block_name="Athagarh",
            village_name="Bhattarika",
            latitude=20.5280,
            longitude=85.3400,
            reporter_name="Tahasildar Athagarh",
            reporter_phone="+91 94373 55667",
            reporter_role="OFFICIAL",
            is_verified=True,
            ai_confidence_score=0.89,
            ai_raw_classification="AI Advisory: Rapid current; motorized rescue craft dispatched.",
            ai_urgency_score=0.86,
            estimated_affected_people=12,
            casualties_reported=0,
            stranded_count=12,
        )
        inc7 = Incident(
            incident_code="INC-OD-2026-0897",
            title="Deep Sea Trawler Engine Breakdown off Dhamra Mouth",
            description="Mechanized fishing trawler 'Maa Mangala' with 14 crew members disabled 6 nautical miles off Dhamra port. Drift towards sandbars.",
            category=IncidentCategory.CYCLONE,
            reported_severity=IncidentSeverity.CRITICAL,
            verified_priority=IncidentSeverity.CRITICAL,
            status=IncidentStatus.IN_PROGRESS,
            district_name="Bhadrak",
            block_name="Chandbali",
            village_name="Dhamra",
            latitude=20.7950,
            longitude=87.0100,
            reporter_name="Coastal Marine Police Dhamra",
            reporter_phone="+91 94374 11998",
            reporter_role="OFFICIAL",
            is_verified=True,
            ai_confidence_score=0.95,
            ai_raw_classification="AI Advisory: Marine rescue operation active. Coast Guard / Marine Police coordinated.",
            ai_urgency_score=0.94,
            estimated_affected_people=14,
            casualties_reported=0,
            stranded_count=14,
        )
        inc8 = Incident(
            incident_code="INC-OD-2026-0898",
            title="Urban Waterlogging at Remuna Golei Road",
            description="Temporary water accumulation of 1.5 feet drained using municipal dewatering pumps.",
            category=IncidentCategory.WATERLOGGING,
            reported_severity=IncidentSeverity.MEDIUM,
            verified_priority=IncidentSeverity.MEDIUM,
            status=IncidentStatus.RESOLVED,
            district_name="Balasore",
            block_name="Remuna",
            village_name="Remuna",
            latitude=21.5120,
            longitude=86.8740,
            reporter_name="Municipal Sanitary Officer",
            reporter_phone="+91 94375 22331",
            reporter_role="OFFICIAL",
            is_verified=True,
            ai_confidence_score=0.82,
            ai_urgency_score=0.45,
            estimated_affected_people=50,
            casualties_reported=0,
            stranded_count=0,
        )
        inc9 = Incident(
            incident_code="INC-OD-2026-0899",
            title="Culvert Scour and Sandbagging at Chatrapur",
            description="Sandbag barrier constructed along rural road culvert. Water receded and traffic restored.",
            category=IncidentCategory.FLOOD,
            reported_severity=IncidentSeverity.LOW,
            verified_priority=IncidentSeverity.LOW,
            status=IncidentStatus.CLOSED,
            district_name="Ganjam",
            block_name="Chatrapur",
            village_name="Chatrapur",
            latitude=19.3550,
            longitude=85.0120,
            reporter_name="Junior Engineer RD Dept",
            reporter_phone="+91 94376 33442",
            reporter_role="OFFICIAL",
            is_verified=True,
            ai_confidence_score=0.80,
            ai_urgency_score=0.30,
            estimated_affected_people=20,
            casualties_reported=0,
            stranded_count=0,
        )
        db.add_all([inc1, inc2, inc3, inc4, inc5, inc6, inc7, inc8, inc9])
        await db.flush()

        # Seed Duplicate Cluster for inc5 -> inc1
        dup_cluster = DuplicateCluster(
            primary_incident_id=inc1.id,
            status=ClusterStatus.PENDING_REVIEW,
            spatial_radius_meters=220.0,
            confidence_score=0.89,
            cluster_summary="2 reports submitted within 220m in Rajnagar regarding Brahmani River breach and flooded school.",
            duplicate_count=1,
        )
        db.add(dup_cluster)
        await db.flush()

        inc5.is_duplicate = True
        inc5.duplicate_of_id = inc1.id
        inc5.duplicate_cluster_id = dup_cluster.id

        # Seed Tactical Tasks
        # Find NDRF and ODRAF teams for task assignments
        ndrf_res = await db.execute(select(ResponseTeam).where(ResponseTeam.code == "NDRF-03-A"))
        ndrf_team = ndrf_res.scalar_one_or_none()

        odraf_res = await db.execute(select(ResponseTeam).where(ResponseTeam.code == "ODRAF-04-B"))
        odraf_team = odraf_res.scalar_one_or_none()

        now_utc = datetime.now(timezone.utc)
        task1 = Task(
            task_code="OD-TSK-401",
            incident_id=inc6.id,
            assigned_team_id=odraf_team.id if odraf_team else None,
            title="Deploy Motorized Inflatable Rescue Boats to evacuate 12 stranded on Bhattarika islet",
            description="Mahanadi flood surge. Rapid water flow requires high-power outboard motors. Evacuate to elevated temple compound.",
            priority="HIGH",
            sla_hours=3,
            deadline=now_utc + timedelta(hours=3),
            status=TaskStatus.ASSIGNED,
            target_village="Bhattarika",
            target_latitude=20.5280,
            target_longitude=85.3400,
            dispatch_notes="Dispatched from 4th ODRAF Unit Cuttack via NH-55.",
        )
        task2 = Task(
            task_code="OD-TSK-402",
            incident_id=inc7.id,
            assigned_team_id=ndrf_team.id if ndrf_team else None,
            title="Marine Search & Rescue for disabled trawler Maa Mangala off Dhamra",
            description="Tow vessel and 14 crew safely to Dhamra port jetty before swell exceeds 3.5 meters.",
            priority="CRITICAL",
            sla_hours=2,
            deadline=now_utc + timedelta(hours=2),
            status=TaskStatus.IN_PROGRESS,
            target_village="Dhamra Port",
            target_latitude=20.7950,
            target_longitude=87.0100,
            dispatch_notes="Team deployed in rigid hull inflatable boat with Marine Police interceptor.",
        )
        task3 = Task(
            task_code="OD-TSK-403",
            incident_id=inc8.id,
            title="Install and operate 500 GPM dewatering pump at Remuna Golei",
            description="Drain stormwater to prevent highway inundation.",
            priority="MEDIUM",
            sla_hours=4,
            status=TaskStatus.COMPLETED,
            target_village="Remuna",
            target_latitude=21.5120,
            target_longitude=86.8740,
            resolution_notes="Water cleared completely. Traffic flow normalized.",
            completed_at=now_utc - timedelta(hours=4),
        )
        db.add_all([task1, task2, task3])

    await db.commit()
    logger.info("Database seeding successfully completed.")

