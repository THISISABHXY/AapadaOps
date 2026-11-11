import { apiClient } from './apiClient';
import { DEMO_RESOURCES } from './demoDataService';
import { TacticalResource, ResourceCategory } from '../types/resource';

export const resourceService = {
  getResources: async (category?: ResourceCategory): Promise<TacticalResource[]> => {
    const isDemo = localStorage.getItem('aapadaops_demo_mode') !== 'false';
    if (isDemo) {
      if (category) {
        return DEMO_RESOURCES.filter((r) => r.category === category);
      }
      return DEMO_RESOURCES;
    }
    const query = category ? `?category=${category}` : '';
    return apiClient.get<TacticalResource[]>(`/resources${query}`);
  },
};

