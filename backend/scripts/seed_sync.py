"""Synchronous, rock-solid SQLite seed script for AapadaOps development database.
Guarantees instantaneous execution on Windows without async loop shutdown deadlocks.
"""

import json
import sqlite3
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
import bcrypt

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

db_path = backend_dir / "aapadaops_dev.db"
print(f"Connecting to: {db_path}...")

con = sqlite3.connect(db_path)
cur = con.cursor()

def get_hash(pwd: str) -> str:
    pwd_bytes = pwd.encode("utf-8")[:72]
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")

default_pwd_hash = get_hash("Password@123")
now = datetime.now(timezone.utc).isoformat()
now_dt = datetime.now(timezone.utc)

# 1. Seed Districts
cur.execute("SELECT COUNT(*) FROM districts")
if cur.fetchone()[0] == 0:
    print("Seeding districts...")
    from app.db.init_db import ODISHA_DISTRICTS_DATA
    for d in ODISHA_DISTRICTS_DATA:
        cur.execute(
            """INSERT INTO districts (id, code, name, name_odia, headquarters, population, coastal_zone, vulnerability_tier, center_lat, center_lng, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (str(uuid.uuid4()), d["code"], d["name"], d["name_odia"], d["headquarters"], d["population"], d["coastal_zone"], d["vulnerability_tier"], d["center_lat"], d["center_lng"], now, now)
        )
    con.commit()
    print("Districts seeded.")

# 2. Seed Users / Personas
cur.execute("SELECT COUNT(*) FROM users")
if cur.fetchone()[0] == 0:
    print("Seeding personas...")
    users = [
        ("admin@aapadaops.odisha.gov.in", "Dr. Manojit Jena (SRC/OSDMA)", "SUPER_ADMIN", "+91 94370 12345", None, "OSDMA-SA-01"),
        ("director@osdma.gov.in", "Sri Pradeep Kumar Jena, IAS", "SUPER_ADMIN", "+91 94370 11111", None, "OSDMA-DG-01"),
        ("collector.puri@nic.in", "Dr. Siddharth Shankar Das, IAS", "DISTRICT_COLLECTOR", "+91 94370 11223", "Puri", "IAS-PURI-01"),
        ("collector.kendrapara@aapadaops.odisha.gov.in", "Amrit Ruturaj, IAS (Collector)", "DISTRICT_COLLECTOR", "+91 94370 54321", "Kendrapara", "IAS-OD-2016"),
        ("tahasildar.krushnaprasad@nic.in", "Smt. Ananya Mishra, OAS", "INCIDENT_VERIFICATION_OFFICER", "+91 94370 22334", "Puri", "OAS-PURI-03"),
        ("verification.officer@aapadaops.odisha.gov.in", "Subhashree Mohanty, OAS", "INCIDENT_VERIFICATION_OFFICER", "+91 94371 99887", "Kendrapara", "OAS-IVO-08"),
        ("bdo.kakatpur@nic.in", "Sri Rajesh Mohanty, OAS", "RESPONSE_COORDINATOR", "+91 94370 33445", "Puri", "BDO-KAK-02"),
        ("response.coordinator@aapadaops.odisha.gov.in", "Commander Bikram Keshari Ray", "RESPONSE_COORDINATOR", "+91 94372 11223", "Khordha", "EOC-RC-04"),
        ("odraf.unit03@odisha.gov.in", "Inspector B. K. Nayak", "FIELD_WORKER", "+91 94370 44556", "Puri", "ODRAF-BN3-01"),
        ("field.worker@aapadaops.odisha.gov.in", "Havildar Dilip Patnaik", "FIELD_WORKER", "+91 94373 44556", "Kendrapara", "ODRAF-BN4-102"),
        ("ndma.liaison@nic.in", "Col. R. S. Rathore", "OBSERVER", "+91 98110 55667", None, "NDMA-LN-01"),
        ("observer@aapadaops.odisha.gov.in", "UNDP Disaster Risk Analyst", "OBSERVER", "+91 98110 55667", None, "OBS-EXT-02"),
        ("citizen@aapadaops.gov.in", "Public Citizen Reporter", "CITIZEN_REPORTER", "+91 94379 99999", None, "CIT-01"),
    ]
    for email, name, role, phone, district, badge in users:
        cur.execute(
            """INSERT INTO users (id, email, hashed_password, full_name, role, phone_number, is_active, jurisdiction_district, badge_number, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?)""",
            (str(uuid.uuid4()), email, default_pwd_hash, name, role, phone, district, badge, now, now)
        )
    con.commit()
    print("Users seeded.")

# 3. Seed Tactical Response Teams
cur.execute("SELECT COUNT(*) FROM response_teams")
if cur.fetchone()[0] == 0:
    print("Seeding tactical response teams...")
    teams = [
        ("NDRF-03-A", "3rd Battalion NDRF (Team Alpha)", "NDRF", "3rd Bn Mundali", "Inspector Rajesh Kumar", "+91 94370 77701", 45, "Kendrapara", 20.5100, 86.4300, "STANDBY", "WATER_RESCUE", 50),
        ("ODRAF-04-B", "4th ODRAF Unit Cuttack", "ODRAF", "4th Bn Cuttack", "Deputy Subedar A. Tripathy", "+91 94370 77702", 30, "Bhadrak", 21.0600, 86.5000, "STANDBY", "WATER_RESCUE", 35),
        ("FIRE-KND-01", "Kendrapara Fire & Emergency Station", "FIRE_SERVICES", "Station Kendrapara", "Station Officer B. Nayak", "+91 94370 77703", 18, "Kendrapara", 20.5000, 86.4200, "STANDBY", "STRUCTURAL_COLLAPSE", 20),
        ("ODRAF-03-PUR", "3rd ODRAF Special Unit Puri", "ODRAF", "3rd Bn Puri", "Inspector B. K. Nayak", "+91 94370 44556", 28, "Puri", 19.8140, 85.8320, "STANDBY", "WATER_RESCUE", 40),
        ("FIRE-PUR-01", "Puri Central Fire Station", "FIRE_SERVICES", "Station Puri", "Station Officer D. Mishra", "+91 94370 44778", 22, "Puri", 19.8180, 85.8350, "STANDBY", "WATER_RESCUE", 25),
    ]
    for code, name, org, bn, lead, phone, count, dist, lat, lng, st, spec, cap in teams:
        cur.execute(
            """INSERT INTO response_teams (id, code, name, organization, battalion, team_lead_name, team_lead_phone, total_personnel, current_district_name, latitude, longitude, status, specialization, rescue_capacity_persons, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (str(uuid.uuid4()), code, name, org, bn, lead, phone, count, dist, lat, lng, st, spec, cap, now, now)
        )
    con.commit()
    print("Response teams seeded.")

# 4. Seed ODRN Resources
cur.execute("SELECT COUNT(*) FROM resources")
if cur.fetchone()[0] == 0:
    print("Seeding resources...")
    resources = [
        ("ODRN-BOAT-KND-01", "Inflatable Motor Power Boat (40 HP OBM)", "POWER_BOAT", "ODRAF", "Kendrapara", "AVAILABLE", 4, "boats", 20.5050, 86.4250, "Sub-Inspector M. Behera", "+91 94371 88881", 12.0, "PERSONS"),
        ("ODRN-JCB-KND-02", "Heavy Tracked Excavator (JCB 220)", "JCB_EXCAVATOR", "Works Department", "Kendrapara", "AVAILABLE", 2, "machines", 20.4980, 86.4190, "Er. Prasant Das", "+91 94371 88882", 1.0, "UNIT"),
        ("ODRN-PUMP-BHK-01", "High-Capacity Dewatering Pump (500 GPM)", "DEWATERING_PUMP", "Fire & Emergency Services", "Bhadrak", "AVAILABLE", 6, "pumps", 21.0540, 86.4950, "Station Officer K. Rout", "+91 94371 88883", 500.0, "GPM"),
        ("ODRN-BOAT-PUR-01", "Rigid Inflatable Rescue Craft (50 HP)", "POWER_BOAT", "ODRAF", "Puri", "AVAILABLE", 3, "boats", 19.8150, 85.8300, "Havildar S. Pradhan", "+91 94370 88884", 15.0, "PERSONS"),
        ("ODRN-GEN-PUR-02", "Mobile Diesel Generator 125 kVA", "GENERATOR", "Energy Department", "Puri", "AVAILABLE", 2, "units", 19.8200, 85.8340, "Er. A. Mohapatra", "+91 94370 88885", 125.0, "KVA"),
    ]
    for code, name, cat, org, dist, st, qty, uom, lat, lng, contact, phone, cap, cap_u in resources:
        cur.execute(
            """INSERT INTO resources (id, code, name, category, organization, district_name, status, quantity, unit_of_measure, latitude, longitude, contact_person, contact_phone, capacity, capacity_unit, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (str(uuid.uuid4()), code, name, cat, org, dist, st, qty, uom, lat, lng, contact, phone, cap, cap_u, now, now)
        )
    con.commit()
    print("Resources seeded.")

# 5. Seed Cyclone Shelters
cur.execute("SELECT COUNT(*) FROM cyclone_shelters")
if cur.fetchone()[0] == 0:
    print("Seeding shelters...")
    shelters = [
        ("MCS-KND-RAJ-01", "Rajnagar Multipurpose Cyclone Shelter", "Kendrapara", "Rajnagar", "Dangamal", 800, 420, 20.7380, 86.8420, 1, 48, 6, 1, "Pabitra Samal", "+91 94380 11221", "ACTIVE"),
        ("MCS-BHK-DHM-01", "Dhamra Port Coastal Cyclone Shelter", "Bhadrak", "Chandbali", "Dhamra", 1200, 750, 20.8010, 86.9530, 1, 36, 5, 1, "Bibhuti Sethi", "+91 94380 11222", "ACTIVE"),
        ("MCS-PUR-KRP-01", "Krushnaprasad Island Cyclone Shelter", "Puri", "Krushnaprasad", "Satapada", 900, 310, 19.6750, 85.4350, 1, 48, 7, 1, "Kailash Barik", "+91 94380 11223", "ACTIVE"),
    ]
    for code, name, dist, block, vill, cap, occ, lat, lng, pwr, fuel, water, med, ct_name, ct_phone, st in shelters:
        cur.execute(
            """INSERT INTO cyclone_shelters (id, code, name, district_name, block_name, village, capacity, current_occupancy, latitude, longitude, has_power_backup, generator_fuel_hours, drinking_water_days, has_medical_kit, caretaker_name, caretaker_phone, status, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (str(uuid.uuid4()), code, name, dist, block, vill, cap, occ, lat, lng, pwr, fuel, water, med, ct_name, ct_phone, st, now, now)
        )
    con.commit()
    print("Shelters seeded.")

# 6. Seed Alert Broadcast
cur.execute("SELECT COUNT(*) FROM alert_broadcasts")
if cur.fetchone()[0] == 0:
    print("Seeding alerts...")
    cur.execute(
        """INSERT INTO alert_broadcasts (id, alert_code, severity, hazard_type, headline, advisory_body, affected_districts_json, source, issued_at, valid_until, is_active, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)""",
        (str(uuid.uuid4()), "SATARK-RED-CYCLONE-01", "RED", "CYCLONE", "Severe Cyclonic Storm Warning for North Odisha Coastal Belt", "IMD Doppler Radar Paradip confirms cyclonic storm intensifying with wind speeds of 110-120 kmph. Inundation alert issued for Kendrapara, Bhadrak, and Balasore.", '["Kendrapara", "Bhadrak", "Balasore", "Puri"]', "IMD_OSDMA_SATARK", (now_dt - timedelta(hours=2)).isoformat(), (now_dt + timedelta(hours=36)).isoformat(), now, now)
    )
    con.commit()
    print("Alerts seeded.")

# 7. Seed Incidents & Duplicate Cluster & Tasks
cur.execute("SELECT COUNT(*) FROM incidents")
if cur.fetchone()[0] == 0:
    print("Seeding incidents across full lifecycle...")
    inc_ids = {}
    incidents = [
        ("INC-OD-2026-0891", "Brahmani River Embankment Breach at Rajnagar", "Major breach of 15 meters reported in saline embankment of Brahmani river near Dangamal village. Seawater inundating agricultural fields and threatening 120 households. Urgent sandbagging and rescue boats needed.", "EMBANKMENT_BREACH", "CRITICAL", "CRITICAL", "VERIFIED", "Kendrapara", "Rajnagar", "Dangamal", 20.7380, 86.8420, "Sarpanch Biswajit Tarai", "+91 94371 22334", "PANCHAYAT_REPRESENTATIVE", 1, 0.94, "AI Advisory: Classified as EMBANKMENT_BREACH with CRITICAL urgency.", 0.96, 450, 0, 85),
        ("INC-OD-2026-0892", "Tree Fall Blocking NH-16 near Chandikhole", "Two massive banyan trees uprooted due to 90 kmph squall winds, blocking both lanes of NH-16 towards Balasore. Emergency relief convoys currently stalled.", "TREE_FALL", "HIGH", None, "NEEDS_VERIFICATION", "Jajpur", "Dharmasala", "Chandikhole", 20.7020, 86.1540, "Traffic Patrol Unit 3", "+91 94372 33445", "OFFICIAL", 0, 0.88, "AI Advisory: Classified as TREE_FALL on critical transport corridor.", 0.75, 100, 0, 0),
        ("INC-OD-2026-0893", "Sea Water Inundation in Krushnaprasad Island Sector", "High tidal surge caused 4 feet waterlogging in 3 hamlets. 45 persons including elderly and children stranded on temple roof without food or potable water.", "FLOOD", "CRITICAL", None, "SUBMITTED", "Puri", "Krushnaprasad", "Satapada", 19.6730, 85.4320, "Debabrata Jena (Gram Sathi)", "+91 94370 22119", "CITIZEN", 0, 0.91, "AI Advisory: Rapid inundation with isolated island population. Immediate rescue boat required.", 0.95, 180, 0, 45),
        ("INC-OD-2026-0894", "Hospital Emergency Power Failure at Puri DHH", "Substation feeder tripped during squall; primary generator fuel contaminated. ICU and neonatal wing require immediate mobile diesel generator backup.", "INFRASTRUCTURE_DAMAGE", "CRITICAL", None, "NEEDS_VERIFICATION", "Puri", "Puri Sadar", "Puri Town", 19.8130, 85.8280, "Medical Officer on Duty", "+91 94370 44332", "OFFICIAL", 0, 0.97, "AI Advisory: Critical healthcare lifeline at risk. Urgent 125kVA Genset dispatch.", 0.98, 60, 0, 0),
        ("INC-OD-2026-0895", "Saline Bundh Washout near Rajnagar Dangamal Primary School", "Flood water entering school premises where 60 villagers took informal shelter. Water rising to 3.5 feet. Need immediate boats.", "EMBANKMENT_BREACH", "CRITICAL", None, "NEEDS_VERIFICATION", "Kendrapara", "Rajnagar", "Dangamal", 20.7395, 86.8435, "Ward Member K. Behera", "+91 94371 66778", "CITIZEN", 0, 0.93, "AI Advisory: Potential duplicate of INC-OD-2026-0891 (220m distance, same hazard).", 0.93, 150, 0, 60),
        ("INC-OD-2026-0896", "Mahanadi River Islet Stranded Villagers", "12 farmers cut off on river sandbar near Athagarh as river discharge increased to 8.5 lakh cusecs from Hirakud reservoir.", "FLOOD", "HIGH", "HIGH", "ASSIGNED", "Cuttack", "Athagarh", "Bhattarika", 20.5280, 85.3400, "Tahasildar Athagarh", "+91 94373 55667", "OFFICIAL", 1, 0.89, "AI Advisory: Rapid current; motorized rescue craft dispatched.", 0.86, 12, 0, 12),
        ("INC-OD-2026-0897", "Deep Sea Trawler Engine Breakdown off Dhamra Mouth", "Mechanized fishing trawler 'Maa Mangala' with 14 crew members disabled 6 nautical miles off Dhamra port. Drift towards sandbars.", "CYCLONE", "CRITICAL", "CRITICAL", "IN_PROGRESS", "Bhadrak", "Chandbali", "Dhamra", 20.7950, 87.0100, "Coastal Marine Police Dhamra", "+91 94374 11998", "OFFICIAL", 1, 0.95, "AI Advisory: Marine rescue operation active. Coast Guard / Marine Police coordinated.", 0.94, 14, 0, 14),
        ("INC-OD-2026-0898", "Urban Waterlogging at Remuna Golei Road", "Temporary water accumulation of 1.5 feet drained using municipal dewatering pumps.", "WATERLOGGING", "MEDIUM", "MEDIUM", "RESOLVED", "Balasore", "Remuna", "Remuna", 21.5120, 86.8740, "Municipal Sanitary Officer", "+91 94375 22331", "OFFICIAL", 1, 0.82, "AI Advisory: Routine municipal drainage resolution.", 0.45, 50, 0, 0),
        ("INC-OD-2026-0899", "Culvert Scour and Sandbagging at Chatrapur", "Sandbag barrier constructed along rural road culvert. Water receded and traffic restored.", "FLOOD", "LOW", "LOW", "CLOSED", "Ganjam", "Chatrapur", "Chatrapur", 19.3550, 85.0120, "Junior Engineer RD Dept", "+91 94376 33442", "OFFICIAL", 1, 0.80, "AI Advisory: Localized scouring mitigated.", 0.30, 20, 0, 0),
    ]
    for code, title, desc, cat, rep_sev, ver_pri, st, dist, block, vill, lat, lng, rep_name, rep_phone, rep_role, is_v, ai_conf, ai_class, ai_urg, aff, cas, strd in incidents:
        inc_id = str(uuid.uuid4())
        inc_ids[code] = inc_id
        cur.execute(
            """INSERT INTO incidents (id, incident_code, title, description, category, reported_severity, verified_priority, status, district_name, block_name, village_name, latitude, longitude, reporter_name, reporter_phone, reporter_role, is_verified, ai_confidence_score, ai_raw_classification, ai_urgency_score, estimated_affected_people, casualties_reported, stranded_count, is_duplicate, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?)""",
            (inc_id, code, title, desc, cat, rep_sev, ver_pri, st, dist, block, vill, lat, lng, rep_name, rep_phone, rep_role, is_v, ai_conf, ai_class, ai_urg, aff, cas, strd, now, now)
        )
    con.commit()
    print("Incidents seeded.")

    # Duplicate cluster for 0895 -> 0891
    p_id = inc_ids["INC-OD-2026-0891"]
    c_id = inc_ids["INC-OD-2026-0895"]
    cluster_id = str(uuid.uuid4())
    cur.execute(
        """INSERT INTO duplicate_clusters (id, primary_incident_id, status, spatial_radius_meters, confidence_score, cluster_summary, duplicate_count, created_at, updated_at)
           VALUES (?, ?, 'PENDING_REVIEW', 220.0, 0.89, '2 reports submitted within 220m in Rajnagar regarding Brahmani River breach and flooded school.', 1, ?, ?)""",
        (cluster_id, p_id, now, now)
    )
    cur.execute("UPDATE incidents SET is_duplicate = 1, duplicate_of_id = ?, duplicate_cluster_id = ? WHERE id = ?", (p_id, cluster_id, c_id))
    con.commit()
    print("Duplicate cluster linked.")

    # Tasks
    cur.execute("SELECT id FROM response_teams WHERE code = 'ODRAF-04-B'")
    odraf_id = cur.fetchone()[0]
    cur.execute("SELECT id FROM response_teams WHERE code = 'NDRF-03-A'")
    ndrf_id = cur.fetchone()[0]

    cur.execute(
        """INSERT INTO tasks (id, task_code, incident_id, assigned_team_id, title, description, priority, sla_hours, deadline, status, target_village, target_latitude, target_longitude, dispatch_notes, created_at, updated_at)
           VALUES (?, 'OD-TSK-401', ?, ?, 'Deploy Motorized Inflatable Rescue Boats to evacuate 12 stranded on Bhattarika islet', 'Mahanadi flood surge. High-power motors required.', 'HIGH', 3, ?, 'ASSIGNED', 'Bhattarika', 20.5280, 85.3400, 'Dispatched from 4th ODRAF Unit Cuttack.', ?, ?)""",
        (str(uuid.uuid4()), inc_ids["INC-OD-2026-0896"], odraf_id, (now_dt + timedelta(hours=3)).isoformat(), now, now)
    )
    cur.execute(
        """INSERT INTO tasks (id, task_code, incident_id, assigned_team_id, title, description, priority, sla_hours, deadline, status, target_village, target_latitude, target_longitude, dispatch_notes, created_at, updated_at)
           VALUES (?, 'OD-TSK-402', ?, ?, 'Marine Search & Rescue for disabled trawler Maa Mangala off Dhamra', 'Tow vessel and 14 crew safely to Dhamra port jetty.', 'CRITICAL', 2, ?, 'IN_PROGRESS', 'Dhamra Port', 20.7950, 87.0100, 'Team deployed in rigid hull inflatable boat.', ?, ?)""",
        (str(uuid.uuid4()), inc_ids["INC-OD-2026-0897"], ndrf_id, (now_dt + timedelta(hours=2)).isoformat(), now, now)
    )
    cur.execute(
        """INSERT INTO tasks (id, task_code, incident_id, title, description, priority, sla_hours, status, target_village, target_latitude, target_longitude, resolution_notes, completed_at, created_at, updated_at)
           VALUES (?, 'OD-TSK-403', ?, 'Install and operate 500 GPM dewatering pump at Remuna Golei', 'Drain stormwater to prevent highway inundation.', 'MEDIUM', 4, 'COMPLETED', 'Remuna', 21.5120, 86.8740, 'Water cleared completely. Highway normalized.', ?, ?, ?)""",
        (str(uuid.uuid4()), inc_ids["INC-OD-2026-0898"], (now_dt - timedelta(hours=4)).isoformat(), (now_dt - timedelta(hours=6)).isoformat(), now)
    )
    con.commit()
    print("Tasks seeded.")

con.close()
print("All seeding successfully finished!")
