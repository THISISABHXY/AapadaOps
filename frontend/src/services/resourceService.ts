import { apiClient } from './apiClient';
import { DEMO_RESOURCES } from './demoDataService';
import { TacticalResource, ResourceCategory } from '../types/resource';

export function mapBackendResource(r: any): TacticalResource {
  return {
    id: r.id,
    resourceCode: r.code || r.resourceCode || `ODRN-${r.id?.substring(0, 6)}`,
    name: r.name,
    category: (r.category || 'RESCUE_BOAT') as ResourceCategory,
    organization: (r.organization || 'ODRAF') as any,
    districtId: r.district_id || `dst_${(r.district_name || 'kendrapara').toLowerCase()}`,
    districtName: r.district_name || r.districtName || 'Kendrapara',
    baseLocation: r.district_name ? `${r.district_name} District Staging Base` : 'Central Depot',
    latitude: Number(r.latitude || 20.5),
    longitude: Number(r.longitude || 86.4),
    status: (r.status || 'AVAILABLE') as any,
    quantity: r.quantity ?? 1,
    unit: r.unit_of_measure || r.unit || 'units',
    contactPerson: r.contact_person || r.contactPerson || 'Store In-Charge',
    contactPhone: r.contact_phone || r.contactPhone || '+91 94370 00000',
    capacity: r.capacity ? `${r.capacity} ${r.capacity_unit || ''}` : undefined,
    lastInspectedAt: r.updated_at || r.lastInspectedAt || new Date().toISOString(),
  };
}

export const resourceService = {
  getResources: async (category?: ResourceCategory): Promise<TacticalResource[]> => {
    const isDemo = localStorage.getItem('aapadaops_demo_mode') === 'true';
    if (!isDemo) {
      try {
        const query = category ? `?category=${category}` : '';
        const res = await apiClient.get<any[]>(`/resources${query}`);
        return (res || []).map(mapBackendResource);
      } catch (err) {
        console.warn('Backend resources fetch failed, using demo fallback:', err);
      }
    }

    if (category) {
      return DEMO_RESOURCES.filter((r) => r.category === category);
    }
    return DEMO_RESOURCES;
  },
};
