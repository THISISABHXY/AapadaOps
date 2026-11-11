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
  getEocKpi: async (districtId?: string): Promise<EocSummaryKpi> => {
    const isDemo = localStorage.getItem('aapadaops_demo_mode') !== 'false';
    if (isDemo) {
      return DEMO_EOC_KPI;
    }
    const query = districtId ? `?district_id=${districtId}` : '';
    return apiClient.get<EocSummaryKpi>(`/analytics/eoc-summary${query}`);
  },

  getHourlyTrends: async (): Promise<HourlyIncidentTrend[]> => {
    const isDemo = localStorage.getItem('aapadaops_demo_mode') !== 'false';
    if (isDemo) {
      return DEMO_HOURLY_TRENDS;
    }
    return apiClient.get<HourlyIncidentTrend[]>('/analytics/hourly-trends');
  },

  getHazardBreakdown: async (): Promise<HazardBreakdown[]> => {
    const isDemo = localStorage.getItem('aapadaops_demo_mode') !== 'false';
    if (isDemo) {
      return DEMO_HAZARD_BREAKDOWN;
    }
    return apiClient.get<HazardBreakdown[]>('/analytics/hazard-breakdown');
  },

  getDistrictReadiness: async (): Promise<DistrictReadinessMetrics[]> => {
    const isDemo = localStorage.getItem('aapadaops_demo_mode') !== 'false';
    if (isDemo) {
      return DEMO_DISTRICT_READINESS;
    }
    return apiClient.get<DistrictReadinessMetrics[]>('/analytics/district-readiness');
  },
};
