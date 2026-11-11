import { apiClient } from './apiClient';
import { DEMO_ALERTS } from './demoDataService';
import { DisasterAlert } from '../types/alert';

export const alertService = {
  getActiveAlerts: async (): Promise<DisasterAlert[]> => {
    const isDemo = localStorage.getItem('aapadaops_demo_mode') !== 'false';
    if (isDemo) {
      return DEMO_ALERTS.filter((a) => a.isActive);
    }
    return apiClient.get<DisasterAlert[]>('/alerts/active');
  },

  createAlert: async (data: Partial<DisasterAlert>): Promise<DisasterAlert> => {
    const isDemo = localStorage.getItem('aapadaops_demo_mode') !== 'false';
    if (isDemo) {
      const newAlert: DisasterAlert = {
        id: 'alt_' + Math.random().toString(36).substring(2, 8),
        alertCode: 'CAP-ODISHA-2026-' + Math.floor(10 + Math.random() * 90),
        hazardType: data.hazardType || 'CYCLONE',
        severityTier: data.severityTier || 'ORANGE',
        titleEn: data.titleEn || '',
        titleOr: data.titleOr || '',
        descriptionEn: data.descriptionEn || '',
        descriptionOr: data.descriptionOr || '',
        affectedDistricts: data.affectedDistricts || ['Puri'],
        effectiveFrom: new Date().toISOString(),
        expiresAt: new Date(Date.now() + 48 * 3600 * 1000).toISOString(),
        instructionsEn: data.instructionsEn || '',
        instructionsOr: data.instructionsOr || '',
        createdByName: 'Authorized State EOC Director',
        createdAt: new Date().toISOString(),
        isActive: true,
      };
      DEMO_ALERTS.unshift(newAlert);
      return newAlert;
    }
    return apiClient.post<DisasterAlert>('/alerts', data);
  },
};

