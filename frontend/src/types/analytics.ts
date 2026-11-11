export interface EocSummaryKpi {
  activeDisastersCount: number;
  totalIngestedIncidents: number;
  unverifiedIncidentsCount: number;
  verifiedActiveTasksCount: number;
  resolvedTasksCount: number;
  totalEvacuatedCitizens: number;
  operationalSheltersCount: number;
  averageShelterOccupancyRate: number;
  deployedTacticalUnitsCount: number;
  availableTacticalUnitsCount: number;
  averageResponseMinutes: number;
  activeStateAlertTier: 'GREEN' | 'YELLOW' | 'ORANGE' | 'RED';
}

export interface HourlyIncidentTrend {
  hour: string;
  incomingReports: number;
  verifiedTasks: number;
  resolvedTasks: number;
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
