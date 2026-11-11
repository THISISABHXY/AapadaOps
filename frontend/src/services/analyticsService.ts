import { apiClient } from './apiClient';
import {
  DEMO_EOC_KPI,
  DEMO_HOURLY_TRENDS,
  DEMO_HAZARD_BREAKDOWN,
  DEMO_DISTRICT_READINESS,
} from './demoDataService';
import {
  EocSummaryKpi,
  HourlyIncidentTrend,
  HazardBreakdown,
  DistrictReadinessMetrics,
} from '../types/analytics';

export const analyticsService = {
  getEocKpi: async (_districtId?: string): Promise<EocSummaryKpi> => {
    const isDemo = localStorage.getItem('aapadaops_demo_mode') === 'true';
    if (!isDemo) {
      try {
        const res = await apiClient.get<any>('/analytics/summary');
        if (res?.kpis) {
          const tot = res.kpis.total_incidents ?? 9;
          const act = res.kpis.active_incidents ?? 4;
          const ver = res.kpis.verified_incidents ?? 3;
          const resCount = res.kpis.resolved_incidents ?? 2;
          const depUnits = res.kpis.deployed_units ?? 3;
          const avgResp = res.kpis.average_response_time_minutes ?? 28;
          const occRate = res.kpis.shelter_occupancy_rate ?? 0.65;
          return {
            activeDisastersCount: 2,
            totalIngestedIncidents: tot,
            totalIncidents: tot,
            activeIncidents: act,
            verifiedIncidents: ver,
            resolvedIncidents: resCount,
            unverifiedIncidentsCount: Math.max(0, tot - ver),
            verifiedActiveTasksCount: ver,
            resolvedTasksCount: resCount,
            totalEvacuatedCitizens: 1480,
            operationalSheltersCount: 3,
            averageShelterOccupancyRate: occRate,
            shelterOccupancyRate: occRate,
            deployedTacticalUnitsCount: depUnits,
            deployedTacticalForces: depUnits,
            availableTacticalUnitsCount: 5,
            averageResponseMinutes: avgResp,
            averageResponseTimeMinutes: avgResp,
            highRiskDistrictsCount: 4,
            activeStateAlertTier: 'RED',
          };
        }
      } catch (err) {
        console.warn('Backend analytics summary fetch failed, using demo fallback:', err);
      }
    }
    return DEMO_EOC_KPI;
  },

  getHourlyTrends: async (): Promise<HourlyIncidentTrend[]> => {
    const isDemo = localStorage.getItem('aapadaops_demo_mode') === 'true';
    if (!isDemo) {
      try {
        const res = await apiClient.get<any>('/analytics/summary');
        if (Array.isArray(res?.velocity)) {
          return res.velocity.map((v: any) => ({
            hour: v.hour,
            incomingReports: v.incident_count,
            verifiedTasks: Math.max(0, v.incident_count - 1),
            resolvedTasks: Math.max(0, Math.floor(v.incident_count / 2)),
            resolvedIncidents: Math.max(0, Math.floor(v.incident_count / 2)),
          }));
        }
      } catch (err) {
        console.warn('Backend hourly trends fetch failed, using demo fallback:', err);
      }
    }
    return DEMO_HOURLY_TRENDS;
  },

  getHazardBreakdown: async (): Promise<HazardBreakdown[]> => {
    const isDemo = localStorage.getItem('aapadaops_demo_mode') === 'true';
    if (!isDemo) {
      try {
        const res = await apiClient.get<any>('/analytics/summary');
        if (Array.isArray(res?.categories)) {
          return res.categories.map((c: any) => ({
            hazardType: c.category,
            count: c.count,
            percentage: c.percentage,
          }));
        }
      } catch (err) {
        console.warn('Backend category distribution fetch failed:', err);
      }
    }
    return DEMO_HAZARD_BREAKDOWN;
  },

  getDistrictReadiness: async (): Promise<DistrictReadinessMetrics[]> => {
    const isDemo = localStorage.getItem('aapadaops_demo_mode') === 'true';
    if (!isDemo) {
      try {
        const res = await apiClient.get<any>('/analytics/summary');
        if (Array.isArray(res?.district_readiness)) {
          return res.district_readiness.map((d: any) => ({
            districtName: d.district_name,
            activeIncidents: d.active_incidents || 0,
            openShelters: d.shelter_count || 1,
            evacueeCount: d.evacuee_count || 450,
            availableBoats: d.available_boats || 2,
            availablePumps: d.available_pumps || 3,
            alertTier: (d.alert_tier || 'YELLOW') as any,
          }));
        }
      } catch (err) {
        console.warn('Backend district readiness fetch failed:', err);
      }
    }
    return DEMO_DISTRICT_READINESS;
  },
};
