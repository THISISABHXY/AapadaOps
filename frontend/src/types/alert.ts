import { HazardType } from './incident';

export type AlertSeverityTier = 'GREEN' | 'YELLOW' | 'ORANGE' | 'RED';

export interface DisasterAlert {
  id: string;
  alertCode: string;
  hazardType: HazardType;
  severityTier: AlertSeverityTier;
  titleEn: string;
  titleOr: string;
  descriptionEn: string;
  descriptionOr: string;
  affectedDistricts: string[];
  effectiveFrom: string;
  expiresAt: string;
  windSpeedKmph?: number;
  rainfallForecastMm?: number;
  instructionsEn: string;
  instructionsOr: string;
  createdByName: string;
  createdAt: string;
  isActive: boolean;
}
