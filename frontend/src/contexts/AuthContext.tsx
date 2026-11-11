import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { User, UserRole } from '../types/user';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, role?: UserRole) => Promise<void>;
  logout: () => void;
  switchDemoRole: (role: UserRole) => void;
}

const DEMO_PERSONAS: Record<UserRole, User> = {
  SUPER_ADMIN: {
    id: 'usr_001',
    email: 'director@osdma.gov.in',
    fullName: 'Sri Pradeep Kumar Jena, IAS',
    role: 'SUPER_ADMIN',
    department: 'OSDMA State Command',
    isActive: true,
    createdAt: '2026-01-01T00:00:00Z',
  },
  DISTRICT_ADMIN: {
    id: 'usr_002',
    email: 'collector.puri@nic.in',
    fullName: 'Dr. Siddharth Shankar Das, IAS',
    role: 'DISTRICT_ADMIN',
    districtId: 'dst_puri',
    districtName: 'Puri',
    department: 'District Disaster Management Authority',
    phone: '+919437011223',
    isActive: true,
    createdAt: '2026-01-01T00:00:00Z',
  },
  VERIFICATION_OFFICER: {
    id: 'usr_003',
    email: 'tahasildar.krushnaprasad@nic.in',
    fullName: 'Smt. Ananya Mishra, OAS',
    role: 'VERIFICATION_OFFICER',
    districtId: 'dst_puri',
    districtName: 'Puri',
    department: 'Revenue & Disaster Management Dept',
    phone: '+919437022334',
    isActive: true,
    createdAt: '2026-01-01T00:00:00Z',
  },
  RESPONSE_COORDINATOR: {
    id: 'usr_004',
    email: 'bdo.kakatpur@nic.in',
    fullName: 'Sri Rajesh Mohanty, OAS',
    role: 'RESPONSE_COORDINATOR',
    districtId: 'dst_puri',
    districtName: 'Puri',
    department: 'Panchayati Raj & Emergency Ops',
    phone: '+919437033445',
    isActive: true,
    createdAt: '2026-01-01T00:00:00Z',
  },
  FIELD_WORKER: {
    id: 'usr_005',
    email: 'odraf.unit03@odisha.gov.in',
    fullName: 'Inspector B. K. Nayak',
    role: 'FIELD_WORKER',
    districtId: 'dst_puri',
    districtName: 'Puri',
    department: 'ODRAF 3rd Battalion',
    phone: '+919437044556',
    isActive: true,
    createdAt: '2026-01-01T00:00:00Z',
  },
  OBSERVER: {
    id: 'usr_006',
    email: 'ndma.liaison@nic.in',
    fullName: 'Col. R. S. Rathore',
    role: 'OBSERVER',
    department: 'National Disaster Management Authority',
    isActive: true,
    createdAt: '2026-01-01T00:00:00Z',
  },
  CITIZEN: {
    id: 'usr_007',
    email: 'citizen@aapadaops.gov.in',
    fullName: 'Public Citizen Reporter',
    role: 'CITIZEN',
    isActive: true,
    createdAt: '2026-01-01T00:00:00Z',
  },
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    // Check saved session
    const savedToken = localStorage.getItem('aapadaops_token');
    const savedUserJson = localStorage.getItem('aapadaops_user');
    if (savedToken && savedUserJson) {
      try {
        setUser(JSON.parse(savedUserJson));
        setToken(savedToken);
      } catch {
        localStorage.removeItem('aapadaops_token');
        localStorage.removeItem('aapadaops_user');
      }
    } else {
      // Default to District Administrator demo session for rapid prototyping
      const defaultUser = DEMO_PERSONAS.DISTRICT_ADMIN;
      setUser(defaultUser);
      setToken('demo_jwt_token_district_admin');
      localStorage.setItem('aapadaops_token', 'demo_jwt_token_district_admin');
      localStorage.setItem('aapadaops_user', JSON.stringify(defaultUser));
    }
    setIsLoading(false);
  }, []);

  const login = useCallback(async (email: string, role: UserRole = 'DISTRICT_ADMIN') => {
    setIsLoading(true);
    // Find matching persona or synthesize
    const persona = Object.values(DEMO_PERSONAS).find((p) => p.email.toLowerCase() === email.toLowerCase()) || {
      ...DEMO_PERSONAS[role],
      email,
      fullName: email.split('@')[0].toUpperCase(),
    };
    const demoToken = 'jwt_' + Math.random().toString(36).substring(2);
    setUser(persona);
    setToken(demoToken);
    localStorage.setItem('aapadaops_token', demoToken);
    localStorage.setItem('aapadaops_user', JSON.stringify(persona));
    setIsLoading(false);
  }, []);

  const logout = useCallback(() => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('aapadaops_token');
    localStorage.removeItem('aapadaops_user');
  }, []);

  const switchDemoRole = useCallback((role: UserRole) => {
    const persona = DEMO_PERSONAS[role];
    if (persona) {
      setUser(persona);
      const demoToken = 'demo_jwt_' + role.toLowerCase();
      setToken(demoToken);
      localStorage.setItem('aapadaops_token', demoToken);
      localStorage.setItem('aapadaops_user', JSON.stringify(persona));
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

