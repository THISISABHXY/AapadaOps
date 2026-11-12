import { apiClient } from './apiClient';
import { DEMO_TASKS, DEMO_TACTICAL_UNITS } from './demoDataService';
import { Task, TaskStatus, TacticalUnit } from '../types/task';
import { PriorityLevel } from '../types/incident';

export function mapBackendTask(t: any): Task {
  return {
    id: t.id,
    taskCode: t.task_code || t.taskCode || `TSK-${t.id?.substring(0, 6)}`,
    incidentId: t.incident_id || t.incidentId,
    incidentCode: t.incident_code || t.incidentCode || 'OD-INC-LINKED',
    title: t.title,
    priority: (t.priority || 'HIGH') as PriorityLevel,
    assignedUnitId: t.assigned_team_id || t.assignedUnitId || '',
    assignedUnitName: t.assigned_team_name || t.assignedUnitName || 'ODRAF Special Force',
    assignedUnitOrg: t.assigned_team_org || t.assignedUnitOrg || 'ODRAF',
    targetVillage: t.target_village || t.targetVillage || 'Operational Sector',
    targetLatitude: Number(t.target_latitude || t.targetLatitude || 20.5),
    targetLongitude: Number(t.target_longitude || t.targetLongitude || 86.4),
    status: (t.status || 'ASSIGNED') as TaskStatus,
    slaHours: t.sla_hours || t.slaHours || 4,
    deadline: t.deadline || new Date(Date.now() + 4 * 3600000).toISOString(),
    progressUpdates: t.progress_updates || [],
    createdAt: t.created_at || new Date().toISOString(),
    completedAt: t.completed_at || t.completedAt,
    resolutionNotes: t.resolution_notes || t.resolutionNotes,
  };
}

export function mapBackendTeam(team: any): TacticalUnit {
  return {
    id: team.id,
    unitCode: team.code || team.unitCode || 'UNIT-01',
    name: team.name,
    organization: (team.organization || 'ODRAF') as any,
    commanderName: team.team_lead_name || team.commanderName || 'Officer in Charge',
    commanderPhone: team.team_lead_phone || team.commanderPhone || '+91 94370 00000',
    crewCount: team.total_personnel || team.crewCount || 25,
    status: team.status === 'STANDBY' ? 'AVAILABLE' : team.status === 'DEPLOYED' ? 'DEPLOYED' : 'MOBILIZED',
    homeStation: team.battalion || team.current_district_name || 'Bhubaneswar Central Staging',
    latitude: Number(team.latitude || 20.5),
    longitude: Number(team.longitude || 86.4),
    districtId: `dst_${(team.current_district_name || 'kendrapara').toLowerCase()}`,
    districtName: team.current_district_name || 'Kendrapara',
    equipmentSummary: {
      boats: team.specialization === 'WATER_RESCUE' ? 4 : 2,
      ambulances: 1,
      pumps: 3,
      generators: 2,
    },
  };
}

export const taskService = {
  getTasks: async (params?: { unitId?: string; status?: TaskStatus }): Promise<Task[]> => {
    const isDemo = localStorage.getItem('aapadaops_demo_mode') === 'true';
    if (!isDemo) {
      try {
        const query = new URLSearchParams();
        if (params?.unitId) query.set('team_id', params.unitId);
        if (params?.status) query.set('status', params.status);

        const res = await apiClient.get<any[]>(`/tasks?${query.toString()}`);
        return (res || []).map(mapBackendTask);
      } catch (err) {
        console.warn('Backend tasks fetch failed, falling back to cached demo tasks:', err);
      }
    }

    let filtered = [...DEMO_TASKS];
    if (params?.unitId) {
      filtered = filtered.filter((t) => t.assignedUnitId === params.unitId);
    }
    if (params?.status) {
      filtered = filtered.filter((t) => t.status === params.status);
    }
    return filtered;
  },

  getTacticalUnits: async (districtId?: string): Promise<TacticalUnit[]> => {
    const isDemo = localStorage.getItem('aapadaops_demo_mode') === 'true';
    if (!isDemo) {
      try {
        const query = districtId && districtId !== 'ALL' ? `?district=${districtId}` : '';
        const res = await apiClient.get<any[]>(`/teams${query}`);
        return (res || []).map(mapBackendTeam);
      } catch (err) {
        console.warn('Backend teams fetch failed, falling back to demo units:', err);
      }
    }

    if (districtId && districtId !== 'ALL') {
      return DEMO_TACTICAL_UNITS.filter((u) => u.districtName?.toLowerCase() === districtId.toLowerCase());
    }
    return DEMO_TACTICAL_UNITS;
  },

  createTask: async (data: {
    incidentId: string;
    incidentCode: string;
    title: string;
    priority: PriorityLevel;
    assignedUnitId: string;
    targetVillage: string;
    targetLatitude: number;
    targetLongitude: number;
    slaHours: number;
  }): Promise<Task> => {
    const isDemo = localStorage.getItem('aapadaops_demo_mode') === 'true';
    if (!isDemo) {
      try {
        const payload = {
          incident_id: data.incidentId,
          assigned_team_id: data.assignedUnitId,
          title: data.title,
          priority: data.priority,
          sla_hours: data.slaHours,
          target_village: data.targetVillage,
          target_latitude: data.targetLatitude,
          target_longitude: data.targetLongitude,
          dispatch_notes: `Tactical force assigned with SLA ${data.slaHours}h.`,
        };
        const res = await apiClient.post<any>('/tasks', payload);
        return mapBackendTask(res);
      } catch (err) {
        console.warn('Backend task create failed, using demo fallback:', err);
      }
    }

    const unit = DEMO_TACTICAL_UNITS.find((u) => u.id === data.assignedUnitId);
    const newTask: Task = {
      id: 'tsk_' + Math.random().toString(36).substring(2, 8),
      taskCode: 'OD-TSK-' + Math.floor(100 + Math.random() * 900),
      incidentId: data.incidentId,
      incidentCode: data.incidentCode,
      title: data.title,
      priority: data.priority,
      assignedUnitId: data.assignedUnitId,
      assignedUnitName: unit?.name || 'Tactical Team',
      assignedUnitOrg: unit?.organization || 'ODRAF',
      targetVillage: data.targetVillage,
      targetLatitude: data.targetLatitude,
      targetLongitude: data.targetLongitude,
      status: 'ASSIGNED',
      slaHours: data.slaHours,
      deadline: new Date(Date.now() + data.slaHours * 3600000).toISOString(),
      progressUpdates: [],
      createdAt: new Date().toISOString(),
    };
    DEMO_TASKS.unshift(newTask);
    return newTask;
  },

  updateTaskStatus: async (
    taskId: string,
    status: TaskStatus,
    resolutionNotes?: string
  ): Promise<Task> => {
    const isDemo = localStorage.getItem('aapadaops_demo_mode') === 'true';
    if (!isDemo) {
      try {
        const res = await apiClient.patch<any>(`/tasks/${taskId}`, {
          status,
          resolution_notes: resolutionNotes,
        });
        return mapBackendTask(res);
      } catch (err) {
        console.warn('Backend updateTaskStatus failed:', err);
      }
    }

    const task = DEMO_TASKS.find((t) => t.id === taskId);
    if (task) {
      task.status = status;
      if (resolutionNotes) task.resolutionNotes = resolutionNotes;
      if (status === 'COMPLETED') task.completedAt = new Date().toISOString();
    }
    return task || ({} as Task);
  },
};
