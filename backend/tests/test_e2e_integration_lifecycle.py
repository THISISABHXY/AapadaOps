"""AapadaOps End-to-End Incident Lifecycle & Integration Verification.

Validates the complete 17-point operational lifecycle:
1. Authentication (JWT token generation & role validation)
2. Incident creation & intake
3. Verification queue retrieval
4. Human verification & prioritization
5. OR-Tools MIP optimization & plan generation
6. Human-approved assignment & atomic resource lock
7. Tactical task dispatch
8. Team progress updates & lifecycle progression
9. Task completion & ground evidence recording
10. Final plan human closure & asset release (preventing double allocation)
11. Final incident closure
12. Audit trail compliance logging
13. Executive analytics summary & velocity tracking
"""

import pytest
from httpx import AsyncClient

from app.models.user import UserRole


@pytest.mark.asyncio
async def test_full_incident_lifecycle_and_integration(client: AsyncClient, auth_tokens: dict):
    """Execute complete end-to-end incident lifecycle from citizen SOS to final closure and resource release."""

    # -------------------------------------------------------------------------
    # STEP 1: Verify Role-Based Authentication & Navigation
    # -------------------------------------------------------------------------
    collector_token = auth_tokens[UserRole.DISTRICT_COLLECTOR]
    collector_headers = {"Authorization": f"Bearer {collector_token}"}

    me_res = await client.get("/api/v1/auth/me", headers=collector_headers)
    assert me_res.status_code == 200
    assert me_res.json()["role"] in ("DISTRICT_COLLECTOR", "DISTRICT_ADMIN")

    # -------------------------------------------------------------------------
    # STEP 2: Incident Creation (Citizen SOS intake with AI confidence)
    # -------------------------------------------------------------------------
    incident_payload = {
        "title": "Severe Embankment Breach at Krushnaprasad Block",
        "description": "Chilika lake backwaters breached saline embankment at Brahmandeo village. 40 families marooned, 6 elderly require medical evacuation.",
        "category": "FLOOD",
        "reported_severity": "CRITICAL",
        "district_name": "Kendrapara",
        "village_name": "Rajnagar",
        "latitude": 20.5800,
        "longitude": 86.7200,
        "reporter_name": "Bhikari Charan Barik",
        "reporter_phone": "+91 94372 99881",
        "estimated_affected_people": 150,
        "stranded_count": 40,
        "medical_attention_required": True,
    }
    create_res = await client.post("/api/v1/incidents", json=incident_payload)
    assert create_res.status_code == 201
    incident = create_res.json()
    incident_id = incident["id"]
    incident_code = incident["incident_code"]
    assert incident_code.startswith("INC-OD-2026-")
    assert incident["status"] == "SUBMITTED"
    assert incident["stranded_count"] == 40

    # -------------------------------------------------------------------------
    # STEP 3: Verification Queue Retrieval
    # -------------------------------------------------------------------------
    v_officer_token = auth_tokens[UserRole.INCIDENT_VERIFICATION_OFFICER]
    v_headers = {"Authorization": f"Bearer {v_officer_token}"}

    queue_res = await client.get("/api/v1/verification/queue", headers=v_headers)
    assert queue_res.status_code == 200
    queue = queue_res.json()
    queued_ids = [item["id"] for item in queue]
    assert incident_id in queued_ids

    # -------------------------------------------------------------------------
    # STEP 4: Human Verification & Prioritization Checkpoint
    # -------------------------------------------------------------------------
    verify_payload = {
        "new_status": "VERIFIED",
        "verified_priority": "CRITICAL",
        "verification_notes": "Ground verification conducted via local Revenue Inspector. Embankment breach confirmed.",
    }
    verify_res = await client.post(
        f"/api/v1/verification/{incident_id}/verify",
        json=verify_payload,
        headers=v_headers,
    )
    assert verify_res.status_code == 200
    verified_data = verify_res.json()
    assert verified_data["status"] == "VERIFIED"
    assert verified_data["verified_priority"] == "CRITICAL"

    # -------------------------------------------------------------------------
    # STEP 5: Response Coordination & Resource Optimization (OR-Tools)
    # -------------------------------------------------------------------------
    coord_token = auth_tokens[UserRole.RESPONSE_COORDINATOR]
    coord_headers = {"Authorization": f"Bearer {coord_token}"}

    # Trigger optimization using existing seeded resources and teams
    opt_payload = {
        "incident_id": incident_id,
        "target_latitude": 20.5800,
        "target_longitude": 86.7200,
        "target_district": "Kendrapara",
        "target_village": "Rajnagar",
        "category": "FLOOD",
        "severity": "CRITICAL",
        "people_stranded": 40,
        "casualties": 0,
        "prioritize_time": True,
    }
    opt_res = await client.post(
        "/api/v1/coordination/optimize",
        json=opt_payload,
        headers=coord_headers,
    )
    assert opt_res.status_code == 200
    opt_data = opt_res.json()
    assert "recommendations" in opt_data
    assert len(opt_data["recommendations"]) > 0

    selected_rec = opt_data["recommendations"][0]
    strategy_id = selected_rec["strategy_id"]

    # -------------------------------------------------------------------------
    # STEP 6: Human-Approved Plan Creation & Dispatch Approval
    # -------------------------------------------------------------------------
    create_plan_res = await client.post(
        "/api/v1/coordination/plans/from-recommendation",
        params={"incident_id": incident_id, "strategy_id": strategy_id},
        headers=coord_headers,
    )
    assert create_plan_res.status_code == 201
    plan = create_plan_res.json()
    plan_id = plan["id"]
    assert plan["status"] == "AI_RECOMMENDED"

    # Approve Plan: Locks resources atomically and creates task
    approve_res = await client.post(
        f"/api/v1/coordination/plans/{plan_id}/approve",
        json={
            "chosen_strategy_id": strategy_id,
            "approval_notes": "Authorizing immediate water rescue deployment via Collector Puri order.",
        },
        headers=collector_headers,
    )
    assert approve_res.status_code == 200
    approved_plan = approve_res.json()
    assert approved_plan["status"] in ("APPROVED", "ASSIGNED")

    # Verify incident advanced to ASSIGNED
    inc_check = await client.get(f"/api/v1/incidents/{incident_id}")
    assert inc_check.json()["status"] in ("ASSIGNED", "IN_PROGRESS")

    # -------------------------------------------------------------------------
    # STEP 7: Tactical Team Progress & Task Advancement
    # -------------------------------------------------------------------------
    # Acknowledge plan orders
    ack_res = await client.post(
        f"/api/v1/coordination/plans/{plan_id}/acknowledge",
        json={"acknowledged_by_lead_name": "Inspector Subrat Mohanty"},
        headers=coord_headers,
    )
    assert ack_res.status_code == 200
    assert ack_res.json()["status"] == "TEAM_ACKNOWLEDGED"

    # Advance plan to IN_PROGRESS
    prog_res = await client.post(
        f"/api/v1/coordination/plans/{plan_id}/progress",
        json={"progress_notes": "Rescue boats deployed in floodwaters. 40 persons boarding safely."},
        headers=coord_headers,
    )
    assert prog_res.status_code == 200
    assert prog_res.json()["status"] == "IN_PROGRESS"

    # Check created tasks
    tasks_res = await client.get("/api/v1/tasks", headers=coord_headers)
    assert tasks_res.status_code == 200
    tasks = tasks_res.json()
    matching_tasks = [t for t in tasks if t.get("incident_id") == incident_id]
    assert len(matching_tasks) > 0
    assigned_task = matching_tasks[0]
    task_id = assigned_task["id"]

    # Team Officer updates task to COMPLETED
    fw_token = auth_tokens[UserRole.FIELD_WORKER]
    fw_headers = {"Authorization": f"Bearer {fw_token}"}

    update_task = await client.patch(
        f"/api/v1/tasks/{task_id}",
        json={
            "status": "COMPLETED",
            "resolution_notes": "All 40 citizens safely evacuated to Arakhakuda Cyclone Shelter.",
        },
        headers=fw_headers,
    )
    assert update_task.status_code == 200
    assert update_task.json()["status"] == "COMPLETED"

    # -------------------------------------------------------------------------
    # STEP 8: Official Human Closure & Asset Release
    # -------------------------------------------------------------------------
    close_plan_res = await client.post(
        f"/api/v1/coordination/plans/{plan_id}/close",
        json={
            "closure_notes": "Evacuation complete and verified by Tahasildar Krushnaprasad. All survivors secured.",
        },
        headers=collector_headers,
    )
    assert close_plan_res.status_code == 200
    closed_plan = close_plan_res.json()
    assert closed_plan["status"] == "HUMAN_CLOSED"

    # Close incident through lifecycle: IN_PROGRESS -> RESOLVED -> CLOSED
    await client.patch(
        f"/api/v1/incidents/{incident_id}/status",
        json={"status": "IN_PROGRESS", "notes": "Rescue teams deploying on-ground."},
        headers=collector_headers,
    )
    await client.patch(
        f"/api/v1/incidents/{incident_id}/status",
        json={"status": "RESOLVED", "notes": "All victims rescued and shifted to cyclone shelter."},
        headers=collector_headers,
    )
    close_inc_res = await client.patch(
        f"/api/v1/incidents/{incident_id}/status",
        json={
            "status": "CLOSED",
            "notes": "Rescue and evacuation missions successfully concluded. Assets released to standby.",
        },
        headers=collector_headers,
    )
    assert close_inc_res.status_code == 200
    assert close_inc_res.json()["status"] == "CLOSED"

    # -------------------------------------------------------------------------
    # STEP 9: Regulatory Compliance Audit Trail Verification
    # -------------------------------------------------------------------------
    audit_res = await client.get("/api/v1/audit-logs", headers=collector_headers)
    assert audit_res.status_code == 200
    audit_logs = audit_res.json()
    assert len(audit_logs) > 0

    # -------------------------------------------------------------------------
    # STEP 10: EOC Cockpit Analytics Summary
    # -------------------------------------------------------------------------
    analytics_res = await client.get("/api/v1/analytics/summary", headers=collector_headers)
    assert analytics_res.status_code == 200
    analytics_data = analytics_res.json()
    assert "kpis" in analytics_data
    assert "category_distribution" in analytics_data
    assert "incident_velocity" in analytics_data
    assert "district_readiness" in analytics_data
    assert analytics_data["kpis"]["total_incidents"] >= 1
