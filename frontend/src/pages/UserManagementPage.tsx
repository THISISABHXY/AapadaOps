import React, { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import {
  Users,
  UserPlus,
  Search,
  Shield,
  CheckCircle2,
  XCircle,
  Edit,
} from 'lucide-react';
import { GovCard } from '../components/ui/GovCard';
import { GovBadge } from '../components/ui/GovBadge';
import { GovButton } from '../components/ui/GovButton';
import { GovModal } from '../components/ui/GovModal';
import { useToast } from '../contexts/ToastContext';
import { User, UserRole } from '../types/user';
import { apiClient } from '../services/apiClient';
import { normalizeRole, toBackendRole } from '../contexts/AuthContext';

const INITIAL_USERS: User[] = [
  {
    id: 'usr_001',
    email: 'director@osdma.gov.in',
    fullName: 'Sri Pradeep Kumar Jena, IAS',
    role: 'SUPER_ADMIN',
    department: 'OSDMA State Command',
    isActive: true,
    createdAt: '2026-01-01T00:00:00Z',
  },
  {
    id: 'usr_002',
    email: 'collector.puri@nic.in',
    fullName: 'Dr. Siddharth Shankar Das, IAS',
    role: 'DISTRICT_ADMIN',
    districtName: 'Puri',
    department: 'District Disaster Management Authority',
    phone: '+919437011223',
    isActive: true,
    createdAt: '2026-01-01T00:00:00Z',
  },
  {
    id: 'usr_003',
    email: 'tahasildar.krushnaprasad@nic.in',
    fullName: 'Smt. Ananya Mishra, OAS',
    role: 'VERIFICATION_OFFICER',
    districtName: 'Puri',
    department: 'Revenue & Disaster Management',
    phone: '+919437022334',
    isActive: true,
    createdAt: '2026-01-01T00:00:00Z',
  },
  {
    id: 'usr_004',
    email: 'bdo.kakatpur@nic.in',
    fullName: 'Sri Rajesh Mohanty, OAS',
    role: 'RESPONSE_COORDINATOR',
    districtName: 'Puri',
    department: 'Panchayati Raj & Emergency Ops',
    phone: '+919437033445',
    isActive: true,
    createdAt: '2026-01-01T00:00:00Z',
  },
  {
    id: 'usr_005',
    email: 'odraf.unit03@odisha.gov.in',
    fullName: 'Inspector B. K. Nayak',
    role: 'FIELD_WORKER',
    districtName: 'Puri',
    department: 'ODRAF 3rd Battalion',
    phone: '+919437044556',
    isActive: true,
    createdAt: '2026-01-01T00:00:00Z',
  },
  {
    id: 'usr_006',
    email: 'ndma.liaison@nic.in',
    fullName: 'Col. R. S. Rathore',
    role: 'OBSERVER',
    department: 'National Disaster Management Authority',
    isActive: true,
    createdAt: '2026-01-01T00:00:00Z',
  },
];

export const UserManagementPage: React.FC = () => {
  const { showToast } = useToast();
  const queryClient = useQueryClient();

  const { data: users = INITIAL_USERS, isLoading } = useQuery({
    queryKey: ['users'],
    queryFn: async () => {
      try {
        const raw = await apiClient.get<any[]>('/users');
        if (Array.isArray(raw) && raw.length > 0) {
          return raw.map((u: any) => ({
            id: u.id,
            email: u.email,
            fullName: u.full_name || u.fullName,
            role: normalizeRole(u.role),
            districtName: u.jurisdiction_district || u.districtName || 'Puri',
            phone: u.phone_number || u.phone,
            department: u.badge_number || 'OSDMA Operations',
            isActive: Boolean(u.is_active ?? true),
            createdAt: u.created_at || '2026-01-01T00:00:00Z',
          }));
        }
      } catch (err) {
        console.warn('Backend users fetch failed, using fallback:', err);
      }
      return INITIAL_USERS;
    },
  });

  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState<string>('ALL');
  const [addModalOpen, setAddModalOpen] = useState(false);

  const [newEmail, setNewEmail] = useState('');
  const [newName, setNewName] = useState('');
  const [newRole, setNewRole] = useState<UserRole>('VERIFICATION_OFFICER');

  const filtered = users.filter((u) => {
    const matchesRole = roleFilter === 'ALL' || u.role === roleFilter;
    const matchesSearch =
      u.fullName.toLowerCase().includes(search.toLowerCase()) ||
      u.email.toLowerCase().includes(search.toLowerCase()) ||
      u.department?.toLowerCase().includes(search.toLowerCase());
    return matchesRole && matchesSearch;
  });

  const handleAddUser = async () => {
    if (!newEmail || !newName) return;
    try {
      await apiClient.post('/users', {
        email: newEmail.trim().toLowerCase(),
        password: 'Password@123',
        full_name: newName,
        role: toBackendRole(newRole),
        phone_number: '+91 94370 00000',
        jurisdiction_district: 'Puri',
        badge_number: `OSDMA-${newRole.substring(0, 3)}-${Math.floor(10 + Math.random() * 90)}`,
      });
      queryClient.invalidateQueries({ queryKey: ['users'] });
      showToast('success', 'User Provisioned', `Added ${newName} (${newRole}) to administrative roster.`);
      setAddModalOpen(false);
      setNewEmail('');
      setNewName('');
    } catch (err: any) {
      showToast('error', 'Registration Failed', err?.message || 'Could not create user.');
    }
  };

  return (
    <div className="space-y-4">
      {/* 1. Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-line">
        <div>
          <div className="flex items-center gap-2">
            <Users className="w-5 h-5 text-forest" />
            <h1 className="text-xl font-bold text-ink-primary tracking-tight">
              User Directory & Role-Based Access Control (RBAC)
            </h1>
          </div>
          <p className="text-xs text-sage mt-0.5">
            Manage authenticated credentials, department assignments, and permission boundaries across the 7 operational tiers.
          </p>
        </div>

        <GovButton
          variant="primary"
          size="sm"
          onClick={() => setAddModalOpen(true)}
          leftIcon={<UserPlus className="w-3.5 h-3.5" />}
        >
          Provision Officer
        </GovButton>
      </div>

      {/* 2. Filters */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-2 text-xs">
          <span className="font-semibold text-ink-primary">Role Filter:</span>
          <select
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
            className="text-xs bg-white border border-line rounded px-2.5 py-1.5 font-medium text-ink-primary"
          >
            <option value="ALL">All Roles ({users.length})</option>
            <option value="SUPER_ADMIN">Super Administrator</option>
            <option value="DISTRICT_ADMIN">District Administrator</option>
            <option value="VERIFICATION_OFFICER">Incident Verification Officer</option>
            <option value="RESPONSE_COORDINATOR">Response Coordinator</option>
            <option value="FIELD_WORKER">Field Worker</option>
            <option value="OBSERVER">Read-only Observer</option>
          </select>
        </div>

        <div className="relative w-full sm:w-64">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-sage" />
          <input
            type="text"
            placeholder="Search officer name, email..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 text-xs bg-white border border-line rounded focus:outline-none focus:ring-1 focus:ring-forest text-ink-primary"
          />
        </div>
      </div>

      {/* 3. Table */}
      <div className="bg-white rounded border border-line overflow-hidden shadow-xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-bg-warm text-sage font-semibold uppercase text-[11px] tracking-wider border-b border-line">
              <tr>
                <th className="px-4 py-2.5">Officer Name</th>
                <th className="px-4 py-2.5">Official Email</th>
                <th className="px-4 py-2.5">Assigned Role</th>
                <th className="px-4 py-2.5">Department / Jurisdiction</th>
                <th className="px-4 py-2.5">Contact Phone</th>
                <th className="px-4 py-2.5">Status</th>
                <th className="px-4 py-2.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line text-ink-primary">
              {filtered.map((u) => (
                <tr key={u.id} className="hover:bg-bg-warm/60 transition-colors">
                  <td className="px-4 py-3 font-semibold text-ink-primary">{u.fullName}</td>
                  <td className="px-4 py-3 font-mono text-sage">{u.email}</td>
                  <td className="px-4 py-3">
                    <GovBadge
                      variant={
                        u.role === 'SUPER_ADMIN'
                          ? 'emergency'
                          : u.role === 'DISTRICT_ADMIN'
                          ? 'amber'
                          : 'forest'
                      }
                      size="sm"
                    >
                      {u.role}
                    </GovBadge>
                  </td>
                  <td className="px-4 py-3 text-ink-secondary">
                    <div>{u.department}</div>
                    {u.districtName && (
                      <span className="font-mono text-[10px] text-sage">{u.districtName} District</span>
                    )}
                  </td>
                  <td className="px-4 py-3 font-mono text-sage">{u.phone || '—'}</td>
                  <td className="px-4 py-3">
                    <span className="inline-flex items-center gap-1 font-mono text-xs text-forest font-semibold">
                      <CheckCircle2 className="w-3.5 h-3.5" /> Active
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={() => alert(`View audit log for ${u.fullName}`)}
                      className="text-xs font-semibold text-forest hover:underline"
                    >
                      Audit
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Provision Officer Modal */}
      <GovModal
        isOpen={addModalOpen}
        onClose={() => setAddModalOpen(false)}
        title="Provision New Government Response Officer"
        description="Assign authorized role and jurisdiction for OSDMA or District Disaster Operations."
        footer={
          <>
            <GovButton variant="secondary" size="sm" onClick={() => setAddModalOpen(false)}>
              Cancel
            </GovButton>
            <GovButton variant="primary" size="sm" onClick={handleAddUser}>
              Provision Credentials
            </GovButton>
          </>
        }
      >
        <div className="space-y-3">
          <div>
            <label className="text-xs font-semibold text-ink-primary block mb-1">Full Official Name *</label>
            <input
              type="text"
              placeholder="e.g. Sri Manoj Kumar Mohanty, OAS"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              className="w-full text-xs h-9 px-3 bg-white border border-line rounded text-ink-primary"
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-ink-primary block mb-1">NIC / Official Email *</label>
            <input
              type="email"
              placeholder="officer@nic.in"
              value={newEmail}
              onChange={(e) => setNewEmail(e.target.value)}
              className="w-full text-xs h-9 px-3 bg-white border border-line rounded text-ink-primary font-mono"
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-ink-primary block mb-1">Designated Role *</label>
            <select
              value={newRole}
              onChange={(e) => setNewRole(e.target.value as UserRole)}
              className="w-full text-xs h-9 px-3 bg-white border border-line rounded text-ink-primary"
            >
              <option value="DISTRICT_ADMIN">District Administrator (Collector)</option>
              <option value="VERIFICATION_OFFICER">Incident Verification Officer (Tahasildar / RI)</option>
              <option value="RESPONSE_COORDINATOR">Response Coordinator (BDO / Fire Officer)</option>
              <option value="FIELD_WORKER">Field Worker (ODRAF / Aapda Mitra)</option>
              <option value="OBSERVER">Read-only Observer (NDMA / Media)</option>
            </select>
          </div>
        </div>
      </GovModal>
    </div>
  );
};

