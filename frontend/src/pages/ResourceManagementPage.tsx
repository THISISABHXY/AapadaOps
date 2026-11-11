import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Package,
  Plus,
  Search,
  Filter,
  CheckCircle2,
  Clock,
  Wrench,
  Download,
  Ship,
  Droplets,
  RefreshCw,
} from 'lucide-react';
import { GovCard } from '../components/ui/GovCard';
import { GovBadge } from '../components/ui/GovBadge';
import { GovButton } from '../components/ui/GovButton';
import { GovModal } from '../components/ui/GovModal';
import { resourceService } from '../services/resourceService';
import { useToast } from '../contexts/ToastContext';
import { TacticalResource, ResourceCategory } from '../types/resource';
import { formatDate } from '../utilities/formatters';

export const ResourceManagementPage: React.FC = () => {
  const { showToast } = useToast();
  const queryClient = useQueryClient();
  const [selectedCategory, setSelectedCategory] = useState<ResourceCategory | 'ALL'>('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [addModalOpen, setAddModalOpen] = useState(false);

  // New Equipment Form State
  const [newEquipName, setNewEquipName] = useState('');
  const [newEquipCat, setNewEquipCat] = useState('POWER_BOAT');
  const [newEquipOrg, setNewEquipOrg] = useState('ODRAF');
  const [newEquipDistrict, setNewEquipDistrict] = useState('Kendrapara');

  const { data: resources = [], isLoading, isFetching } = useQuery({
    queryKey: ['resources', selectedCategory],
    queryFn: () => resourceService.getResources(selectedCategory === 'ALL' ? undefined : selectedCategory),
    refetchInterval: 15000,
  });

  const createMutation = useMutation({
    mutationFn: (data: any) => resourceService.createResource(data),
    onSuccess: (newRes) => {
      queryClient.invalidateQueries({ queryKey: ['resources'] });
      showToast('success', 'Asset Registered', `Registered ${newRes.name} (${newRes.assetCode}) into ODRN database.`);
      setAddModalOpen(false);
      setNewEquipName('');
    },
    onError: (err: any) => {
      showToast('error', 'Registration Failed', err.message || 'Could not register equipment.');
    },
  });

  const handleRegisterAsset = () => {
    if (!newEquipName.trim()) {
      showToast('error', 'Required Field', 'Please enter asset name/specification.');
      return;
    }
    createMutation.mutate({
      name: newEquipName.trim(),
      category: newEquipCat,
      organization: newEquipOrg,
      district_name: newEquipDistrict,
      quantity: 1,
      unit_of_measure: 'unit',
    });
  };

  const filteredResources = resources.filter((res) => {
    const matchesCategory = selectedCategory === 'ALL' || res.category === selectedCategory;
    const matchesSearch =
      res.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      res.assetCode.toLowerCase().includes(searchQuery.toLowerCase()) ||
      res.homeDepot.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  return (
    <div className="space-y-4">
      {/* 1. Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-line">
        <div>
          <div className="flex items-center gap-2">
            <Package className="w-5 h-5 text-forest" />
            <h1 className="text-xl font-bold text-ink-primary tracking-tight">
              Tactical Resource & Equipment Management (ODRN)
            </h1>
            {isFetching && <RefreshCw className="w-3.5 h-3.5 text-sage animate-spin" />}
          </div>
          <p className="text-xs text-sage mt-0.5">
            Odisha Disaster Resource Network. Real-time dynamic inventory of rescue boats, dewatering pumps, chainsaws, and generator sets.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <GovButton
            variant="primary"
            size="sm"
            onClick={() => setAddModalOpen(true)}
            leftIcon={<Plus className="w-3.5 h-3.5" />}
          >
            Register Equipment
          </GovButton>
        </div>
      </div>

      {/* 2. Category Tabs & Search Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex flex-wrap gap-1 bg-white p-1 rounded border border-line">
          {[
            { id: 'ALL', label: 'All Equipment' },
            { id: 'RESCUE_BOAT', label: 'Rescue Boats' },
            { id: 'DEWATERING_PUMP', label: 'Dewatering Pumps' },
            { id: 'CHAINSAW', label: 'Chainsaws / JCB' },
            { id: 'DG_SET', label: 'DG Sets' },
            { id: 'RELIEF_KITS', label: 'Relief Rations' },
          ].map((cat) => (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id as any)}
              className={`px-3 py-1.5 text-xs font-semibold rounded cursor-pointer transition-colors ${
                selectedCategory === cat.id
                  ? 'bg-forest text-white'
                  : 'text-ink-secondary hover:text-ink-primary hover:bg-bg-warm'
              }`}
            >
              {cat.label}
            </button>
          ))}
        </div>

        <div className="relative w-full sm:w-64">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-sage" />
          <input
            type="text"
            placeholder="Search code, asset name, depot..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 text-xs bg-white border border-line rounded focus:outline-none focus:ring-1 focus:ring-forest text-ink-primary"
          />
        </div>
      </div>

      {/* 3. Practical Data Table */}
      <div className="bg-white rounded border border-line overflow-hidden shadow-xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-bg-warm text-sage font-semibold uppercase text-[11px] tracking-wider border-b border-line">
              <tr>
                <th className="px-4 py-2.5">Asset Code</th>
                <th className="px-4 py-2.5">Equipment Name</th>
                <th className="px-4 py-2.5">Operating Agency</th>
                <th className="px-4 py-2.5">Home Staging Depot</th>
                <th className="px-4 py-2.5">Current Status</th>
                <th className="px-4 py-2.5">Fuel / Readiness</th>
                <th className="px-4 py-2.5 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line text-ink-primary">
              {filteredResources.map((res) => (
                <tr key={res.id} className="hover:bg-bg-warm/60 transition-colors">
                  <td className="px-4 py-3 font-mono font-bold text-forest">{res.assetCode}</td>
                  <td className="px-4 py-3 font-medium">
                    <div>{res.name}</div>
                    <span className="text-[11px] font-mono text-sage">{res.category}</span>
                  </td>
                  <td className="px-4 py-3 font-mono text-ink-secondary">{res.agency}</td>
                  <td className="px-4 py-3 text-ink-secondary">{res.homeDepot}</td>
                  <td className="px-4 py-3">
                    <GovBadge
                      variant={
                        res.status === 'AVAILABLE'
                          ? 'forest'
                          : res.status === 'DEPLOYED'
                          ? 'amber'
                          : 'emergency'
                      }
                      size="sm"
                    >
                      {res.status}
                    </GovBadge>
                  </td>
                  <td className="px-4 py-3 font-mono">
                    {res.fuelHoursRemaining ? (
                      <span className="text-ink-primary font-semibold">
                        {res.fuelHoursRemaining}h Fuel
                      </span>
                    ) : (
                      <span className="text-forest font-semibold">{res.conditionRating}</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={() => alert(`Asset inspection details: ${res.assetCode}`)}
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

      {/* Register Asset Modal */}
      <GovModal
        isOpen={addModalOpen}
        onClose={() => setAddModalOpen(false)}
        title="Register Tactical Equipment in ODRN Database"
        description="Add newly requisitioned boats, dewatering pumps, or heavy chainsaws into District Inventory."
        footer={
          <>
            <GovButton variant="secondary" size="sm" onClick={() => setAddModalOpen(false)}>
              Cancel
            </GovButton>
            <GovButton
              variant="primary"
              size="sm"
              isLoading={createMutation.isPending}
              onClick={handleRegisterAsset}
            >
              Save Equipment to ODRN
            </GovButton>
          </>
        }
      >
        <div className="space-y-3">
          <div>
            <label className="text-xs font-semibold text-ink-primary block mb-1">Equipment Name / Description *</label>
            <input
              type="text"
              value={newEquipName}
              onChange={(e) => setNewEquipName(e.target.value)}
              placeholder="e.g. Aska Inflatable Motor Boat (8 Person)"
              className="w-full text-xs h-9 px-3 bg-white border border-line rounded text-ink-primary"
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-ink-primary block mb-1">Equipment Category *</label>
            <select
              value={newEquipCat}
              onChange={(e) => setNewEquipCat(e.target.value)}
              className="w-full text-xs h-9 px-3 bg-white border border-line rounded text-ink-primary"
            >
              <option value="POWER_BOAT">Power Rescue Boat (OBM 40HP)</option>
              <option value="INFLATABLE_BOAT">Inflatable Rescue Boat</option>
              <option value="DEWATERING_PUMP">High Capacity Dewatering Pump (1000 LPM)</option>
              <option value="JCB_EXCAVATOR">JCB / Heavy Earthmover</option>
              <option value="DIESEL_GENERATOR">Silent Diesel Generator (125 kVA)</option>
              <option value="EMERGENCY_RATION_KIT">Emergency Relief Dry Rations</option>
            </select>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs font-semibold text-ink-primary block mb-1">Operating Agency *</label>
              <select
                value={newEquipOrg}
                onChange={(e) => setNewEquipOrg(e.target.value)}
                className="w-full text-xs h-9 px-3 bg-white border border-line rounded text-ink-primary"
              >
                <option value="ODRAF">ODRAF</option>
                <option value="NDRF">NDRF</option>
                <option value="FIRE_SERVICES">Odisha Fire Services</option>
                <option value="CIVIL_DEFENCE">Civil Defence</option>
                <option value="REVENUE">Revenue & Disaster Mgmt</option>
              </select>
            </div>

            <div>
              <label className="text-xs font-semibold text-ink-primary block mb-1">Stationed District *</label>
              <select
                value={newEquipDistrict}
                onChange={(e) => setNewEquipDistrict(e.target.value)}
                className="w-full text-xs h-9 px-3 bg-white border border-line rounded text-ink-primary"
              >
                <option value="Kendrapara">Kendrapara</option>
                <option value="Puri">Puri</option>
                <option value="Bhadrak">Bhadrak</option>
                <option value="Balasore">Balasore</option>
                <option value="Jagatsinghpur">Jagatsinghpur</option>
                <option value="Ganjam">Ganjam</option>
              </select>
            </div>
          </div>
        </div>
      </GovModal>
    </div>
  );
};

