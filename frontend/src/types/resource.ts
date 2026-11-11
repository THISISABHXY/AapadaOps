export type ResourceCategory =
  | 'RESCUE_BOAT'
  | 'DEWATERING_PUMP'
  | 'CHAINSAW'
  | 'DG_SET'
  | 'RELIEF_KITS';

export type ResourceStatus = 'AVAILABLE' | 'DEPLOYED' | 'MAINTENANCE' | 'CONDEMNED';

export interface TacticalResource {
  id: string;
  assetCode: string;
  category: ResourceCategory;
  name: string;
  agency: 'ODRAF' | 'NDRF' | 'FIRE_SERVICES' | 'CIVIL_DEFENCE' | 'REVENUE';
  homeDepot: string;
  districtName: string;
  status: ResourceStatus;
  currentDeploymentTaskId?: string;
  currentDeploymentLocation?: string;
  fuelHoursRemaining?: number;
  conditionRating: 'EXCELLENT' | 'GOOD' | 'NEEDS_SERVICE';
  lastInspected: string;
}

