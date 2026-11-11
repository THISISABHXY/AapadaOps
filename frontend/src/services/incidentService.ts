import { apiClient } from './apiClient';
import { DEMO_INCIDENTS } from './demoDataService';
import { Incident, IncidentStatus, PriorityLevel, HazardType } from '../types/incident';

export function mapBackendIncident(item: any): Incident {
  return {
    id: item.id,
    incidentCode: item.incident_code || item.incidentCode || `OD-${item.id?.substring(0, 8)}`,
    source: (item.source || (item.reporter_role === 'OFFICIAL' ? 'FIELD_WORKER' : 'CITIZEN_WEB')) as any,
    status: item.status as IncidentStatus,
    callerName: item.reporter_name || item.callerName || 'Anonymous Citizen',
    callerPhone: item.reporter_phone || item.callerPhone || '+91 94370 00000',
    latitude: Number(item.latitude),
    longitude: Number(item.longitude),
    addressText: item.village_name
      ? `${item.village_name}, ${item.block_name || ''}, ${item.district_name || ''}`
      : item.addressText || 'Odisha Sector',
    districtId: item.district_id || `dst_${(item.district_name || 'kendrapara').toLowerCase()}`,
    districtName: item.district_name || item.districtName || 'Kendrapara',
    blockId: item.block_id,
    blockName: item.block_name || item.blockName,
    villageName: item.village_name || item.villageName || 'Inundation Site',
    hazardType: (item.category || item.hazardType || 'FLOOD') as HazardType,
    reportedSeverity: (item.reported_severity || item.reportedSeverity || 'HIGH') as PriorityLevel,
    verifiedPriority: item.verified_priority || item.verifiedPriority,
    personsStranded: item.stranded_count ?? item.personsStranded ?? item.estimated_affected_people ?? 0,
    hasVulnerablePeople: Boolean(item.has_vulnerable_people ?? item.hasVulnerablePeople ?? false),
    rawDescription: item.description || item.rawDescription || '',
    photoUrls: item.photo_urls || item.photoUrls || [],
    parentIncidentId: item.duplicate_of_id || item.parentIncidentId,
    duplicateCount: item.duplicate_count || item.duplicateCount || 0,
    verifiedById: item.verified_by_id || item.verifiedById,
    verifiedByName: item.verified_by_name || item.verifiedByName,
    verifiedAt: item.verified_at || item.verifiedAt,
    rejectionReason: item.rejection_reason || item.rejectionReason,
    disputeNotes: item.dispute_notes || item.disputeNotes,
    aiEvaluation: item.ai_confidence_score
      ? {
          id: `ai_${item.id}`,
          detectedHazard: (item.category || 'FLOOD') as HazardType,
          confidenceScore: item.ai_confidence_score,
          suggestedPriority: (item.reported_severity || 'HIGH') as PriorityLevel,
          extractedEntities: {
            strandedCount: item.stranded_count || 0,
            hasElderly: true,
            hasPregnantWomen: false,
          },
          evaluatedAt: item.created_at,
        }
      : undefined,
    createdAt: item.created_at || new Date().toISOString(),
    updatedAt: item.updated_at || new Date().toISOString(),
  };
}

