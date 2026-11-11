import React from 'react';
import {
  BarChart3,
  Download,
  Calendar,
  FileText,
  Printer,
  TrendingUp,
  ShieldCheck,
} from 'lucide-react';
import { GovCard } from '../components/ui/GovCard';
import { GovBadge } from '../components/ui/GovBadge';
import { GovButton } from '../components/ui/GovButton';
import {
  DEMO_EOC_KPI,
  DEMO_HOURLY_TRENDS,
  DEMO_HAZARD_BREAKDOWN,
  DEMO_DISTRICT_READINESS,
} from '../services/demoDataService';

export const AnalyticsPage: React.FC = () => {
  const handlePrintSitRep = () => {
    window.print();
  };

  return (
    <div className="space-y-4">
      {/* 1. Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-line">
        <div>
          <div className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-forest" />
            <h1 className="text-xl font-bold text-ink-primary tracking-tight">
              Disaster Analytics & Situation Report (SitRep) Generator
            </h1>
          </div>
          <p className="text-xs text-sage mt-0.5">
            Official Situation Summary prepared for the Chief Minister's Office, Special Relief Commissioner, and National Disaster Management Authority (NDMA).
          </p>
        </div>

        <div className="flex items-center gap-2">
          <GovButton
            variant="secondary"
            size="sm"
            onClick={handlePrintSitRep}
            leftIcon={<Printer className="w-3.5 h-3.5" />}
          >
            Print / Export Official SitRep
          </GovButton>
        </div>
      </div>

      {/* 2. Top Metric Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <GovCard padding="sm">
          <span className="text-xs text-sage block">Total SOS Calls Received</span>
          <strong className="text-2xl font-mono text-ink-primary block mt-1">
            {DEMO_EOC_KPI.totalIngestedIncidents}
          </strong>
          <span className="text-[11px] text-forest font-medium">98.2% Geocoded</span>
        </GovCard>

        <GovCard padding="sm">
          <span className="text-xs text-sage block">Verified Active Missions</span>
          <strong className="text-2xl font-mono text-ink-primary block mt-1">
            {DEMO_EOC_KPI.verifiedActiveTasksCount}
          </strong>
          <span className="text-[11px] text-amber-dark font-medium">Under ODRAF/OFES Execution</span>
        </GovCard>

        <GovCard padding="sm">
          <span className="text-xs text-sage block">Total Safely Evacuated</span>
          <strong className="text-2xl font-mono text-ink-primary block mt-1">
            {DEMO_EOC_KPI.totalEvacuatedCitizens.toLocaleString('en-IN')}
          </strong>
          <span className="text-[11px] text-forest font-medium">Across 184 Activated Shelters</span>
        </GovCard>

        <GovCard padding="sm">
          <span className="text-xs text-sage block">Average Response Time</span>
          <strong className="text-2xl font-mono text-ink-primary block mt-1">
            {DEMO_EOC_KPI.averageResponseMinutes} Mins
          </strong>
          <span className="text-[11px] text-sage font-medium">From Triage to On-Scene</span>
        </GovCard>
      </div>

      {/* 3. Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Hourly Trend Simple Accessible Bar Chart (7 Cols) */}
        <div className="lg:col-span-7 space-y-3">
          <GovCard
            header={
              <div className="flex items-center justify-between w-full">
                <span className="font-semibold text-xs uppercase tracking-wider text-sage">
                  Hourly Incident Intake vs. Resolution Rate
                </span>
                <span className="text-xs font-mono text-sage">Last 7 Hours (Puri District)</span>
              </div>
            }
          >
            <div className="space-y-3">
              {DEMO_HOURLY_TRENDS.map((t) => (
                <div key={t.hour} className="space-y-1">
                  <div className="flex justify-between text-xs font-mono">
                    <span className="text-ink-primary font-bold">{t.hour} IST</span>
                    <span className="text-sage">
                      Ingested: <strong className="text-ink-primary">{t.incomingReports}</strong> | Resolved: <strong className="text-forest">{t.resolvedTasks}</strong>
                    </span>
                  </div>
                  <div className="w-full bg-bg-subtle h-3 rounded flex overflow-hidden">
                    <div
                      className="bg-emergency/80 h-full"
                      style={{ width: `${Math.min(100, (t.incomingReports / 100) * 100)}%` }}
                    />
                    <div
                      className="bg-forest h-full"
                      style={{ width: `${Math.min(100, (t.resolvedTasks / 100) * 100)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-4 pt-3 border-t border-line flex items-center justify-center gap-6 text-xs font-mono text-sage">
              <span className="flex items-center gap-1.5">
                <span className="w-3 h-3 bg-emergency/80 rounded" /> Ingested Calls
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-3 h-3 bg-forest rounded" /> Field Rescues Resolved
              </span>
            </div>
          </GovCard>
        </div>

        {/* Hazard Category Breakdown (5 Cols) */}
        <div className="lg:col-span-5 space-y-3">
          <GovCard
            header={
              <span className="font-semibold text-xs uppercase tracking-wider text-sage">
                Hazard Nature Breakdown
              </span>
            }
          >
            <div className="space-y-3">
              {DEMO_HAZARD_BREAKDOWN.map((h) => (
                <div key={h.hazardType} className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span className="font-medium text-ink-primary">{h.hazardType}</span>
                    <span className="font-mono text-sage">{h.count} calls ({h.percentage}%)</span>
                  </div>
                  <div className="w-full bg-bg-subtle h-2 rounded overflow-hidden">
                    <div
                      className="bg-forest h-full"
                      style={{ width: `${h.percentage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </GovCard>
        </div>
      </div>

      {/* 4. Official Situation Report (SitRep) Document Preview Card */}
      <GovCard
        header={
          <div className="flex items-center justify-between w-full">
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4 text-forest" />
              <span className="font-bold text-sm text-ink-primary">
                Official Situation Report #04 — Odisha Cyclonic Storm Protocol
              </span>
            </div>
            <GovBadge variant="forest" size="sm">CERTIFIED OFFICIAL</GovBadge>
          </div>
        }
      >
        <div className="bg-bg-warm p-4 rounded border border-line space-y-3 text-xs leading-relaxed">
          <div className="border-b border-line pb-2 flex justify-between font-mono text-sage text-[11px]">
            <span>Report Authority: Special Relief Commissioner (SRC), Government of Odisha</span>
            <span>Issued: 12-Nov-2026 00:30 IST</span>
          </div>

          <p>
            <strong>1. General Situation:</strong> A Very Severe Cyclonic Storm is centered over the Westcentral Bay of Bengal, moving North-Northwestward at 18 km/h. Coastal districts of Puri, Jagatsinghpur, and Kendrapara have been placed under RED alert. 24 ODRAF and 16 NDRF battalions have been positioned in coastal staging areas.
          </p>

          <p>
            <strong>2. Evacuation Status:</strong> As of 00:30 IST, a total of <strong>38,450 citizens</strong> have been safely relocated to 184 engineered Multi-Purpose Cyclone Shelters (MCS). All shelters are operating free community kitchens with 4 days of dry rations and potable water supply.
          </p>

          <p>
            <strong>3. Key Ground Operations:</strong> 142 localized incidents have been successfully resolved by Fire Services and ODRAF teams. Critical road clearance on NH-316 (Puri-Bhubaneswar highway) is currently underway. No loss of human life has been reported.
          </p>

          <div className="pt-2 border-t border-line flex justify-between font-mono text-[11px] text-sage">
            <span>Prepared by: State Emergency Operations Center (SEOC), Rajiv Bhawan</span>
            <span>Sign-off: S. K. Mohapatra, IAS, EOC Director</span>
          </div>
        </div>
      </GovCard>
    </div>
  );
};
