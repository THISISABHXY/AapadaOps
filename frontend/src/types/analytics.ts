export interface EocSummaryKpi {
  activeDisastersCount: number;
  totalIngestedIncidents: number;
  totalIncidents?: number;
  activeIncidents?: number;
  verifiedIncidents?: number;
  resolvedIncidents?: number;
  unverifiedIncidentsCount: number;
  verifiedActiveTasksCount: number;
  resolvedTasksCount: number;
  totalEvacuatedCitizens: number;
  operationalSheltersCount: number;
  averageShelterOccupancyRate: number;
  shelterOccupancyRate?: number;
  deployedTacticalUnitsCount: number;
  deployedTacticalForces?: number;
  availableTacticalUnitsCount: number;
  averageResponseMinutes: number;
  averageResponseTimeMinutes?: number;
  highRiskDistrictsCount?: number;
  activeStateAlertTier: 'GREEN' | 'YELLOW' | 'ORANGE' | 'RED';
}

export interface HourlyIncidentTrend {
  hour: string;
  incomingReports: number;
  verifiedTasks: number;
  resolvedTasks: number;
  resolvedIncidents?: number;
}

export interface HazardBreakdown {
  hazardType: string;
  count: number;
  percentage: number;
}

export interface DistrictReadinessMetrics {
  districtName: string;
  activeIncidents: number;
  openShelters: number;
  evacueeCount: number;
  availableBoats: number;
  availablePumps: number;
  alertTier: 'GREEN' | 'YELLOW' | 'ORANGE' | 'RED';
}