export const incidentService = {
  getIncidents: async (params?: {
    districtId?: string;
    status?: IncidentStatus;
    priority?: PriorityLevel;
    search?: string;
    page?: number;
    pageSize?: number;
  }): Promise<Incident[]> => {
    const isDemo = localStorage.getItem('aapadaops_demo_mode') === 'true';

    if (!isDemo) {
      try {
        const query = new URLSearchParams();
        if (params?.districtId && params.districtId !== 'ALL') {
          query.set('district', params.districtId);
        }
        if (params?.status) query.set('status', params.status);
        if (params?.priority) query.set('severity', params.priority);
        if (params?.search) query.set('search', params.search);
        if (params?.page) query.set('page', String(params.page));
        if (params?.pageSize) query.set('page_size', String(params.pageSize));

        const res = await apiClient.get<any>(`/incidents?${query.toString()}`);
        const rawList = Array.isArray(res) ? res : res?.items || [];
        return rawList.map(mapBackendIncident);
      } catch (err) {
        console.warn('Backend unavailable, falling back to cached demo incidents:', err);
      }
    }

    // Demo / fallback mode
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
      filtered = filtered.filter((i) => i.districtName?.toLowerCase() === params.districtId?.toLowerCase());
    }
    return filtered;
  },

  getIncidentById: async (id: string): Promise<Incident | null> => {
    const isDemo = localStorage.getItem('aapadaops_demo_mode') === 'true';
    if (!isDemo) {
      try {
        const raw = await apiClient.get<any>(`/incidents/${id}`);
        return mapBackendIncident(raw);
      } catch (err) {
        console.warn('Backend getIncidentById failed, checking fallback:', err);
      }
    }
    return DEMO_INCIDENTS.find((i) => i.id === id || i.incidentCode === id) || null;
  },

  submitIncident: async (data: Partial<Incident>): Promise<Incident> => {
    const isDemo = localStorage.getItem('aapadaops_demo_mode') === 'true';
    if (!isDemo) {
      const payload = {
        title: `${data.hazardType || 'Flood'} reported at ${data.villageName || data.blockName || 'Odisha Sector'}`,
        description: data.rawDescription || 'Disaster report submitted via portal.',
        category: data.hazardType || 'FLOOD',
        reported_severity: data.reportedSeverity || 'HIGH',
        district_name: data.districtName || 'Puri',
        district_id: data.districtId,
        block_name: data.blockName || 'Puri Sadar',
        village_name: data.villageName || 'Sector Alpha',
        latitude: data.latitude || 19.8135,
        longitude: data.longitude || 85.8312,
        reporter_name: data.callerName || 'Public Reporter',
        reporter_phone: data.callerPhone || '+91 94370 00000',
        stranded_count: data.personsStranded || 0,
        estimated_affected_people: data.personsStranded || 1,
        casualties_reported: 0,
      };

      try {
        const response = await apiClient.post<any>('/incidents', payload);
        return mapBackendIncident(response);
      } catch (err) {
        console.warn('Direct submit failed, using fallback:', err);
      }
    }

    // Demo mode fallback
    const newInc: Incident = {
      id: 'inc_' + Math.random().toString(36).substring(2, 8),
      incidentCode: 'OD-2026-' + Math.floor(1000 + Math.random() * 9000),
      source: data.source || 'CITIZEN_WEB',
      status: 'NEEDS_VERIFICATION',
      callerName: data.callerName || 'Anonymous',
      callerPhone: data.callerPhone || '+91 94370 00000',
      latitude: data.latitude || 19.8135,
      longitude: data.longitude || 85.8312,
      addressText: data.addressText || 'District Sector',
      districtId: data.districtId || 'dst_puri',
      districtName: data.districtName || 'Puri',
      blockName: data.blockName || 'Puri Sadar',
      villageName: data.villageName || 'Coastal Area',
      hazardType: data.hazardType || 'FLOOD',
      reportedSeverity: data.reportedSeverity || 'HIGH',
      personsStranded: data.personsStranded || 1,
      hasVulnerablePeople: data.hasVulnerablePeople || false,
      rawDescription: data.rawDescription || '',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    DEMO_INCIDENTS.unshift(newInc);
    return newInc;
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
    const isDemo = localStorage.getItem('aapadaops_demo_mode') === 'true';
    if (!isDemo) {
      try {
        const payload = {
          status: data.status,
          verified_priority: data.verifiedPriority,
          verification_notes: data.verificationNotes || 'Verified by authorized officer.',
          rejection_reason: data.rejectionReason,
        };
        const res = await apiClient.post<any>(`/verification/${id}/verify`, payload);
        return mapBackendIncident(res);
      } catch (err) {
        console.warn('Backend verification call failed, falling back:', err);
      }
    }

    const inc = DEMO_INCIDENTS.find((i) => i.id === id);
    if (inc) {
      inc.status = data.status;
      inc.verifiedPriority = data.verifiedPriority;
      inc.verifiedAt = new Date().toISOString();
      inc.verifiedByName = 'Authorized Officer';
      if (data.rejectionReason) inc.rejectionReason = data.rejectionReason;
      if (data.status === 'DISPUTED') inc.disputeNotes = data.verificationNotes;
    }
    return inc || ({} as Incident);
  },

  linkDuplicate: async (childId: string, parentId: string): Promise<any> => {
    const isDemo = localStorage.getItem('aapadaops_demo_mode') === 'true';
    if (!isDemo) {
      try {
        return await apiClient.post<any>('/duplicates/merge', {
          primary_incident_id: parentId,
          duplicate_incident_ids: [childId],
          merge_notes: 'Duplicate consolidated by operational coordinator.',
        });
      } catch (err) {
        console.warn('Backend duplicate merge failed:', err);
      }
    }

    const child = DEMO_INCIDENTS.find((i) => i.id === childId);
    const parent = DEMO_INCIDENTS.find((i) => i.id === parentId);
    if (child && parent) {
      child.status = 'DUPLICATE';
      child.parentIncidentId = parentId;
      parent.duplicateCount = (parent.duplicateCount || 0) + 1;
      parent.personsStranded += child.personsStranded || 0;
    }
    return child;
  },

  getVerificationQueue: async (district?: string): Promise<Incident[]> => {
    const isDemo = localStorage.getItem('aapadaops_demo_mode') === 'true';
    if (!isDemo) {
      try {
        const query = district && district !== 'ALL' ? `?district=${district}` : '';
        const res = await apiClient.get<any[]>(`/verification/queue${query}`);
        return (res || []).map(mapBackendIncident);
      } catch (err) {
        console.warn('Backend queue fetch failed:', err);
      }
    }
    return DEMO_INCIDENTS.filter(
      (i) => i.status === 'SUBMITTED' || i.status === 'NEEDS_VERIFICATION'
    );
  },

  getDuplicateClusters: async (): Promise<any[]> => {
    const isDemo = localStorage.getItem('aapadaops_demo_mode') === 'true';
    if (!isDemo) {
      try {
        return await apiClient.get<any[]>('/duplicates/clusters');
      } catch (err) {
        console.warn('Backend duplicate clusters fetch failed:', err);
      }
    }
    return [];
  },
};
