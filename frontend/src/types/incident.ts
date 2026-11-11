export type IncidentStatus =
  | 'SUBMITTED'
  | 'PROCESSING'
  | 'NEEDS_VERIFICATION'
  | 'VERIFIED'
  | 'PRIORITIZED'
  | 'ASSIGNED'
  | 'IN_PROGRESS'
  | 'RESOLVED'
  | 'CLOSED'
  | 'DUPLICATE'
  | 'REJECTED'
  | 'DISPUTED'
  | 'REOPENED';

export type HazardType =
  | 'CYCLONE'
  | 'FLOOD'
  | 'WATERLOGGING'
  | 'EMBANKMENT_BREACH'
  | 'STRUCTURAL_COLLAPSE'
  | 'MEDICAL_EMERGENCY'
  | 'HEATWAVE'
  | 'OTHER';

export type PriorityLevel = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';

export interface AIEvaluation {
  id: string;
  detectedHazard: HazardType;
  confidenceScore: number;
  extractedEntities: {
    strandedCount?: number;
    waterDepthFeet?: number;
    hasInfants?: boolean;
    hasPregnantWomen?: boolean;
    hasElderly?: boolean;
    hasInjured?: boolean;
  };
  suggestedPriority: PriorityLevel;
  duplicateConfidence?: number;
  suggestedParentId?: string;
  evaluatedAt: string;
}

export interface Incident {
  id: string;
  incidentCode: string;
  source: 'CITIZEN_WEB' | 'HELPLINE_1077' | 'FIELD_WORKER' | 'SMS';
  status: IncidentStatus;
  callerName: string;
  callerPhone: string;
  latitude: number;
  longitude: number;
  addressText: string;
  districtId: string;
  districtName: string;
  blockId?: string;
  blockName?: string;
  villageName?: string;
  hazardType: HazardType;
  reportedSeverity: PriorityLevel;
  verifiedPriority?: PriorityLevel;
  personsStranded: number;
  hasVulnerablePeople: boolean;
  rawDescription: string;
  photoUrls?: string[];
  parentIncidentId?: string | null;
  duplicateCount?: number;
  verifiedById?: string | null;
  verifiedByName?: string | null;
  verifiedAt?: string | null;
  rejectionReason?: string | null;
  disputeNotes?: string | null;
  aiEvaluation?: AIEvaluation;
  createdAt: string;
  updatedAt: string;
}

export interface IncidentCluster {
  id: string;
  clusterCode: string;
  masterIncident: Incident;
  candidateDuplicates: Incident[];
  radiusMeters: number;
  createdTimeSpanMinutes: number;
}
