import { apiClient } from './apiClient';

export interface ExtractedIncident {
  incident_category: string;
  district: string;
  location_description: string;
  description: string;
  severity_indicators: string[];
  stranded_count: number;
  casualties_count: number;
  medical_urgency: string;
  resource_requirements: string[];
  confidence_score: number;
  missing_fields: string[];
}

export interface PrioritizationResult {
  incident_id: string;
  priority_score: number;
  recommended_level: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  reasoning_factors: string[];
  scoring_breakdown: Record<string, number>;
  deductions_applied: string[];
}

export interface CopilotSopResponse {
  query: string;
  verified_answer: string;
  retrieved_passages: Array<{
    title: string;
    text: string;
    authority: string;
    relevance_score: number;
  }>;
  hallucination_risk_score: number;
  is_verified_standard: boolean;
}

export const aiService = {
  extractStructuredIncident: async (
    rawText: string,
    language = 'en',
    source = 'PORTAL'
  ): Promise<ExtractedIncident> => {
    return apiClient.post<ExtractedIncident>('/ai/extract', {
      raw_text: rawText,
      language,
      source,
    });
  },

  prioritizeIncident: async (data: {
    incident_id: string;
    threat_to_life: boolean;
    medical_urgency: 'NONE' | 'MODERATE' | 'CRITICAL';
    people_affected: number;
    accessibility: 'NORMAL' | 'DEGRADED' | 'CUT_OFF';
    resource_requirements: string[];
    report_freshness_hours: number;
    verification_status: string;
  }): Promise<PrioritizationResult> => {
    return apiClient.post<PrioritizationResult>('/ai/prioritize', data);
  },

  querySopCopilot: async (query: string, topK = 3): Promise<CopilotSopResponse> => {
    return apiClient.post<CopilotSopResponse>('/ai/copilot-sop', {
      query,
      top_k: topK,
    });
  },

  transcribeAudio: async (
    audioBase64: string,
    language = 'od'
  ): Promise<{
    transcript: string;
    language_detected: string;
    confidence_score: number;
    is_low_confidence: boolean;
    audio_reference_id: string;
  }> => {
    return apiClient.post('/ai/transcribe', {
      audio_base64: audioBase64,
      language,
    });
  },
};

