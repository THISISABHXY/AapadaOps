import { apiClient } from './apiClient';
import { DEMO_ALERTS } from './demoDataService';
import { DisasterAlert } from '../types/alert';

export function mapBackendAlert(a: any): DisasterAlert {
  let districts = ['Kendrapara', 'Bhadrak', 'Balasore'];
  if (a.affected_districts_json) {
    try {
      districts = JSON.parse(a.affected_districts_json);
    } catch {
      // Ignore parse error
    }
  }

  return {
    id: a.id,
    alertCode: a.alert_code || a.alertCode || `SATARK-${a.id?.substring(0, 6)}`,
    hazardType: a.hazard_type || a.hazardType || 'CYCLONE',
    severityTier: (a.severity || a.severityTier || 'RED') as any,
    titleEn: a.headline || a.titleEn || 'State Disaster Warning',
    titleOr: 'ଓଡ଼ିଶା ରାଜ୍ୟ ବିପର୍ଯ୍ୟୟ ସତର୍କତା',
    descriptionEn: a.advisory_body || a.descriptionEn || '',
    descriptionOr: 'ଜରୁରୀକାଳୀନ ପଦକ୍ଷେପ ଏବଂ ବାତ୍ୟା ଆଶ୍ରୟସ୍ଥଳକୁ ସ୍ଥାନାନ୍ତରଣ ଜାରି ରହିଛି।',
    affectedDistricts: districts,
    effectiveFrom: a.issued_at || a.effectiveFrom || new Date().toISOString(),
    expiresAt: a.valid_until || a.expiresAt || new Date(Date.now() + 36 * 3600000).toISOString(),
    instructionsEn: 'Fishermen are advised not to venture into sea. Coastal residents should evacuate to Multipurpose Cyclone Shelters.',
    instructionsOr: 'ମତ୍ସ୍ୟଜୀବୀମାନଙ୍କୁ ସମୁଦ୍ରକୁ ଯିବା ପାଇଁ ବାରଣ କରାଯାଇଛି। ନିକଟସ୍ଥ ବାତ୍ୟା ଆଶ୍ରୟସ୍ଥଳକୁ ଯାଆନ୍ତୁ।',
    createdByName: a.source || 'IMD_OSDMA_SATARK',
    createdAt: a.created_at || new Date().toISOString(),
    isActive: Boolean(a.is_active ?? true),
  };
}

export const alertService = {
  getActiveAlerts: async (): Promise<DisasterAlert[]> => {
    const isDemo = localStorage.getItem('aapadaops_demo_mode') === 'true';
    if (!isDemo) {
      try {
        const res = await apiClient.get<any[]>('/alerts/active');
        return (res || []).map(mapBackendAlert);
      } catch (err) {
        console.warn('Backend active alerts fetch failed, using demo fallback:', err);
      }
    }
    return DEMO_ALERTS.filter((a) => a.isActive);
  },

  createAlert: async (data: Partial<DisasterAlert>): Promise<DisasterAlert> => {
    const isDemo = localStorage.getItem('aapadaops_demo_mode') === 'true';
    if (!isDemo) {
      try {
        const payload = {
          alert_code: `SATARK-${data.severityTier || 'ORANGE'}-${Math.floor(100 + Math.random() * 900)}`,
          severity: data.severityTier || 'ORANGE',
          hazard_type: data.hazardType || 'CYCLONE',
          headline: data.titleEn || 'Emergency Weather Warning',
          advisory_body: data.descriptionEn || '',
          affected_districts_json: JSON.stringify(data.affectedDistricts || ['Puri']),
          source: 'OSDMA_EOC_DIRECTOR',
          valid_hours: 48,
        };
        const res = await apiClient.post<any>('/alerts/broadcast', payload);
        return mapBackendAlert(res);
      } catch (err) {
        console.warn('Backend broadcast alert failed:', err);
      }
    }

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
  },
};
