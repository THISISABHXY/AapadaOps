import { apiClient } from './apiClient';

export interface EvidenceResponse {
  id: string;
  incident_id?: string;
  task_id?: string;
  report_id?: string;
  file_name: string;
  file_size_bytes: number;
  mime_type: string;
  sha256_hash: string;
  is_verified: boolean;
  created_at: string;
}

export const evidenceService = {
  uploadFile: async (
    file: File,
    options?: {
      incidentId?: string;
      taskId?: string;
      reportId?: string;
    }
  ): Promise<EvidenceResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    if (options?.incidentId) formData.append('incident_id', options.incidentId);
    if (options?.taskId) formData.append('task_id', options.taskId);
    if (options?.reportId) formData.append('report_id', options.reportId);

    return apiClient.upload<EvidenceResponse>('/evidence/upload', formData);
  },

  getFileUrl: (fileId: string): string => {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
    return `${baseUrl}/evidence/download/${fileId}`;
  },
};
