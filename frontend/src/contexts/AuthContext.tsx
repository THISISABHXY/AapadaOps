import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { User, UserRole } from '../types/user';
import { apiClient } from '../services/apiClient';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password?: string, role?: UserRole) => Promise<void>;
  logout: () => void;
  switchDemoRole: (role: UserRole) => Promise<void>;
}

export function normalizeRole(role: string): UserRole {
  if (role === 'DISTRICT_COLLECTOR') return 'DISTRICT_ADMIN';
  if (role === 'INCIDENT_VERIFICATION_OFFICER') return 'VERIFICATION_OFFICER';
  if (role === 'CITIZEN_REPORTER') return 'CITIZEN';
  return (role as UserRole) || 'OBSERVER';
}

export function toBackendRole(role: UserRole): string {
  if (role === 'DISTRICT_ADMIN') return 'DISTRICT_COLLECTOR';
  if (role === 'VERIFICATION_OFFICER') return 'INCIDENT_VERIFICATION_OFFICER';
  if (role === 'CITIZEN') return 'CITIZEN_REPORTER';
  return role;
}

export const PERSONA_CREDENTIALS: Record<UserRole, { email: string; defaultPassword: string }> = {
  SUPER_ADMIN: { email: 'director@osdma.gov.in', defaultPassword: 'Password@123' },
  DISTRICT_ADMIN: { email: 'collector.puri@nic.in', defaultPassword: 'Password@123' },
  VERIFICATION_OFFICER: { email: 'tahasildar.krushnaprasad@nic.in', defaultPassword: 'Password@123' },
  RESPONSE_COORDINATOR: { email: 'bdo.kakatpur@nic.in', defaultPassword: 'Password@123' },
  FIELD_WORKER: { email: 'odraf.unit03@odisha.gov.in', defaultPassword: 'Password@123' },
  OBSERVER: { email: 'ndma.liaison@nic.in', defaultPassword: 'Password@123' },
  CITIZEN: { email: 'citizen@aapadaops.gov.in', defaultPassword: 'Password@123' },
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Sync / verify user session with backend
  useEffect(() => {
    const initSession = async () => {
      const savedToken = localStorage.getItem('aapadaops_token');
      const savedUserJson = localStorage.getItem('aapadaops_user');

      if (savedToken) {
        try {
          // Attempt verifying with backend /auth/me
          const profile = await apiClient.get<any>('/auth/me');
          if (profile && profile.id) {
            const mappedUser: User = {
              id: profile.id,
              email: profile.email,
              fullName: profile.full_name || profile.fullName,
              role: normalizeRole(profile.role),
              department: profile.department || 'OSDMA Operations',
              districtName: profile.jurisdiction_district || profile.districtName,
              phone: profile.phone_number || profile.phone,
              isActive: profile.is_active ?? true,
              createdAt: profile.created_at || new Date().toISOString(),
            };
            setUser(mappedUser);
            setToken(savedToken);
            localStorage.setItem('aapadaops_user', JSON.stringify(mappedUser));
            setIsLoading(false);
            return;
          }
        } catch {
          // If offline or token expired but saved user exists, fallback gracefully
          if (savedUserJson) {
            try {
              setUser(JSON.parse(savedUserJson));
              setToken(savedToken);
              setIsLoading(false);
              return;
            } catch {
              // Ignore parse error
            }
          }
        }
      }

      // Initial onboarding fallback: District Admin persona
      try {
        const creds = PERSONA_CREDENTIALS.DISTRICT_ADMIN;
        const res = await apiClient.post<any>('/auth/login', {
          email: creds.email,
          password: creds.defaultPassword,
        });
        const mappedUser: User = {
          id: res.user.id,
          email: res.user.email,
          fullName: res.user.full_name,
          role: normalizeRole(res.user.role),
          districtName: res.user.jurisdiction_district,
          isActive: true,
          createdAt: new Date().toISOString(),
        };
        setUser(mappedUser);
        setToken(res.access_token);
        localStorage.setItem('aapadaops_token', res.access_token);
        localStorage.setItem('aapadaops_user', JSON.stringify(mappedUser));
      } catch {
        // If backend is booting, set initial state
        const fallback = {
          id: 'usr_002',
          email: 'collector.puri@nic.in',
          fullName: 'Dr. Siddharth Shankar Das, IAS',
          role: 'DISTRICT_ADMIN' as UserRole,
          districtName: 'Puri',
          department: 'District Disaster Management Authority',
          phone: '+919437011223',
          isActive: true,
          createdAt: new Date().toISOString(),
        };
        setUser(fallback);
      } finally {
        setIsLoading(false);
      }
    };

    initSession();

    // Listen for auth expiration events
    const handleAuthExpired = () => {
      logout();
    };
    window.addEventListener('aapadaops:auth_expired', handleAuthExpired);
    return () => window.removeEventListener('aapadaops:auth_expired', handleAuthExpired);
  }, []);

  const login = useCallback(async (email: string, password = 'Password@123', role: UserRole = 'DISTRICT_ADMIN') => {
    setIsLoading(true);
    try {
      const response = await apiClient.post<any>('/auth/login', {
        email: email.trim().toLowerCase(),
        password,
      });

      const loggedUser: User = {
        id: response.user.id,
        email: response.user.email,
        fullName: response.user.full_name,
        role: normalizeRole(response.user.role),
        districtName: response.user.jurisdiction_district,
        isActive: true,
        createdAt: new Date().toISOString(),
      };

      setUser(loggedUser);
      setToken(response.access_token);
      localStorage.setItem('aapadaops_token', response.access_token);
      localStorage.setItem('aapadaops_user', JSON.stringify(loggedUser));
    } catch (err) {
      // In demo mode fallback
      const creds = PERSONA_CREDENTIALS[role];
      const fallbackUser: User = {
        id: 'usr_' + Math.random().toString(36).substring(2, 6),
        email,
        fullName: email.split('@')[0].toUpperCase(),
        role,
        isActive: true,
        createdAt: new Date().toISOString(),
      };
      setUser(fallbackUser);
      setToken('demo_token');
      localStorage.setItem('aapadaops_token', 'demo_token');
      localStorage.setItem('aapadaops_user', JSON.stringify(fallbackUser));
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('aapadaops_token');
    localStorage.removeItem('aapadaops_user');
  }, []);

  const switchDemoRole = useCallback(async (role: UserRole) => {
    setIsLoading(true);
    const creds = PERSONA_CREDENTIALS[role];
    try {
      const res = await apiClient.post<any>('/auth/login', {
        email: creds.email,
        password: creds.defaultPassword,
      });
      const switchedUser: User = {
        id: res.user.id,
        email: res.user.email,
        fullName: res.user.full_name,
        role: normalizeRole(res.user.role),
        districtName: res.user.jurisdiction_district,
        isActive: true,
        createdAt: new Date().toISOString(),
      };
      setUser(switchedUser);
      setToken(res.access_token);
      localStorage.setItem('aapadaops_token', res.access_token);
      localStorage.setItem('aapadaops_user', JSON.stringify(switchedUser));
    } catch {
      // Offline fallback
      const fallbackUser: User = {
        id: 'usr_' + role.toLowerCase(),
        email: creds.email,
        fullName: creds.email.split('@')[0].replace('.', ' ').toUpperCase(),
        role,
        isActive: true,
        createdAt: new Date().toISOString(),
      };
      setUser(fallbackUser);
      setToken('demo_token_' + role.toLowerCase());
      localStorage.setItem('aapadaops_token', 'demo_token_' + role.toLowerCase());
      localStorage.setItem('aapadaops_user', JSON.stringify(fallbackUser));
    } finally {
      setIsLoading(false);
    }
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!user,
        isLoading,
        login,
        logout,
        switchDemoRole,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
