import { apiClient } from './apiClient';

export interface AuditLogItem {
  id: string;
  action: string;
  entity_type: string;
  entity_id: string;
  actor_id?: string;
  actor_email?: string;
  actor_name?: string;
  actor_role?: string;
  description: string;
  ip_address?: string;
  created_at: string;
}

export const auditService = {
  getAuditLogs: async (params?: {
    entityType?: string;
    action?: string;
    limit?: number;
    skip?: number;
  }): Promise<AuditLogItem[]> => {
    const isDemo = localStorage.getItem('aapadaops_demo_mode') === 'true';
    if (!isDemo) {
      try {
        const query = new URLSearchParams();
        if (params?.entityType) query.set('entity_type', params.entityType);
        if (params?.action) query.set('action', params.action);
        if (params?.limit) query.set('limit', String(params.limit));
        if (params?.skip) query.set('skip', String(params.skip));

        return await apiClient.get<AuditLogItem[]>(`/audit-logs?${query.toString()}`);
      } catch (err) {
        console.warn('Backend audit logs fetch failed:', err);
      }
    }

    // Default mock audit trail
    return [
      {
        id: 'aud_01',
        action: 'VERIFY_INCIDENT',
        entity_type: 'INCIDENT',
        entity_id: 'inc_0891',
        actor_name: 'Subhashree Mohanty, OAS',
        actor_role: 'INCIDENT_VERIFICATION_OFFICER',
        description: 'Verified Brahmani saline bundh breach at Rajnagar with CRITICAL priority.',
        created_at: new Date(Date.now() - 3600000).toISOString(),
      },
      {
        id: 'aud_02',
        action: 'DISPATCH_TASK',
        entity_type: 'TASK',
        entity_id: 'tsk_401',
        actor_name: 'Commander Bikram Keshari Ray',
        actor_role: 'RESPONSE_COORDINATOR',
        description: 'Dispatched 4th ODRAF Unit Cuttack to Bhattarika islet rescue mission.',
        created_at: new Date(Date.now() - 7200000).toISOString(),
      },
    ];
  },
};
