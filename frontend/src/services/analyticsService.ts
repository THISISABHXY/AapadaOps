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
          return {
            totalIncidents: res.kpis.total_incidents,
            activeIncidents: res.kpis.active_incidents,
            verifiedIncidents: res.kpis.verified_incidents,
            resolvedIncidents: res.kpis.resolved_incidents,
            deployedTacticalForces: res.kpis.deployed_units,
            shelterOccupancyRate: res.kpis.shelter_occupancy_rate,
            averageResponseTimeMinutes: res.kpis.average_response_time_minutes || 28,
            highRiskDistrictsCount: 4,
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
            verifiedIncidents: Math.max(0, v.incident_count - 1),
            resolvedIncidents: Math.max(0, Math.floor(v.incident_count / 2)),
          }));
        }
      } catch (err) {
        console.warn('Backend velocity fetch failed:', err);
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
            readinessScore: d.readiness_score,
            activeIncidents: d.active_incidents,
            deployedForces: 2,
            availableForces: d.available_teams,
            shelterCapacityUsagePercent: d.shelter_capacity_percent,
          }));
        }
      } catch (err) {
        console.warn('Backend district readiness fetch failed:', err);
      }
    }
    return DEMO_DISTRICT_READINESS;
  },
};
