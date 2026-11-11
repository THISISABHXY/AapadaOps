import { apiClient } from './apiClient';

export interface StrategyRecommendation {
  strategy_name: 'MINIMAL_TIME' | 'MAXIMAL_CAPACITY' | 'RESERVE_PRESERVATION';
  title: string;
  recommended_teams: Array<{
    id: string;
    unit_code: string;
    name: string;
    organization: string;
    specialization: string;
    personnel_count: number;
    rescue_capacity_persons: number;
    status: string;
    latitude: number;
    longitude: number;
  }>;
  allocated_resources: Array<{
    id: string;
    resource_code: string;
    name: string;
    category: string;
    capacity: number;
    capacity_unit: string;
    status: string;
    district: string;
    latitude: number;
    longitude: number;
  }>;
  total_rescue_capacity_persons: number;
  estimated_arrival_minutes: number;
  objective_cost: number;
  reasoning: string;
  assumptions: string[];
  limitations: string[];
  estimated_resource_impact: string;
  is_live_telemetry: boolean;
  telemetry_source: string;
  telemetry_note: string;
}

export interface OptimizationResponse {
  incident_id: string;
  incident_code: string;
  recommendations: StrategyRecommendation[];
  solver_status: string;
  evaluated_teams_count: number;
  evaluated_resources_count: number;
}

export const coordinationService = {
  getOptimization: async (
    incidentId: string,
    params?: {
      requiredBoats?: number;
      requiredPumps?: number;
      preserveReserveRatio?: number;
    }
  ): Promise<OptimizationResponse> => {
    return apiClient.post<OptimizationResponse>('/coordination/optimize', {
      incident_id: incidentId,
      required_boats: params?.requiredBoats ?? 2,
      required_pumps: params?.requiredPumps ?? 1,
      preserve_reserve_ratio: params?.preserveReserveRatio ?? 0.2,
    });
  },

  createPlanFromRecommendation: async (
    incidentId: string,
    recommendation: StrategyRecommendation,
    incidentCode?: string
  ): Promise<any> => {
    return apiClient.post<any>('/coordination/plans/from-recommendation', {
      incident_id: incidentId,
      incident_code: incidentCode,
      recommendation,
    });
  },

  approvePlan: async (
    planId: string,
    slaHours = 4,
    operationalNotes?: string
  ): Promise<any> => {
    return apiClient.post<any>(`/coordination/plans/${planId}/approve`, {
      sla_hours: slaHours,
      operational_notes: operationalNotes,
    });
  },

  acknowledgePlan: async (
    planId: string,
    acknowledgmentNotes?: string
  ): Promise<any> => {
    return apiClient.post<any>(`/coordination/plans/${planId}/acknowledge`, {
      acknowledgment_notes: acknowledgmentNotes,
    });
  },

  updateProgress: async (
    planId: string,
    progressNotes: string,
    milestones?: string[]
  ): Promise<any> => {
    return apiClient.post<any>(`/coordination/plans/${planId}/progress`, {
      progress_notes: progressNotes,
      milestones,
    });
  },

  closePlan: async (
    planId: string,
    closureNotes: string,
    verifiedCasualtiesSaved = 0
  ): Promise<any> => {
    return apiClient.post<any>(`/coordination/plans/${planId}/close`, {
      closure_notes: closureNotes,
      verified_casualties_saved: verifiedCasualtiesSaved,
    });
  },

  listPlans: async (status?: string): Promise<any[]> => {
    const query = status ? `?status=${status}` : '';
    return apiClient.get<any[]>(`/coordination/plans${query}`);
  },
};
