import { apiClient } from './apiClient';
import { DEMO_INCIDENTS } from './demoDataService';
import { Incident, IncidentStatus, PriorityLevel } from '../types/incident';

export const incidentService = {
  getIncidents: async (params?: {
    districtId?: string;
    status?: IncidentStatus;
    priority?: PriorityLevel;
  }): Promise<Incident[]> => {
    const isDemo = localStorage.getItem('aapadaops_demo_mode') !== 'false';
    if (isDemo) {
      let filtered = [...DEMO_INCIDENTS];
      if (params?.status) {
        filtered = filtered.filter((i) => i.status === params.status);
      }
      if (params?.priority) {
        filtered = filtered.filter(
          (i) => i.verifiedPriority === params.priority || i.reportedSeverity === params.priority
        );
      }
      if (params?.districtId && params.districtId !== 'ALL') {
        filtered = filtered.filter((i) => i.districtId === params.districtId);
      }
      return filtered;
    }

    const query = new URLSearchParams();
    if (params?.districtId) query.set('district_id', params.districtId);
    if (params?.status) query.set('status', params.status);
    if (params?.priority) query.set('priority', params.priority);

    return apiClient.get<Incident[]>(`/incidents?${query.toString()}`);
  },

  getIncidentById: async (id: string): Promise<Incident | null> => {
    const isDemo = localStorage.getItem('aapadaops_demo_mode') !== 'false';
    if (isDemo) {
      return DEMO_INCIDENTS.find((i) => i.id === id || i.incidentCode === id) || null;
    }
    return apiClient.get<Incident>(`/incidents/${id}`);
  },

  submitIncident: async (data: Partial<Incident>): Promise<Incident> => {
    const isDemo = localStorage.getItem('aapadaops_demo_mode') !== 'false';
    if (isDemo) {
      const newInc: Incident = {
        id: 'inc_' + Math.random().toString(36).substring(2, 8),
        incidentCode: 'OD-2026-' + Math.floor(1000 + Math.random() * 9000),
        source: data.source || 'CITIZEN_WEB',
        status: 'NEEDS_VERIFICATION',
        callerName: data.callerName || 'Anonymous',
        callerPhone: data.callerPhone || '9800000000',
        latitude: data.latitude || 19.8135,
        longitude: data.longitude || 85.8312,
        addressText: data.addressText || 'District Sector',
        districtId: data.districtId || 'dst_puri',
        districtName: data.districtName || 'Puri',
        blockName: data.blockName || 'Puri Sadar',
        villageName: data.villageName || 'Coastal Area',
        hazardType: data.hazardType || 'OTHER',
        reportedSeverity: data.reportedSeverity || 'HIGH',
        personsStranded: data.personsStranded || 1,
        hasVulnerablePeople: data.hasVulnerablePeople || false,
        rawDescription: data.rawDescription || '',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
      DEMO_INCIDENTS.unshift(newInc);
      return newInc;
    }
    return apiClient.post<Incident>('/incidents', data);
  },

  verifyIncident: async (
    id: string,
    data: {
      status: 'VERIFIED' | 'REJECTED' | 'DISPUTED';
      verifiedPriority: PriorityLevel;
      verificationNotes: string;
      rejectionReason?: string;
    }
  ): Promise<Incident> => {
    const isDemo = localStorage.getItem('aapadaops_demo_mode') !== 'false';
    if (isDemo) {
      const inc = DEMO_INCIDENTS.find((i) => i.id === id);
      if (inc) {
        inc.status = data.status;
        inc.verifiedPriority = data.verifiedPriority;
        inc.verifiedAt = new Date().toISOString();
        inc.verifiedByName = 'Authorized Officer (Demo)';
        if (data.rejectionReason) inc.rejectionReason = data.rejectionReason;
        if (data.status === 'DISPUTED') inc.disputeNotes = data.verificationNotes;
      }
      return inc || ({} as Incident);
    }
    return apiClient.patch<Incident>(`/incidents/${id}/verify`, data);
  },

  linkDuplicate: async (childId: string, parentId: string): Promise<Incident> => {
    const isDemo = localStorage.getItem('aapadaops_demo_mode') !== 'false';
    if (isDemo) {
      const child = DEMO_INCIDENTS.find((i) => i.id === childId);
      const parent = DEMO_INCIDENTS.find((i) => i.id === parentId);
      if (child && parent) {
        child.status = 'DUPLICATE';
        child.parentIncidentId = parentId;
        parent.duplicateCount = (parent.duplicateCount || 0) + 1;
        parent.personsStranded += child.personsStranded || 0;
      }
      return child || ({} as Incident);
    }
    return apiClient.post<Incident>(`/incidents/${childId}/cluster-duplicate`, {
      parent_incident_id: parentId,
    });
  },
};

