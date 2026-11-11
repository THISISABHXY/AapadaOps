import { apiClient } from './apiClient';
import { DEMO_SHELTERS } from './demoDataService';
import { CycloneShelter } from '../types/shelter';

export function mapBackendShelter(s: any): CycloneShelter {
  const total = s.capacity || s.totalCapacity || 800;
  const occ = s.current_occupancy ?? s.currentOccupancy ?? 0;
  return {
    id: s.id,
    code: s.code || `MCS-${s.id?.substring(0, 6)}`,
    name: s.name,
    districtId: s.district_id || `dst_${(s.district_name || 'kendrapara').toLowerCase()}`,
    districtName: s.district_name || s.districtName || 'Kendrapara',
    blockName: s.block_name || s.blockName || 'Block Alpha',
    villageName: s.village || s.villageName || 'Coastal Sector',
    latitude: Number(s.latitude || 20.7),
    longitude: Number(s.longitude || 86.8),
    totalCapacity: total,
    currentOccupancy: occ,
    availableCapacity: Math.max(0, total - occ),
    occupancyRate: total > 0 ? Number((occ / total).toFixed(2)) : 0,
    status: s.status === 'FULL' || (total > 0 && occ >= total) ? 'FULL' : 'OPERATIONAL',
    powerBackup: Boolean(s.has_power_backup ?? s.powerBackup ?? true),
    waterSupplyDays: s.drinking_water_days ?? s.waterSupplyDays ?? 5,
    medicalAidAvailable: Boolean(s.has_medical_kit ?? s.medicalAidAvailable ?? true),
    caretakerName: s.caretaker_name || s.caretakerName || 'Caretaker on Duty',
    caretakerPhone: s.caretaker_phone || s.caretakerPhone || '+91 94370 00000',
    lastUpdated: s.updated_at || s.lastUpdated || new Date().toISOString(),
  };
}

export const shelterService = {
  getShelters: async (districtId?: string): Promise<CycloneShelter[]> => {
    const isDemo = localStorage.getItem('aapadaops_demo_mode') === 'true';
    if (!isDemo) {
      try {
        const query = districtId && districtId !== 'ALL' ? `?district=${districtId}` : '';
        const res = await apiClient.get<any[]>(`/shelters${query}`);
        return (res || []).map(mapBackendShelter);
      } catch (err) {
        console.warn('Backend shelters fetch failed, using demo fallback:', err);
      }
    }

    if (districtId && districtId !== 'ALL') {
      return DEMO_SHELTERS.filter((s) => s.districtName?.toLowerCase() === districtId.toLowerCase());
    }
    return DEMO_SHELTERS;
  },

  getShelterById: async (id: string): Promise<CycloneShelter | null> => {
    const isDemo = localStorage.getItem('aapadaops_demo_mode') === 'true';
    if (!isDemo) {
      try {
        const raw = await apiClient.get<any>(`/shelters/${id}`);
        return mapBackendShelter(raw);
      } catch (err) {
        console.warn('Backend getShelterById failed:', err);
      }
    }
    return DEMO_SHELTERS.find((s) => s.id === id || s.code === id) || null;
  },

  updateOccupancy: async (id: string, newOccupancy: number): Promise<CycloneShelter> => {
    const isDemo = localStorage.getItem('aapadaops_demo_mode') === 'true';
    if (!isDemo) {
      try {
        const res = await apiClient.patch<any>(`/shelters/${id}/occupancy`, {
          current_occupancy: newOccupancy,
        });
        return mapBackendShelter(res);
      } catch (err) {
        console.warn('Backend updateOccupancy failed:', err);
      }
    }

    const shelter = DEMO_SHELTERS.find((s) => s.id === id);
    if (shelter) {
      shelter.currentOccupancy = newOccupancy;
      shelter.availableCapacity = Math.max(0, shelter.totalCapacity - newOccupancy);
      shelter.occupancyRate = Number((newOccupancy / shelter.totalCapacity).toFixed(2));
      shelter.status = shelter.occupancyRate >= 0.95 ? 'FULL' : 'OPERATIONAL';
      shelter.lastUpdated = new Date().toISOString();
    }
    return shelter || ({} as CycloneShelter);
  },
};
