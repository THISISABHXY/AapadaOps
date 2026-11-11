import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  AlertTriangle,
  Users,
  Building2,
  Ship,
  CheckCircle2,
  Clock,
  ArrowRight,
  ExternalLink,
  Filter,
} from 'lucide-react';
import { GovCard } from '../components/ui/GovCard';
import { GovBadge } from '../components/ui/GovBadge';
import { GovButton } from '../components/ui/GovButton';
import {
  DEMO_INCIDENTS,
  DEMO_SHELTERS,
  DEMO_EOC_KPI,
  ODISHA_DISTRICTS,
} from '../services/demoDataService';
import { formatTimeAgo } from '../utilities/formatters';

export const DashboardPage: React.FC = () => {
  const [selectedDistrict, setSelectedDistrict] = useState<string>('Puri');
  const [feedTab, setFeedTab] = useState<'UNVERIFIED' | 'DISPATCHED' | 'SHELTERS'>('UNVERIFIED');

  const unverifiedList = DEMO_INCIDENTS.filter((i) => i.status === 'NEEDS_VERIFICATION');
  const activeDispatchedList = DEMO_INCIDENTS.filter(
    (i) => i.status === 'ASSIGNED' || i.status === 'IN_PROGRESS' || i.status === 'VERIFIED'
  );

  return (
    <div className="space-y-4">
      {/* 1. Dashboard Filter & Sub-header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-line">
        <div>
          <h1 className="text-xl font-bold text-ink-primary tracking-tight">
            Emergency Operations Command (EOC) Cockpit
          </h1>
          <p className="text-xs text-sage">
            Real-time multi-hazard telemetry, unverified incident intake queue, and tactical force deployments.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-sage" />
          <span className="text-xs font-semibold text-ink-primary">Jurisdiction:</span>
          <select
            value={selectedDistrict}
            onChange={(e) => setSelectedDistrict(e.target.value)}
            className="text-xs bg-white border border-line rounded px-2.5 py-1.5 font-medium text-ink-primary focus:outline-none focus:ring-1 focus:ring-forest"
          >
            <option value="ALL">All Odisha (30 Districts)</option>
            {ODISHA_DISTRICTS.map((d) => (
              <option key={d} value={d}>
                {d} District
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* 2. Four High-Density KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <GovCard padding="sm" className="border-l-4 border-l-emergency">
          <div className="flex items-center justify-between">
            <span className="text-xs text-sage font-medium">Unverified Reports</span>
            <AlertTriangle className="w-4 h-4 text-emergency" />
          </div>
          <div className="mt-1 flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-ink-primary">
              {DEMO_EOC_KPI.unverifiedIncidentsCount}
            </span>
            <span className="text-[11px] text-emergency font-semibold">Requires Review</span>
          </div>
          <Link
            to="/verification"
            className="text-[11px] text-forest font-semibold hover:underline flex items-center gap-1 mt-2 pt-2 border-t border-line"
          >
            <span>Open Verification Queue</span>
            <ArrowRight className="w-3 h-3" />
          </Link>
        </GovCard>

        <GovCard padding="sm" className="border-l-4 border-l-amber">
          <div className="flex items-center justify-between">
            <span className="text-xs text-sage font-medium">Active Tasks Dispatched</span>
            <Clock className="w-4 h-4 text-amber-dark" />
          </div>
          <div className="mt-1 flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-ink-primary">
              {DEMO_EOC_KPI.verifiedActiveTasksCount}
            </span>
            <span className="text-[11px] text-amber-dark font-medium">In Field Ops</span>
          </div>
          <Link
            to="/tasks"
            className="text-[11px] text-forest font-semibold hover:underline flex items-center gap-1 mt-2 pt-2 border-t border-line"
          >
            <span>Track Team Task Board</span>
            <ArrowRight className="w-3 h-3" />
          </Link>
        </GovCard>

        <GovCard padding="sm" className="border-l-4 border-l-forest">
          <div className="flex items-center justify-between">
            <span className="text-xs text-sage font-medium">Evacuees in Shelters</span>
            <Users className="w-4 h-4 text-forest" />
          </div>
          <div className="mt-1 flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-ink-primary">
              {DEMO_EOC_KPI.totalEvacuatedCitizens.toLocaleString('en-IN')}
            </span>
            <span className="text-[11px] text-sage font-mono">
              ({Math.round(DEMO_EOC_KPI.averageShelterOccupancyRate * 100)}% Cap)
            </span>
          </div>
          <Link
            to="/shelters"
            className="text-[11px] text-forest font-semibold hover:underline flex items-center gap-1 mt-2 pt-2 border-t border-line"
          >
            <span>Inspect 800+ Shelters</span>
            <ArrowRight className="w-3 h-3" />
          </Link>
        </GovCard>

        <GovCard padding="sm" className="border-l-4 border-l-sage">
          <div className="flex items-center justify-between">
            <span className="text-xs text-sage font-medium">Tactical Force Units</span>
            <Ship className="w-4 h-4 text-sage" />
          </div>
          <div className="mt-1 flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-ink-primary">
              {DEMO_EOC_KPI.deployedTacticalUnitsCount} / {DEMO_EOC_KPI.deployedTacticalUnitsCount + DEMO_EOC_KPI.availableTacticalUnitsCount}
            </span>
            <span className="text-[11px] text-forest font-medium">ODRAF / NDRF</span>
          </div>
          <Link
            to="/coordination"
            className="text-[11px] text-forest font-semibold hover:underline flex items-center gap-1 mt-2 pt-2 border-t border-line"
          >
            <span>Mobilize Tactical Reserve</span>
            <ArrowRight className="w-3 h-3" />
          </Link>
        </GovCard>
      </div>

      {/* 3. Main Split View: Map Overview + Operational Activity Streams */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Left Side: Situation Map Preview (7 Cols) */}
        <div className="lg:col-span-7 space-y-3">
          <GovCard
            header={
              <div className="flex items-center justify-between w-full">
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-sm text-ink-primary">Geospatial Situation Overview</span>
                  <GovBadge variant="forest" size="sm">LIVE GIS</GovBadge>
                </div>
                <Link
                  to="/map"
                  className="text-xs font-semibold text-forest hover:underline flex items-center gap-1"
                >
                  <span>Full Screen Map</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </Link>
              </div>
            }
            padding="none"
          >
            {/* Embedded Visual Situation Preview */}
            <div className="h-[360px] bg-bg-warm relative overflow-hidden flex flex-col items-center justify-center border-b border-line p-4">
              {/* Simulated Map Visual Representation */}
              <div className="absolute inset-0 opacity-15 pointer-events-none bg-[radial-gradient(#365B4A_1px,transparent_1px)] [background-size:16px_16px]" />

              <div className="z-10 bg-white/95 border border-line rounded p-4 max-w-sm text-center shadow-xs">
                <div className="w-10 h-10 rounded-full bg-forest-subtle mx-auto flex items-center justify-center text-forest mb-2">
                  <Building2 className="w-5 h-5" />
                </div>
                <h4 className="text-sm font-semibold text-ink-primary mb-1">
                  Active Coastal Threat Zone: Puri & Jagatsinghpur
                </h4>
                <p className="text-xs text-sage mb-3 leading-relaxed">
                  Interactive PostGIS layers ready: Cyclone track buffer, flood plain inundation, and 8 active cluster pins in {selectedDistrict}.
                </p>
                <Link to="/map">
                  <GovButton variant="primary" size="sm" className="w-full">
                    Launch Interactive GIS Map Console
                  </GovButton>
                </Link>
              </div>

              {/* Mini Map Status Chips */}
              <div className="absolute bottom-2 left-2 z-10 flex gap-1.5 font-mono text-[10px]">
                <span className="bg-white/90 px-2 py-0.5 rounded border border-line text-ink-primary">
                  Center: 19.8135° N, 85.8312° E
                </span>
                <span className="bg-white/90 px-2 py-0.5 rounded border border-line text-forest font-semibold">
                  SRID: 4326 (WGS 84)
                </span>
              </div>
            </div>

            {/* Quick Status Bar under Map */}
            <div className="p-3 bg-white grid grid-cols-3 text-center text-xs divide-x divide-line font-mono">
              <div>
                <span className="text-sage block text-[11px]">Reported Embankments</span>
                <strong className="text-ink-primary">2 Breaches Active</strong>
              </div>
              <div>
                <span className="text-sage block text-[11px]">Road Blockages</span>
                <strong className="text-ink-primary">NH-316 & SH-12</strong>
              </div>
              <div>
                <span className="text-sage block text-[11px]">Free Kitchens Open</span>
                <strong className="text-forest">64 Active</strong>
              </div>
            </div>
          </GovCard>
        </div>

        {/* Right Side: Tabbed Operational Incident & Shelter Feeds (5 Cols) */}
        <div className="lg:col-span-5 space-y-3">
          <GovCard
            header={
              <div className="flex items-center justify-between w-full">
                <div className="flex gap-1">
                  <button
                    onClick={() => setFeedTab('UNVERIFIED')}
                    className={`px-2.5 py-1 text-xs font-semibold rounded cursor-pointer ${
                      feedTab === 'UNVERIFIED'
                        ? 'bg-forest text-white'
                        : 'text-sage hover:text-ink-primary'
                    }`}
                  >
                    Unverified ({unverifiedList.length})
                  </button>

                  <button
                    onClick={() => setFeedTab('DISPATCHED')}
                    className={`px-2.5 py-1 text-xs font-semibold rounded cursor-pointer ${
                      feedTab === 'DISPATCHED'
                        ? 'bg-forest text-white'
                        : 'text-sage hover:text-ink-primary'
                    }`}
                  >
                    Active Tasks ({activeDispatchedList.length})
                  </button>

                  <button
                    onClick={() => setFeedTab('SHELTERS')}
                    className={`px-2.5 py-1 text-xs font-semibold rounded cursor-pointer ${
                      feedTab === 'SHELTERS'
                        ? 'bg-forest text-white'
                        : 'text-sage hover:text-ink-primary'
                    }`}
                  >
                    Shelters
                  </button>
                </div>

                <Link
                  to={feedTab === 'UNVERIFIED' ? '/verification' : feedTab === 'DISPATCHED' ? '/tasks' : '/shelters'}
                  className="text-xs text-forest hover:underline font-semibold"
                >
                  View All
                </Link>
              </div>
            }
            padding="none"
          >
            <div className="max-h-[420px] overflow-y-auto divide-y divide-line">
              {feedTab === 'UNVERIFIED' &&
                unverifiedList.map((inc) => (
                  <div key={inc.id} className="p-3 hover:bg-bg-warm transition-colors space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-xs font-semibold text-ink-primary">
                        {inc.incidentCode}
                      </span>
                      <div className="flex items-center gap-1.5">
                        <GovBadge variant="emergency" size="sm">
                          {inc.reportedSeverity}
                        </GovBadge>
                        <span className="font-mono text-[11px] text-sage">
                          {formatTimeAgo(inc.createdAt)}
                        </span>
                      </div>
                    </div>

                    <div className="text-xs font-semibold text-ink-primary">
                      {inc.villageName}, {inc.blockName}
                    </div>

                    <p className="text-xs text-ink-secondary line-clamp-2 leading-relaxed">
                      {inc.rawDescription}
                    </p>

                    <div className="pt-1 flex items-center justify-between text-xs">
                      <span className="text-[11px] font-mono text-sage">
                        Stranded: <strong className="text-ink-primary">{inc.personsStranded}</strong>
                      </span>
                      <Link
                        to={`/incidents/${inc.id}`}
                        className="text-forest font-semibold hover:underline inline-flex items-center gap-0.5 text-xs"
                      >
                        Audit Report <ArrowRight className="w-3 h-3" />
                      </Link>
                    </div>
                  </div>
                ))}

              {feedTab === 'DISPATCHED' &&
                activeDispatchedList.map((inc) => (
                  <div key={inc.id} className="p-3 hover:bg-bg-warm transition-colors space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-xs font-semibold text-ink-primary">
                        {inc.incidentCode}
                      </span>
                      <GovBadge
                        variant={inc.status === 'IN_PROGRESS' ? 'amber' : 'forest'}
                        size="sm"
                      >
                        {inc.status}
                      </GovBadge>
                    </div>
                    <div className="text-xs font-semibold text-ink-primary">{inc.villageName}</div>
                    <p className="text-xs text-sage line-clamp-1">{inc.rawDescription}</p>
                    <div className="pt-1 flex items-center justify-between text-xs">
                      <span className="text-sage text-[11px]">
                        Verified by: {inc.verifiedByName || 'Tahasildar'}
                      </span>
                      <Link to={`/incidents/${inc.id}`} className="text-forest font-semibold text-xs">
                        Details →
                      </Link>
                    </div>
                  </div>
                ))}

              {feedTab === 'SHELTERS' &&
                DEMO_SHELTERS.map((s) => (
                  <div key={s.id} className="p-3 hover:bg-bg-warm transition-colors space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-xs text-ink-primary">{s.name}</span>
                      <GovBadge
                        variant={s.occupancyRate >= 0.9 ? 'emergency' : 'forest'}
                        size="sm"
                      >
                        {Math.round(s.occupancyRate * 100)}% Occupied
                      </GovBadge>
                    </div>
                    <div className="text-xs text-sage flex justify-between font-mono">
                      <span>{s.blockName} Block</span>
                      <span>{s.currentOccupancy} / {s.totalCapacity} evacuees</span>
                    </div>
                  </div>
                ))}
            </div>
          </GovCard>
        </div>
      </div>
    </div>
  );
};

