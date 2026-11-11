import { PriorityLevel } from './incident';

export type TaskStatus =
  | 'PENDING'
  | 'ASSIGNED'
  | 'EN_ROUTE'
  | 'ON_SCENE'
  | 'RESOLVED'
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
  status: 'STANDBY' | 'MOBILIZED' | 'DEPLOYED' | 'MAINTENANCE' | 'OFFLINE';
  commanderName: string;
  commanderPhone: string;
  crewCount: number;
  equipmentSummary: {
    boats?: number;
    pumps?: number;
    chainsaws?: number;
    dgSets?: number;
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
  assignedById: string;
  assignedByName: string;
  status: TaskStatus;
  targetVillage: string;
  targetLatitude: number;
  targetLongitude: number;
  slaDeadline: string;
  isOverdue?: boolean;
  groundReport?: string | null;
  personsRescued?: number;
  resolvedAt?: string | null;
  createdAt: string;
  updatedAt: string;
}
