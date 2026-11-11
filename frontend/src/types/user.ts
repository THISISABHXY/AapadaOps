export type UserRole =
  | 'SUPER_ADMIN'
  | 'DISTRICT_ADMIN'
  | 'VERIFICATION_OFFICER'
  | 'RESPONSE_COORDINATOR'
  | 'FIELD_WORKER'
  | 'OBSERVER'
  | 'CITIZEN';

export interface User {
  id: string;
  email: string;
  fullName: string;
  role: UserRole;
  phone?: string;
  districtId?: string;
  districtName?: string;
  department?: string;
  isActive: boolean;
  createdAt: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}
