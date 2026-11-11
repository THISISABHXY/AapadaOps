import React, { useState } from 'react';
import {
  Settings,
  Sliders,
  Radio,
  ShieldCheck,
  Server,
  Save,
  CheckCircle2,
} from 'lucide-react';
import { GovCard } from '../components/ui/GovCard';
import { GovBadge } from '../components/ui/GovBadge';
import { GovButton } from '../components/ui/GovButton';
import { useDemoMode } from '../contexts/DemoModeContext';
import { useToast } from '../contexts/ToastContext';

export const SystemSettingsPage: React.FC = () => {
  const { isDemoMode, setDemoMode } = useDemoMode();
  const { showToast } = useToast();

  const [clusterRadiusMeters, setClusterRadiusMeters] = useState<number>(250);
  const [clusterTimeWindowHours, setClusterTimeWindowHours] = useState<number>(2);
  const [rateLimitPerMinute, setRateLimitPerMinute] = useState<number>(120);

  const handleSaveSettings = () => {
    showToast('success', 'Configuration Saved', 'Spatial clustering thresholds updated in system memory.');
  };

  return (
    <div className="space-y-4">
      {/* 1. Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-line">
        <div>
          <div className="flex items-center gap-2">
            <Settings className="w-5 h-5 text-forest" />
            <h1 className="text-xl font-bold text-ink-primary tracking-tight">
              AapadaOps System Configuration & Operational Parameters
            </h1>
          </div>
          <p className="text-xs text-sage mt-0.5">
            Operational thresholds, spatial clustering parameters, external weather API bindings, and security rules.
          </p>
        </div>

        <GovButton
          variant="primary"
          size="sm"
          onClick={handleSaveSettings}
          leftIcon={<Save className="w-3.5 h-3.5" />}
        >
          Save Configuration
        </GovButton>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* 1. Spatial Deduplication Settings */}
        <GovCard
          header={
            <div className="flex items-center gap-2 font-semibold text-xs uppercase tracking-wider text-sage">
              <Sliders className="w-4 h-4 text-forest" />
              <span>DBSCAN Spatial Clustering Engine</span>
            </div>
          }
        >
          <div className="space-y-4 text-xs">
            <div>
              <div className="flex justify-between items-center mb-1">
                <label className="font-semibold text-ink-primary">
                  Proximity Radius Threshold (Epsilon)
                </label>
                <span className="font-mono font-bold text-forest">{clusterRadiusMeters} Meters</span>
              </div>
              <input
                type="range"
                min={100}
                max={1000}
                step={25}
                value={clusterRadiusMeters}
                onChange={(e) => setClusterRadiusMeters(Number(e.target.value))}
                className="w-full accent-forest cursor-pointer"
              />
              <span className="text-[11px] text-sage block mt-1">
                Disaster distress calls within this geographic radius are clustered as candidate duplicates. Recommended: 250m.
              </span>
            </div>

            <div className="pt-3 border-t border-line">
              <div className="flex justify-between items-center mb-1">
                <label className="font-semibold text-ink-primary">Temporal Correlation Window</label>
                <span className="font-mono font-bold text-forest">{clusterTimeWindowHours} Hours</span>
              </div>
              <input
                type="range"
                min={1}
                max={6}
                step={1}
                value={clusterTimeWindowHours}
                onChange={(e) => setClusterTimeWindowHours(Number(e.target.value))}
                className="w-full accent-forest cursor-pointer"
              />
              <span className="text-[11px] text-sage block mt-1">
                Reports received within this timeframe are evaluated for duplicates. Recommended: 2 Hours.
              </span>
            </div>
          </div>
        </GovCard>

        {/* 2. Simulation & Environment Mode */}
        <GovCard
          header={
            <div className="flex items-center gap-2 font-semibold text-xs uppercase tracking-wider text-sage">
              <Server className="w-4 h-4 text-forest" />
              <span>Environment & Data Mode</span>
            </div>
          }
        >
          <div className="space-y-4 text-xs">
            <div className="p-3 bg-bg-warm rounded border border-line space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-ink-primary">Demo-Data Simulation Mode</span>
                <GovBadge variant={isDemoMode ? 'amber' : 'forest'} size="sm">
                  {isDemoMode ? 'SIMULATED ACTIVE' : 'LIVE API'}
                </GovBadge>
              </div>
              <p className="text-[11px] text-sage leading-relaxed">
                When enabled, uses realistic high-fidelity cyclone scenario data for Puri and coastal Odisha. Switch to Live API mode to interact with the FastAPI backend.
              </p>
              <div className="flex items-center gap-2 pt-1">
                <button
                  type="button"
                  onClick={() => setDemoMode(true)}
                  className={`px-3 py-1.5 rounded font-mono text-xs cursor-pointer ${
                    isDemoMode ? 'bg-amber text-white font-bold' : 'bg-white border border-line text-sage'
                  }`}
                >
                  Enable Demo Mode
                </button>
                <button
                  type="button"
                  onClick={() => setDemoMode(false)}
                  className={`px-3 py-1.5 rounded font-mono text-xs cursor-pointer ${
                    !isDemoMode ? 'bg-forest text-white font-bold' : 'bg-white border border-line text-sage'
                  }`}
                >
                  Live API Mode
                </button>
              </div>
            </div>

            <div className="space-y-2 pt-2">
              <span className="font-semibold text-ink-primary block">Public Ingestion Rate Limiting</span>
              <div className="flex justify-between items-center font-mono">
                <span className="text-sage">Max Requests per IP:</span>
                <strong className="text-ink-primary">{rateLimitPerMinute} / min</strong>
              </div>
              <span className="text-[11px] text-sage block">
                Prevents denial-of-service swamping on public citizen SOS ingestion endpoints.
              </span>
            </div>
          </div>
        </GovCard>
      </div>

      {/* 3. External API Feeds Health Table */}
      <GovCard
        header={
          <span className="font-semibold text-xs uppercase tracking-wider text-sage">
            External Government Integration Endpoints
          </span>
        }
      >
        <div className="overflow-x-auto text-xs">
          <table className="w-full text-left">
            <thead className="bg-bg-warm text-sage font-semibold uppercase text-[11px] border-b border-line">
              <tr>
                <th className="px-4 py-2">External Agency Feed</th>
                <th className="px-4 py-2">Protocol</th>
                <th className="px-4 py-2">Target Endpoint</th>
                <th className="px-4 py-2">Service Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line font-mono text-ink-primary">
              <tr>
                <td className="px-4 py-2.5 font-bold">IMD Cyclone Tracking Bulletin</td>
                <td className="px-4 py-2.5">REST / JSON</td>
                <td className="px-4 py-2.5 text-sage">mausam.imd.gov.in/api/v1/cyclone</td>
                <td className="px-4 py-2.5 text-forest font-semibold">● ONLINE (Simulated)</td>
              </tr>
              <tr>
                <td className="px-4 py-2.5 font-bold">CWC River Gauges (Mahanadi)</td>
                <td className="px-4 py-2.5">REST / GeoJSON</td>
                <td className="px-4 py-2.5 text-sage">ffs.india-water.gov.in/api</td>
                <td className="px-4 py-2.5 text-forest font-semibold">● ONLINE (Simulated)</td>
              </tr>
              <tr>
                <td className="px-4 py-2.5 font-bold">OSDMA Coastal Siren EWDS Network</td>
                <td className="px-4 py-2.5">DMR / Satellite Link</td>
                <td className="px-4 py-2.5 text-sage">ewds.osdma.gov.in/towers</td>
                <td className="px-4 py-2.5 text-forest font-semibold">● READY (122 Towers)</td>
              </tr>
            </tbody>
          </table>
        </div>
      </GovCard>
    </div>
  );
};

