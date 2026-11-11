import React, { useState } from 'react';
import {
  Radio,
  Ship,
  MapPin,
  Clock,
  ShieldAlert,
  ArrowRight,
  CheckCircle2,
  Navigation,
} from 'lucide-react';
import { GovCard } from '../components/ui/GovCard';
import { GovBadge } from '../components/ui/GovBadge';
import { GovButton } from '../components/ui/GovButton';
import { taskService } from '../services/taskService';
import { useToast } from '../contexts/ToastContext';
import {
  DEMO_INCIDENTS,
  DEMO_TACTICAL_UNITS,
} from '../services/demoDataService';
import { Incident } from '../types/incident';
import { TacticalUnit } from '../types/task';
import { formatCoordinates } from '../utilities/formatters';

export const ResponseCoordinationPage: React.FC = () => {
  const { showToast } = useToast();
  const eligibleIncidents = DEMO_INCIDENTS.filter(
    (i) => i.status === 'VERIFIED' || i.status === 'NEEDS_VERIFICATION'
  );

  const [selectedIncident, setSelectedIncident] = useState<Incident>(eligibleIncidents[0]);
  const [selectedUnit, setSelectedUnit] = useState<TacticalUnit>(DEMO_TACTICAL_UNITS[0]);
  const [slaHours, setSlaHours] = useState<number>(2);
  const [isDispatching, setIsDispatching] = useState<boolean>(false);

  const handleDispatch = async () => {
    if (!selectedIncident || !selectedUnit) return;
    setIsDispatching(true);
    try {
      await taskService.createTask({
        incidentId: selectedIncident.id,
        incidentCode: selectedIncident.incidentCode,
        title: `Deploy ${selectedUnit.organization} power boats for emergency evacuation at ${selectedIncident.villageName}`,
        priority: selectedIncident.verifiedPriority || selectedIncident.reportedSeverity,
        assignedUnitId: selectedUnit.id,
        targetVillage: selectedIncident.villageName || 'Unspecified Village',
        targetLatitude: selectedIncident.latitude,
        targetLongitude: selectedIncident.longitude,
        slaHours,
      });
      showToast(
        'success',
        'Tactical Force Dispatched',
        `Assigned ${selectedUnit.name} to ${selectedIncident.incidentCode} with SLA of ${slaHours} hours`
      );
    } catch {
      showToast('error', 'Dispatch Failed', 'Could not assign tactical unit.');
    } finally {
      setIsDispatching(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* 1. Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-line">
        <div>
          <div className="flex items-center gap-2">
            <Radio className="w-5 h-5 text-forest" />
            <h1 className="text-xl font-bold text-ink-primary tracking-tight">
              Tactical Response Coordination & Force Dispatch
            </h1>
          </div>
          <p className="text-xs text-sage mt-0.5">
            Role: Response Coordinator (BDO / Fire Operations Head). Match verified life-threatening distress calls with nearest available ODRAF and Fire Services battalions.
          </p>
        </div>

        <div className="flex items-center gap-2 text-xs font-mono">
          <span className="bg-forest-subtle text-forest border border-forest/30 px-2.5 py-1 rounded font-bold">
            Available Battalions: {DEMO_TACTICAL_UNITS.filter((u) => u.status !== 'DEPLOYED').length}
          </span>
        </div>
      </div>

      {/* 2. Main Split Coordination Console */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Left Column: Verified Incidents Waiting for Dispatch (5 Cols) */}
        <div className="lg:col-span-5 space-y-2">
          <div className="text-xs font-semibold text-sage uppercase tracking-wider px-1">
            Verified Cases Needing Units ({eligibleIncidents.length})
          </div>

          <div className="space-y-2 max-h-[640px] overflow-y-auto pr-1">
            {eligibleIncidents.map((inc) => (
              <div
                key={inc.id}
                onClick={() => setSelectedIncident(inc)}
                className={`p-3.5 rounded border transition-all cursor-pointer text-left ${
                  selectedIncident?.id === inc.id
                    ? 'bg-white border-forest ring-2 ring-forest/20 shadow-xs'
                    : 'bg-white border-line hover:border-line-dark'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-bold text-ink-primary">
                    {inc.incidentCode}
                  </span>
                  <GovBadge
                    variant={inc.reportedSeverity === 'CRITICAL' ? 'emergency' : 'amber'}
                    size="sm"
                  >
                    {inc.reportedSeverity}
                  </GovBadge>
                </div>

                <div className="text-xs font-semibold text-ink-primary mt-1">
                  {inc.villageName}, {inc.blockName} Block
                </div>

                <p className="text-xs text-ink-secondary line-clamp-2 mt-1">
                  {inc.rawDescription}
                </p>

                <div className="mt-2 pt-2 border-t border-line flex items-center justify-between text-[11px] font-mono text-sage">
                  <span>
                    Stranded: <strong className="text-emergency">{inc.personsStranded} People</strong>
                  </span>
                  <span className="text-forest font-semibold">{inc.hazardType}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Column: Tactical Unit Selector & Dispatch Action (7 Cols) */}
        {selectedIncident && (
          <div className="lg:col-span-7 space-y-4">
            <GovCard
              header={
                <div className="flex items-center justify-between w-full">
                  <span className="font-semibold text-xs uppercase tracking-wider text-sage">
                    Target Mission: {selectedIncident.incidentCode} — {selectedIncident.villageName}
                  </span>
                  <GovBadge variant="emergency" size="sm">
                    {selectedIncident.reportedSeverity} PRIORITY
                  </GovBadge>
                </div>
              }
            >
              <div className="space-y-3">
                <div className="p-3 bg-bg-warm rounded border border-line text-xs font-mono flex items-center justify-between">
                  <div>
                    <span className="text-sage block text-[10px]">Destination Coordinates</span>
                    <strong className="text-ink-primary">
                      {formatCoordinates(selectedIncident.latitude, selectedIncident.longitude)}
                    </strong>
                  </div>
                  <div>
                    <span className="text-sage block text-[10px]">Hazard Nature</span>
                    <strong className="text-forest">{selectedIncident.hazardType}</strong>
                  </div>
                  <div>
                    <span className="text-sage block text-[10px]">Stranded Headcount</span>
                    <strong className="text-emergency">{selectedIncident.personsStranded} Persons</strong>
                  </div>
                </div>

                {/* Available Tactical Forces List */}
                <div className="space-y-2 pt-2">
                  <label className="text-xs font-semibold text-ink-primary block">
                    Select Tactical Force for Dispatch:
                  </label>

                  <div className="space-y-2">
                    {DEMO_TACTICAL_UNITS.map((unit) => (
                      <div
                        key={unit.id}
                        onClick={() => setSelectedUnit(unit)}
                        className={`p-3 rounded border text-xs transition-colors cursor-pointer flex items-center justify-between ${
                          selectedUnit?.id === unit.id
                            ? 'bg-forest-subtle/50 border-forest font-medium'
                            : 'bg-white border-line hover:bg-bg-warm'
                        }`}
                      >
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <span className="font-mono font-bold text-ink-primary">{unit.unitCode}</span>
                            <span className="font-bold text-forest">{unit.name}</span>
                            <GovBadge
                              variant={unit.status === 'MOBILIZED' ? 'amber' : 'forest'}
                              size="sm"
                            >
                              {unit.status}
                            </GovBadge>
                          </div>
                          <div className="text-sage text-[11px]">
                            Staged at: {unit.homeStation} • Commander: {unit.commanderName}
                          </div>
                          <div className="font-mono text-[11px] text-ink-secondary">
                            Assets: {unit.equipmentSummary.boats} Rescue Boats, {unit.equipmentSummary.pumps} Pumps, {unit.crewCount} Personnel
                          </div>
                        </div>

                        <div className="text-right font-mono">
                          <span className="text-sage block text-[10px]">ETA to Site</span>
                          <strong className="text-ink-primary text-xs">~25 Mins</strong>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Dispatch Parameters */}
                <div className="grid grid-cols-2 gap-3 pt-2 border-t border-line">
                  <div>
                    <label className="text-xs font-semibold text-ink-primary block mb-1">
                      Mission SLA Deadline
                    </label>
                    <select
                      value={slaHours}
                      onChange={(e) => setSlaHours(Number(e.target.value))}
                      className="w-full text-xs h-9 px-3 bg-white border border-line rounded text-ink-primary font-mono"
                    >
                      <option value={1}>1 Hour (Urgent Life Threat)</option>
                      <option value={2}>2 Hours (Standard Severe)</option>
                      <option value={4}>4 Hours (Infrastructure Clearance)</option>
                    </select>
                  </div>

                  <div>
                    <label className="text-xs font-semibold text-ink-primary block mb-1">
                      Route Clearance Note
                    </label>
                    <span className="text-xs text-forest font-semibold block pt-2">
                      ✓ Flood-Safe Route Verified via SH-12
                    </span>
                  </div>
                </div>

                {/* Confirm Dispatch Action */}
                <div className="pt-4 border-t border-line">
                  <GovButton
                    variant="primary"
                    size="md"
                    className="w-full h-10 font-bold"
                    onClick={handleDispatch}
                    isLoading={isDispatching}
                    leftIcon={<Navigation className="w-4 h-4 mr-1" />}
                  >
                    Confirm Tactical Dispatch of {selectedUnit?.name}
                  </GovButton>
                </div>
              </div>
            </GovCard>
          </div>
        )}
      </div>
    </div>
  );
};
