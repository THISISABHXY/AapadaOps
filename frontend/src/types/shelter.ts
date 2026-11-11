export type ShelterStatus = 'OPERATIONAL' | 'ACTIVATED' | 'STANDBY' | 'FULL' | 'INACTIVE';

export interface CycloneShelter {
  id: string;
  code: string;
  name: string;
  districtId: string;
  districtName: string;
  blockId?: string;
  blockName: string;
  villageName?: string;
  latitude: number;
  longitude: number;
  totalCapacity: number;
  currentOccupancy: number;
  availableCapacity: number;
  occupancyRate: number;
  status: ShelterStatus;
  hasDgSet?: boolean;
  powerBackup?: boolean;
  dgFuelHours?: number;
  waterSupplyLitres?: number;
  waterSupplyDays?: number;
  dryRationsDays?: number;
  medicalKitReady?: boolean;
  medicalAidAvailable?: boolean;
  contactPerson?: string;
  contactPhone?: string;
  caretakerName?: string;
  caretakerPhone?: string;
  distanceKm?: number;
  lastUpdated: string;
}

