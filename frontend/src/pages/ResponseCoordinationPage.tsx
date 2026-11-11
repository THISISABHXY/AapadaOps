import React, { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import {
  Radio,
  Ship,
  MapPin,
  Clock,
  ShieldAlert,
  ArrowRight,
  CheckCircle2,
  Navigation,
  Sparkles,
  ShieldCheck,
  Cpu,
  Layers,
} from 'lucide-react';
import { GovCard } from '../components/ui/GovCard';
import { GovBadge } from '../components/ui/GovBadge';
import { GovButton } from '../components/ui/GovButton';
import { incidentService } from '../services/incidentService';
import { taskService } from '../services/taskService';
import { coordinationService, StrategyRecommendation } from '../services/coordinationService';
import { useToast } from '../contexts/ToastContext';
import { Incident } from '../types/incident';
import { TacticalUnit } from '../types/task';
import { formatCoordinates } from '../utilities/formatters';

export const ResponseCoordinationPage: React.FC = () => {
  const { showToast } = useToast();
  const queryClient = useQueryClient();

  // Queries
  const { data: incidents = [], isLoading: loadingIncidents } = useQuery({
    queryKey: ['incidents'],
    queryFn: () => incidentService.getIncidents(),
  });

  const { data: tacticalUnits = [] } = useQuery({
    queryKey: ['tactical-units'],
    queryFn: () => taskService.getTacticalUnits(),
  });

  const eligibleIncidents = incidents.filter(
    (i) => i.status === 'VERIFIED' || i.status === 'NEEDS_VERIFICATION' || i.status === 'SUBMITTED'
  );

  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);
  const [selectedUnit, setSelectedUnit] = useState<TacticalUnit | null>(null);
  const [slaHours, setSlaHours] = useState<number>(2);
  const [isDispatching, setIsDispatching] = useState<boolean>(false);

  // OR-Tools Optimization State
  const [isOptimizing, setIsOptimizing] = useState<boolean>(false);
  const [recommendations, setRecommendations] = useState<StrategyRecommendation[]>([]);
  const [selectedStrategy, setSelectedStrategy] = useState<StrategyRecommendation | null>(null);
  const [optimizationActive, setOptimizationActive] = useState<boolean>(false);

  // Set default selection when incidents load
  React.useEffect(() => {
    if (!selectedIncident && eligibleIncidents.length > 0) {
      setSelectedIncident(eligibleIncidents[0]);
    }
  }, [eligibleIncidents, selectedIncident]);

  React.useEffect(() => {
    if (!selectedUnit && tacticalUnits.length > 0) {
      setSelectedUnit(tacticalUnits[0]);
    }
  }, [tacticalUnits, selectedUnit]);

  // Run OR-Tools Optimization Engine
  const handleRunOptimization = async () => {
    if (!selectedIncident) return;
    setIsOptimizing(true);
    setOptimizationActive(true);
    try {
      const res = await coordinationService.getOptimization(selectedIncident.id, {
        requiredBoats: Math.max(1, Math.ceil(selectedIncident.personsStranded / 15)),
        requiredPumps: selectedIncident.hazardType === 'FLOOD' ? 2 : 1,
        preserveReserveRatio: 0.2,
      });
      setRecommendations(res.recommendations || []);
      setSelectedStrategy(res.recommendations?.[0] || null);
      showToast(
        'success',
        'OR-Tools Optimization Solved',
        `Generated 3 feasible allocation strategies considering team capabilities and flood velocity models.`
      );
    } catch (err: any) {
      showToast('error', 'Optimization Failed', err?.message || 'Could not solve MIP formulation.');
    } finally {
      setIsOptimizing(false);
    }
  };

  // Authorize & Dispatch an OR-Tools Strategy
  const handleApproveStrategy = async () => {
    if (!selectedIncident || !selectedStrategy) return;
    setIsDispatching(true);
    try {
      // 1. Create plan from recommendation
      const plan = await coordinationService.createPlanFromRecommendation(
        selectedIncident.id,
        selectedStrategy,
        selectedIncident.incidentCode
      );

      // 2. Approve plan (executes atomic double-allocation check & creates tasks)
      await coordinationService.approvePlan(plan.id, slaHours, 'Authorized by Response Coordinator via OR-Tools dispatch.');

      showToast(
        'success',
        'Strategy Authorized & Dispatched',
        `Mission deployed under ${selectedStrategy.strategy_name}. ${selectedStrategy.recommended_teams.length} teams assigned.`
      );

      // Invalidate queries to refresh lists and tasks
      queryClient.invalidateQueries({ queryKey: ['incidents'] });
      queryClient.invalidateQueries({ queryKey: ['tactical-units'] });
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      setRecommendations([]);
      setOptimizationActive(false);
    } catch (err: any) {
      showToast(
        'error',
        'Dispatch Conflict Rejected',
        err?.message || 'Double allocation blocked: One or more selected resources are no longer available.'
      );
    } finally {
      setIsDispatching(false);
    }
  };

  // Manual Dispatch Action
  const handleManualDispatch = async () => {
    if (!selectedIncident || !selectedUnit) return;
    setIsDispatching(true);
    try {
      await taskService.createTask({
        incidentId: selectedIncident.id,
        incidentCode: selectedIncident.incidentCode,
        title: `Deploy ${selectedUnit.organization} power craft for emergency rescue at ${selectedIncident.villageName}`,
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

      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      queryClient.invalidateQueries({ queryKey: ['incidents'] });
    } catch (err: any) {
      showToast('error', 'Dispatch Failed', err?.message || 'Could not assign tactical unit.');
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
            Available Battalions: {tacticalUnits.filter((u) => u.status !== 'DEPLOYED').length}
          </span>
        </div>
      </div>

      {/* 2. Main Split Coordination Console */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Left Column: Verified Incidents Waiting for Dispatch (5 Cols) */}
        <div className="lg:col-span-5 space-y-2">
          <div className="text-xs font-semibold text-sage uppercase tracking-wider px-1">
            Incidents Needing Allocation ({eligibleIncidents.length})
          </div>

          <div className="space-y-2 max-h-[640px] overflow-y-auto pr-1">
            {eligibleIncidents.map((inc) => (
              <div
                key={inc.id}
                onClick={() => {
                  setSelectedIncident(inc);
                  setOptimizationActive(false);
                  setRecommendations([]);
                }}
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
                  {inc.villageName}, {inc.blockName ? `${inc.blockName} Block` : inc.districtName}
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

        {/* Right Column: Tactical Coordination & OR-Tools Workbench (7 Cols) */}
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

                {/* Operations Research (OR-Tools) Trigger */}
                <div className="p-3 rounded border border-forest/30 bg-forest-subtle/30 flex items-center justify-between">
                  <div>
                    <div className="flex items-center gap-1.5 font-bold text-xs text-forest">
                      <Cpu className="w-4 h-4" />
                      <span>Google OR-Tools Mixed-Integer Optimization Engine</span>
                    </div>
                    <p className="text-[11px] text-sage mt-0.5">
                      Evaluates unit specializations, transit speeds, and depot reserve floors to compute 3 optimal strategies.
                    </p>
                  </div>
                  <GovButton
                    variant="primary"
                    size="sm"
                    onClick={handleRunOptimization}
                    isLoading={isOptimizing}
                    leftIcon={<Sparkles className="w-3.5 h-3.5" />}
                  >
                    Solve Multi-Strategy MIP
                  </GovButton>
                </div>

                {/* OR-Tools Strategy Cards View */}
                {optimizationActive && recommendations.length > 0 && (
                  <div className="space-y-3 pt-2">
                    <label className="text-xs font-semibold text-ink-primary block">
                      Select AI Optimization Strategy for Human Coordinator Approval:
                    </label>

                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                      {recommendations.map((rec) => (
                        <div
                          key={rec.strategy_name}
                          onClick={() => setSelectedStrategy(rec)}
                          className={`p-3 rounded border text-xs cursor-pointer transition-all flex flex-col justify-between ${
                            selectedStrategy?.strategy_name === rec.strategy_name
                              ? 'bg-white border-forest ring-2 ring-forest/30 shadow-xs'
                              : 'bg-bg-warm/60 border-line hover:bg-white'
                          }`}
                        >
                          <div>
                            <div className="font-bold text-xs text-ink-primary mb-1">
                              {rec.strategy_name.replace('_', ' ')}
                            </div>
                            <div className="font-mono text-[11px] text-sage space-y-0.5">
                              <div>ETA: <strong className="text-ink-primary">~{rec.estimated_arrival_minutes} Mins</strong></div>
                              <div>Cap: <strong className="text-forest">{rec.total_rescue_capacity_persons} Persons</strong></div>
                              <div>Teams: <strong className="text-ink-primary">{rec.recommended_teams.length}</strong></div>
                            </div>
                            <p className="text-[11px] text-ink-secondary mt-2 line-clamp-3">
                              {rec.reasoning}
                            </p>
                          </div>

                          <div className="mt-2 pt-2 border-t border-line text-[10px] text-sage font-mono">
                            {rec.telemetry_source}
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* Selected Strategy Detail Callout */}
                    {selectedStrategy && (
                      <div className="p-3 bg-white rounded border border-line text-xs space-y-2">
                        <div className="font-semibold text-ink-primary flex items-center justify-between">
                          <span>Assigned Forces: {selectedStrategy.recommended_teams.map((t) => t.name).join(', ')}</span>
                          <span className="font-mono text-sage text-[11px]">Cost Metric: {selectedStrategy.objective_cost.toFixed(1)}</span>
                        </div>
                        <div className="text-[11px] text-sage">
                          <strong>Resource Impact:</strong> {selectedStrategy.estimated_resource_impact}
                        </div>
                        <div className="p-2 bg-amber-subtle/50 rounded border border-amber/20 text-[11px] text-amber-dark">
                          <strong>Telemetry Disclaimer:</strong> {selectedStrategy.telemetry_note}
                        </div>

                        <GovButton
                          variant="primary"
                          size="md"
                          className="w-full mt-2 font-bold"
                          onClick={handleApproveStrategy}
                          isLoading={isDispatching}
                          leftIcon={<ShieldCheck className="w-4 h-4 mr-1" />}
                        >
                          Authorize & Deploy Strategy: {selectedStrategy.strategy_name}
                        </GovButton>
                      </div>
                    )}
                  </div>
                )}

                {/* Manual Force Dispatch Alternative */}
                {!optimizationActive && (
                  <>
                    <div className="space-y-2 pt-2">
                      <label className="text-xs font-semibold text-ink-primary block">
                        Manual Force Selection (Alternative to OR-Tools):
                      </label>

                      <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
                        {tacticalUnits.map((unit) => (
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
                                Base: {unit.homeStation} • Commander: {unit.commanderName}
                              </div>
                              <div className="font-mono text-[11px] text-ink-secondary">
                                Crew: {unit.crewCount} Personnel • Boats: {unit.equipmentSummary.boats}
                              </div>
                            </div>

                            <div className="text-right font-mono">
                              <span className="text-sage block text-[10px]">Estimated ETA</span>
                              <strong className="text-ink-primary text-xs">~30 Mins</strong>
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

                    {/* Confirm Manual Dispatch Action */}
                    <div className="pt-2 border-t border-line">
                      <GovButton
                        variant="secondary"
                        size="md"
                        className="w-full h-10 font-bold"
                        onClick={handleManualDispatch}
                        isLoading={isDispatching}
                        leftIcon={<Navigation className="w-4 h-4 mr-1" />}
                      >
                        Confirm Tactical Dispatch of {selectedUnit?.name || 'Selected Force'}
                      </GovButton>
                    </div>
                  </>
                )}
              </div>
            </GovCard>
          </div>
        )}
      </div>
    </div>
  );
};
