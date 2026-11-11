import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  ShieldAlert,
  Search,
  Building2,
  PhoneCall,
  Droplets,
  Zap,
  Users,
  Edit2,
  CheckCircle2,
  RefreshCw,
} from 'lucide-react';
import { GovCard } from '../components/ui/GovCard';
import { GovBadge } from '../components/ui/GovBadge';
import { GovButton } from '../components/ui/GovButton';
import { GovModal } from '../components/ui/GovModal';
import { shelterService } from '../services/shelterService';
import { useToast } from '../contexts/ToastContext';
import { ODISHA_DISTRICTS } from '../services/demoDataService';
import { CycloneShelter } from '../types/shelter';
import { formatCoordinates } from '../utilities/formatters';

export const SheltersPage: React.FC = () => {
  const { showToast } = useToast();
  const queryClient = useQueryClient();
  const [search, setSearch] = useState('');
  const [selectedDistrict, setSelectedDistrict] = useState('ALL');

  // Edit Headcount Modal
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [targetShelter, setTargetShelter] = useState<CycloneShelter | null>(null);
  const [newOccupancy, setNewOccupancy] = useState<number>(0);

  const { data: shelters = [], isLoading, isFetching } = useQuery({
    queryKey: ['shelters', selectedDistrict],
    queryFn: () => shelterService.getShelters(selectedDistrict),
    refetchInterval: 15000,
  });

  const updateOccupancyMutation = useMutation({
    mutationFn: ({ id, count }: { id: string; count: number }) =>
      shelterService.updateOccupancy(id, count),
    onSuccess: (updated) => {
      queryClient.invalidateQueries({ queryKey: ['shelters'] });
      showToast('success', 'Shelter Occupancy Updated', `Recorded ${updated.currentOccupancy} evacuees at ${updated.name}`);
      setEditModalOpen(false);
    },
    onError: (err: any) => {
      showToast('error', 'Update Failed', err.message || 'Could not record headcount.');
    },
  });

  const filtered = shelters.filter((s) => {
    const matchesDistrict = selectedDistrict === 'ALL' || s.districtName?.toLowerCase() === selectedDistrict.toLowerCase();
    const matchesSearch =
      s.name.toLowerCase().includes(search.toLowerCase()) ||
      s.code.toLowerCase().includes(search.toLowerCase()) ||
      s.blockName.toLowerCase().includes(search.toLowerCase());
    return matchesDistrict && matchesSearch;
  });

  const openEditModal = (shelter: CycloneShelter) => {
    setTargetShelter(shelter);
    setNewOccupancy(shelter.currentOccupancy);
    setEditModalOpen(true);
  };

  const handleSaveOccupancy = () => {
    if (!targetShelter) return;
    updateOccupancyMutation.mutate({
      id: targetShelter.id,
      count: Number(newOccupancy),
    });
  };

  return (
    <div className="space-y-4">
      {/* 1. Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-line">
        <div>
          <div className="flex items-center gap-2">
            <Building2 className="w-5 h-5 text-forest" />
            <h1 className="text-xl font-bold text-ink-primary tracking-tight">
              Multi-Purpose Cyclone & Flood Shelter Management
            </h1>
            {isFetching && <RefreshCw className="w-3.5 h-3.5 text-sage animate-spin" />}
          </div>
          <p className="text-xs text-sage mt-0.5">
            Real-time occupancy tracking, drinking water reserves, dry rations, and diesel generator fuel monitoring for Odisha's 800+ Cyclone Shelters.
          </p>
        </div>

        <div className="flex items-center gap-2 text-xs font-mono">
          <span className="bg-forest-subtle text-forest border border-forest/30 px-2.5 py-1 rounded font-bold">
            Total Capacity: {shelters.reduce((acc, s) => acc + s.totalCapacity, 0).toLocaleString()}
          </span>
          <span className="bg-white border border-line px-2.5 py-1 rounded font-semibold text-ink-primary">
            Current Evacuees: {shelters.reduce((acc, s) => acc + s.currentOccupancy, 0).toLocaleString()}
          </span>
        </div>
      </div>

      {/* 2. Filters */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-ink-primary">District:</span>
          <select
            value={selectedDistrict}
            onChange={(e) => setSelectedDistrict(e.target.value)}
            className="text-xs bg-white border border-line rounded px-2.5 py-1.5 font-medium text-ink-primary"
          >
            <option value="ALL">All Coastal Districts</option>
            {ODISHA_DISTRICTS.map((d) => (
              <option key={d} value={d}>
                {d}
              </option>
            ))}
          </select>
        </div>

        <div className="relative w-full sm:w-72">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-sage" />
          <input
            type="text"
            placeholder="Search shelter name, code, or block..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 text-xs bg-white border border-line rounded focus:outline-none focus:ring-1 focus:ring-forest text-ink-primary"
          />
        </div>
      </div>

      {/* 3. Shelter Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((s) => (
          <GovCard key={s.id} padding="md" className="space-y-3">
            <div className="flex items-start justify-between gap-2">
              <div>
                <span className="font-mono text-[10px] text-sage block">{s.code}</span>
                <h3 className="font-semibold text-sm text-ink-primary leading-snug">{s.name}</h3>
                <span className="text-xs text-sage">{s.blockName} Block, {s.districtName}</span>
              </div>
              <GovBadge
                variant={s.occupancyRate >= 0.9 ? 'emergency' : s.occupancyRate >= 0.7 ? 'amber' : 'forest'}
                size="sm"
              >
                {s.status}
              </GovBadge>
            </div>

            {/* Occupancy Meter */}
            <div className="space-y-1">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-sage">Occupancy: {s.currentOccupancy} / {s.totalCapacity}</span>
                <strong className="text-ink-primary">{Math.round(s.occupancyRate * 100)}%</strong>
              </div>
              <div className="w-full bg-bg-subtle h-2 rounded overflow-hidden">
                <div
                  className={`h-full rounded ${
                    s.occupancyRate >= 0.9 ? 'bg-emergency' : s.occupancyRate >= 0.7 ? 'bg-amber' : 'bg-forest'
                  }`}
                  style={{ width: `${Math.min(100, s.occupancyRate * 100)}%` }}
                />
              </div>
            </div>

            {/* Lifeline Gauges Grid */}
            <div className="p-2.5 bg-bg-warm rounded border border-line grid grid-cols-3 text-center text-xs font-mono">
              <div>
                <span className="text-sage block text-[10px]">Water Supply</span>
                <strong className="text-ink-primary">{s.waterSupplyLitres} L</strong>
              </div>
              <div>
                <span className="text-sage block text-[10px]">Dry Rations</span>
                <strong className="text-ink-primary">{s.dryRationsDays} Days</strong>
              </div>
              <div>
                <span className="text-sage block text-[10px]">DG Fuel</span>
                <strong className="text-ink-primary">{s.dgFuelHours} Hrs</strong>
              </div>
            </div>

            <div className="pt-2 border-t border-line flex items-center justify-between text-xs">
              <div className="font-mono text-[11px] text-sage">
                {formatCoordinates(s.latitude, s.longitude)}
              </div>
              <GovButton
                variant="secondary"
                size="sm"
                onClick={() => openEditModal(s)}
                leftIcon={<Edit2 className="w-3 h-3 text-forest" />}
              >
                Update Headcount
              </GovButton>
            </div>
          </GovCard>
        ))}
      </div>

      {/* Headcount Update Modal */}
      {targetShelter && (
        <GovModal
          isOpen={editModalOpen}
          onClose={() => setEditModalOpen(false)}
          title={`Update Evacuee Headcount — ${targetShelter.name}`}
          description={`Total capacity: ${targetShelter.totalCapacity} persons.`}
          footer={
            <>
              <GovButton variant="secondary" size="sm" onClick={() => setEditModalOpen(false)}>
                Cancel
              </GovButton>
              <GovButton
                variant="primary"
                size="sm"
                isLoading={updateOccupancyMutation.isPending}
                onClick={handleSaveOccupancy}
              >
                Save Headcount
              </GovButton>
            </>
          }
        >
          <div className="space-y-4">
            <div>
              <label className="text-xs font-semibold text-ink-primary block mb-1">
                Current Evacuee Headcount *
              </label>
              <input
                type="number"
                value={newOccupancy}
                onChange={(e) => setNewOccupancy(Number(e.target.value))}
                min={0}
                max={targetShelter.totalCapacity + 200}
                className="w-full text-sm font-mono h-10 px-3 bg-white border border-line rounded text-ink-primary"
              />
              <span className="text-[11px] text-sage mt-1 block">
                Occupancy will calculate to{' '}
                <strong>{Math.round((newOccupancy / targetShelter.totalCapacity) * 100)}%</strong>.
              </span>
            </div>
          </div>
        </GovModal>
      )}
    </div>
  );
};

