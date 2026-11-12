/**
 * AapadaOps Frontend API Layer.
 * Re-exports apiClient and core endpoints for standardized imports across the application.
 */

export { apiClient, publicApiClient } from '../services/apiClient';
export * from '../services/incidentService';
export * from '../services/alertService';
export * from '../services/shelterService';
export * from '../services/resourceService';
export * from '../services/analyticsService';
export * from '../services/coordinationService';
export * from '../services/taskService';
export * from '../services/auditService';
export * from '../services/aiService';
export * from '../services/evidenceService';

