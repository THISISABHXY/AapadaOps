import { apiClient } from './apiClient';
import { DEMO_RESOURCES } from './demoDataService';
import { TacticalResource, ResourceCategory } from '../types/resource';

export function mapBackendResource(r: any): TacticalResource {
  const code = r.code || r.resource_code || r.assetCode || r.resourceCode || `ODRN-${(r.id || '').substring(0, 6)}`;
  
  // Normalize category mapping
  let category: ResourceCategory = 'RESCUE_BOAT';
  const rawCat = (r.category || '').toUpperCase();
  if (rawCat.includes('BOAT')) category = 'RESCUE_BOAT';
  else if (rawCat.includes('PUMP')) category = 'DEWATERING_PUMP';
  else if (rawCat.includes('CHAINSAW') || rawCat.includes('EXCAVATOR') || rawCat.includes('JCB')) category = 'CHAINSAW';
  else if (rawCat.includes('GENERATOR') || rawCat.includes('DG')) category = 'DG_SET';
  else if (rawCat.includes('RATION') || rawCat.includes('KIT')) category = 'RELIEF_KITS';

  // Normalize status
  let status: any = 'AVAILABLE';
  const rawStatus = (r.status || '').toUpperCase();
  if (rawStatus === 'IN_USE' || rawStatus === 'DISPATCHED' || rawStatus === 'DEPLOYED') status = 'DEPLOYED';
  else if (rawStatus === 'MAINTENANCE') status = 'MAINTENANCE';
  else if (rawStatus === 'DECOMMISSIONED' || rawStatus === 'CONDEMNED') status = 'CONDEMNED';

  return {
    id: r.id,
    assetCode: code,
    name: r.name || 'Tactical Asset',
    category,
    agency: (r.organization || r.agency || 'ODRAF') as any,
    homeDepot: r.base_location || (r.district_name ? `${r.district_name} District Staging Base` : 'Central ODRN Depot'),
    districtName: r.district_name || r.districtName || 'Kendrapara',
    status,
    currentDeploymentTaskId: r.current_task_id || r.currentDeploymentTaskId,
    currentDeploymentLocation: r.current_location || r.currentDeploymentLocation,
    fuelHoursRemaining: r.fuel_hours || r.fuelHoursRemaining || 12,
    conditionRating: (r.condition_rating || r.conditionRating || 'EXCELLENT') as any,
    lastInspected: r.last_inspected || r.updated_at || r.lastInspected || new Date().toISOString(),
  };
}

export const resourceService = {
  getResources: async (category?: ResourceCategory | string): Promise<TacticalResource[]> => {
    const isDemo = localStorage.getItem('aapadaops_demo_mode') === 'true';
    if (!isDemo) {
      try {
        const query = category && category !== 'ALL' ? `?category=${category}` : '';
        const res = await apiClient.get<any[]>(`/resources${query}`);
        if (Array.isArray(res) && res.length > 0) {
          return res.map(mapBackendResource);
        }
      } catch (err) {
        console.warn('Backend resources fetch failed, using demo fallback:', err);
      }
    }

    if (category && category !== 'ALL') {
      return DEMO_RESOURCES.filter((r) => r.category === category);
    }
    return DEMO_RESOURCES;
  },

  createResource: async (data: {
    name: string;
    category: string;
    organization: string;
    district_name: string;
    quantity?: number;
    unit_of_measure?: string;
  }): Promise<TacticalResource> => {
    const res = await apiClient.post<any>('/resources', data);
    return mapBackendResource(res);
  },
};

