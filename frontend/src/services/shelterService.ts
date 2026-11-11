import { apiClient } from './apiClient';
import { DEMO_SHELTERS } from './demoDataService';
import { CycloneShelter } from '../types/shelter';

export const shelterService = {
  getShelters: async (districtId?: string): Promise<CycloneShelter[]> => {
    const isDemo = localStorage.getItem('aapadaops_demo_mode') !== 'false';
    if (isDemo) {
      if (districtId && districtId !== 'ALL') {
        return DEMO_SHELTERS.filter((s) => s.districtId === districtId);
      }
      return DEMO_SHELTERS;
    }
    const query = districtId ? `?district_id=${districtId}` : '';
    return apiClient.get<CycloneShelter[]>(`/shelters${query}`);
  },

  getShelterById: async (id: string): Promise<CycloneShelter | null> => {
    const isDemo = localStorage.getItem('aapadaops_demo_mode') !== 'false';
    if (isDemo) {
      return DEMO_SHELTERS.find((s) => s.id === id || s.code === id) || null;
    }
    return apiClient.get<CycloneShelter>(`/shelters/${id}`);
  },

  updateOccupancy: async (id: string, newOccupancy: number): Promise<CycloneShelter> => {
    const isDemo = localStorage.getItem('aapadaops_demo_mode') !== 'false';
    if (isDemo) {
      const shelter = DEMO_SHELTERS.find((s) => s.id === id);
      if (shelter) {
        shelter.currentOccupancy = newOccupancy;
        shelter.availableCapacity = Math.max(0, shelter.totalCapacity - newOccupancy);
        shelter.occupancyRate = Number((newOccupancy / shelter.totalCapacity).toFixed(2));
        shelter.status = shelter.occupancyRate >= 0.95 ? 'FULL' : 'OPERATIONAL';
        shelter.lastUpdated = new Date().toISOString();
      }
      return shelter || ({} as CycloneShelter);
    }
    return apiClient.patch<CycloneShelter>(`/shelters/${id}/logistics`, {
      current_occupancy: newOccupancy,
    });
  },
};
