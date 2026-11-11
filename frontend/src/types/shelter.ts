export type ShelterStatus = 'OPERATIONAL' | 'ACTIVATED' | 'STANDBY' | 'FULL' | 'INACTIVE';

export interface CycloneShelter {
  id: string;
  code: string;
  name: string;
  districtId: string;
  districtName: string;
  blockId: string;
  blockName: string;
  latitude: number;
  longitude: number;
  totalCapacity: number;
  currentOccupancy: number;
  availableCapacity: number;
  occupancyRate: number;
  status: ShelterStatus;
  hasDgSet: boolean;
  dgFuelHours: number;
  waterSupplyLitres: number;
  dryRationsDays: number;
  medicalKitReady: boolean;
  contactPerson: string;
  contactPhone: string;
  distanceKm?: number;
  lastUpdated: string;
}

