import { PriorityLevel } from './incident';

export type TaskStatus =
  | 'PENDING'
  | 'ASSIGNED'
  | 'EN_ROUTE'
  | 'ON_SCENE'
  | 'IN_PROGRESS'
  | 'RESOLVED'
  | 'COMPLETED'
  | 'CANCELLED';

export interface TacticalUnit {
  id: string;
  unitCode: string;
  name: string;
  organization: 'ODRAF' | 'NDRF' | 'FIRE_SERVICES' | 'CIVIL_DEFENCE';
  districtId: string;
  districtName: string;
  homeStation: string;
  latitude: number;
  longitude: number;
  status: 'STANDBY' | 'MOBILIZED' | 'DEPLOYED' | 'AVAILABLE' | 'MAINTENANCE' | 'OFFLINE';
  commanderName: string;
  commanderPhone: string;
  crewCount: number;
  equipmentSummary: {
    boats?: number;
    pumps?: number;
    chainsaws?: number;
    dgSets?: number;
    ambulances?: number;
  };
}

export interface Task {
  id: string;
  taskCode: string;
  incidentId: string;
  incidentCode: string;
  title: string;
  priority: PriorityLevel;
  assignedUnitId: string;
  assignedUnitName: string;
  assignedUnitOrg: string;
  assignedById?: string;
  assignedByName?: string;
  status: TaskStatus;
  targetVillage: string;
  targetLatitude: number;
  targetLongitude: number;
  slaDeadline: string;
  deadline?: string;
  slaHours?: number;
  isOverdue?: boolean;
  groundReport?: string | null;
  resolutionNotes?: string;
  progressUpdates?: any[];
  personsRescued?: number;
  resolvedAt?: string | null;
  completedAt?: string | null;
  createdAt: string;
  updatedAt?: string;
}

