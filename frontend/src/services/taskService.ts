import { apiClient } from './apiClient';
import { DEMO_TASKS, DEMO_TACTICAL_UNITS } from './demoDataService';
import { Task, TaskStatus, TacticalUnit } from '../types/task';
import { PriorityLevel } from '../types/incident';

export const taskService = {
  getTasks: async (params?: { unitId?: string; status?: TaskStatus }): Promise<Task[]> => {
    const isDemo = localStorage.getItem('aapadaops_demo_mode') !== 'false';
    if (isDemo) {
      let filtered = [...DEMO_TASKS];
      if (params?.unitId) {
        filtered = filtered.filter((t) => t.assignedUnitId === params.unitId);
      }
      if (params?.status) {
        filtered = filtered.filter((t) => t.status === params.status);
      }
      return filtered;
    }
    const query = new URLSearchParams();
    if (params?.unitId) query.set('unit_id', params.unitId);
    if (params?.status) query.set('status', params.status);
    return apiClient.get<Task[]>(`/tasks?${query.toString()}`);
  },

  getTacticalUnits: async (districtId?: string): Promise<TacticalUnit[]> => {
    const isDemo = localStorage.getItem('aapadaops_demo_mode') !== 'false';
    if (isDemo) {
      if (districtId && districtId !== 'ALL') {
        return DEMO_TACTICAL_UNITS.filter((u) => u.districtId === districtId);
      }
      return DEMO_TACTICAL_UNITS;
    }
    const query = districtId ? `?district_id=${districtId}` : '';
    return apiClient.get<TacticalUnit[]>(`/resources/units${query}`);
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
    const isDemo = localStorage.getItem('aapadaops_demo_mode') !== 'false';
    if (isDemo) {
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
        assignedById: 'usr_current',
        assignedByName: 'Response Coordinator (Demo)',
        status: 'ASSIGNED',
        targetVillage: data.targetVillage,
        targetLatitude: data.targetLatitude,
        targetLongitude: data.targetLongitude,
        slaDeadline: new Date(Date.now() + data.slaHours * 3600 * 1000).toISOString(),
        isOverdue: false,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
      DEMO_TASKS.unshift(newTask);
      return newTask;
    }
    return apiClient.post<Task>('/tasks', data);
  },

  updateTaskStatus: async (
    id: string,
    status: TaskStatus,
    groundReport?: string,
    personsRescued?: number
  ): Promise<Task> => {
    const isDemo = localStorage.getItem('aapadaops_demo_mode') !== 'false';
    if (isDemo) {
      const task = DEMO_TASKS.find((t) => t.id === id);
      if (task) {
        task.status = status;
        task.updatedAt = new Date().toISOString();
        if (groundReport) task.groundReport = groundReport;
        if (personsRescued !== undefined) task.personsRescued = personsRescued;
        if (status === 'RESOLVED') task.resolvedAt = new Date().toISOString();
      }
      return task || ({} as Task);
    }
    return apiClient.patch<Task>(`/tasks/${id}/status`, {
      status,
      ground_report: groundReport,
      persons_rescued: personsRescued,
    });
  },
};
