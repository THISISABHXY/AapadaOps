import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Layers,
  Filter,
  ShieldAlert,
  Building2,
  Ship,
  Wind,
  Droplets,
  X,
  ExternalLink,
} from 'lucide-react';
import { GovCard } from '../components/ui/GovCard';
import { GovBadge } from '../components/ui/GovBadge';
import { GovButton } from '../components/ui/GovButton';
import { incidentService } from '../services/incidentService';
import { shelterService } from '../services/shelterService';
import { taskService } from '../services/taskService';
import { ODISHA_DISTRICTS } from '../services/demoDataService';
import { Incident } from '../types/incident';
import { formatCoordinates, formatTimeAgo } from '../utilities/formatters';

export const IncidentMapPage: React.FC = () => {
  const [selectedDistrict, setSelectedDistrict] = useState<string>('ALL');
  const [showCycloneTrack, setShowCycloneTrack] = useState<boolean>(true);
  const [showFloodZones, setShowFloodZones] = useState<boolean>(true);
  const [showShelters, setShowShelters] = useState<boolean>(true);
  const [showUnits, setShowUnits] = useState<boolean>(true);
  const [showIncidents, setShowIncidents] = useState<boolean>(true);

  const { data: incidents = [] } = useQuery({
    queryKey: ['incidents', selectedDistrict],
    queryFn: () => incidentService.getIncidents({ districtId: selectedDistrict }),
  });

  const { data: shelters = [] } = useQuery({
    queryKey: ['shelters', selectedDistrict],
    queryFn: () => shelterService.getShelters(selectedDistrict),
  });

  const { data: tacticalUnits = [] } = useQuery({
    queryKey: ['units', selectedDistrict],
    queryFn: () => taskService.getTacticalUnits(selectedDistrict),
  });

  const [activeIncident, setActiveIncident] = useState<Incident | null>(null);

  useEffect(() => {
    if (!activeIncident && incidents.length > 0) {
      setActiveIncident(incidents[0]);
    }
  }, [incidents, activeIncident]);

  return (
    <div className="h-[calc(100vh-6rem)] flex flex-col space-y-2">
      {/* 1. Map Top Layer Controls Bar */}
      <div className="bg-white border border-line rounded px-3 py-2 flex flex-wrap items-center justify-between gap-2 shadow-xs text-xs">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 font-bold text-ink-primary">
            <Layers className="w-4 h-4 text-forest" />
            <span>GIS Map Controls</span>
          </div>

          <div className="h-4 w-px bg-line hidden sm:block" />

          {/* District Selector */}
          <div className="flex items-center gap-1.5">
            <span className="text-sage font-medium">District:</span>
            <select
              value={selectedDistrict}
              onChange={(e) => setSelectedDistrict(e.target.value)}
              className="bg-bg-warm border border-line rounded px-2 py-1 font-semibold text-ink-primary text-xs"
            >
              <option value="ALL">All Coastal Odisha</option>
              {ODISHA_DISTRICTS.map((d) => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Layer Checkboxes */}
        <div className="flex flex-wrap items-center gap-2 sm:gap-4 text-xs select-none">
          <label className="flex items-center gap-1.5 cursor-pointer text-ink-primary">
            <input
              type="checkbox"
              checked={showCycloneTrack}
              onChange={(e) => setShowCycloneTrack(e.target.checked)}
              className="rounded text-forest focus:ring-forest"
            />
            <span className="flex items-center gap-1 text-[11px] font-medium">
              <Wind className="w-3.5 h-3.5 text-emergency" /> Cyclone Cone
            </span>
          </label>

          <label className="flex items-center gap-1.5 cursor-pointer text-ink-primary">
            <input
              type="checkbox"
              checked={showFloodZones}
              onChange={(e) => setShowFloodZones(e.target.checked)}
              className="rounded text-forest focus:ring-forest"
            />
            <span className="flex items-center gap-1 text-[11px] font-medium">
              <Droplets className="w-3.5 h-3.5 text-amber-dark" /> Inundation Zones
            </span>
          </label>

          <label className="flex items-center gap-1.5 cursor-pointer text-ink-primary">
            <input
              type="checkbox"
              checked={showIncidents}
              onChange={(e) => setShowIncidents(e.target.checked)}
              className="rounded text-forest focus:ring-forest"
            />
            <span className="flex items-center gap-1 text-[11px] font-medium">
              <ShieldAlert className="w-3.5 h-3.5 text-emergency" /> Incidents ({incidents.length})
            </span>
          </label>

          <label className="flex items-center gap-1.5 cursor-pointer text-ink-primary">
            <input
              type="checkbox"
              checked={showShelters}
              onChange={(e) => setShowShelters(e.target.checked)}
              className="rounded text-forest focus:ring-forest"
            />
            <span className="flex items-center gap-1 text-[11px] font-medium">
              <Building2 className="w-3.5 h-3.5 text-forest" /> Shelters ({shelters.length})
            </span>
          </label>

          <label className="flex items-center gap-1.5 cursor-pointer text-ink-primary">
            <input
              type="checkbox"
              checked={showUnits}
              onChange={(e) => setShowUnits(e.target.checked)}
              className="rounded text-forest focus:ring-forest"
            />
            <span className="flex items-center gap-1 text-[11px] font-medium">
              <Ship className="w-3.5 h-3.5 text-sage" /> Tactical Units ({tacticalUnits.length})
            </span>
          </label>
        </div>
      </div>

      {/* 2. Map Canvas & Interactive Drawer */}
      <div className="flex-1 relative bg-white border border-line rounded overflow-hidden shadow-xs flex">
        {/* Full Visual Map Display Area */}
        <div className="flex-1 bg-bg-warm relative overflow-hidden flex flex-col justify-between p-4">
          {/* Subtle Grid Canvas */}
          <div className="absolute inset-0 opacity-20 pointer-events-none bg-[radial-gradient(#365B4A_1px,transparent_1px)] [background-size:24px_24px]" />

          {/* Active Storm Track Advisory Box */}
          {showCycloneTrack && (
            <div className="z-10 bg-white/95 border border-line rounded p-3 max-w-sm shadow-xs text-xs space-y-1">
              <div className="flex items-center justify-between font-bold text-emergency">
                <span className="flex items-center gap-1.5">
                  <Wind className="w-4 h-4" /> IMD Track Bulletin #14
                </span>
                <span className="font-mono text-[10px] bg-emergency-subtle px-1.5 py-0.5 rounded">
                  LANDFALL IN 14H
                </span>
              </div>
              <p className="text-sage text-[11px]">
                Coordinates: 19.4°N, 85.9°E. Sustained winds 165 km/h. Moving North-Northwest toward Puri coastline.
              </p>
            </div>
          )}

          {/* Map Vector Pins Simulation */}
          <div className="z-10 my-auto flex flex-wrap gap-3 justify-center items-center">
            {showIncidents &&
              incidents.slice(0, 8).map((inc) => (
                <button
                  key={inc.id}
                  onClick={() => setActiveIncident(inc)}
                  className={`p-2 rounded border shadow-sm transition-all text-left max-w-xs cursor-pointer ${
                    activeIncident?.id === inc.id
                      ? 'bg-white border-forest ring-2 ring-forest/20'
                      : 'bg-white/90 border-line hover:border-line-dark'
                  }`}
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-mono text-[11px] font-bold text-ink-primary">
                      {inc.incidentCode}
                    </span>
                    <GovBadge
                      variant={inc.reportedSeverity === 'CRITICAL' ? 'emergency' : 'amber'}
                      size="sm"
                    >
                      {inc.hazardType}
                    </GovBadge>
                  </div>
                  <div className="text-xs font-semibold text-ink-primary mt-1 truncate">
                    {inc.villageName}, {inc.blockName || inc.districtName}
                  </div>
                  <div className="text-[11px] text-sage font-mono mt-0.5">
                    {formatCoordinates(inc.latitude, inc.longitude)}
                  </div>
                </button>
              ))}
          </div>

          {/* Map Footer Metadata */}
          <div className="z-10 flex items-center justify-between text-[11px] font-mono text-sage bg-white/90 px-3 py-1.5 rounded border border-line">
            <span>Projection: EPSG:4326 (WGS 84 GPS Native)</span>
            <span>OSDMA / Survey of India Digital Basemap</span>
          </div>
        </div>

        {/* Selected Pin Inspector Slide-out Panel (Desktop Right 340px) */}
        {activeIncident && (
          <aside className="w-80 sm:w-96 bg-white border-l border-line p-4 overflow-y-auto flex flex-col justify-between shadow-sm z-20">
            <div className="space-y-4">
              <div className="flex items-start justify-between pb-3 border-b border-line">
                <div>
                  <div className="flex items-center gap-1.5">
                    <span className="font-mono text-xs font-bold text-ink-primary">
                      {activeIncident.incidentCode}
                    </span>
                    <GovBadge
                      variant={activeIncident.status === 'VERIFIED' ? 'forest' : 'amber'}
                      size="sm"
                    >
                      {activeIncident.status}
                    </GovBadge>
                  </div>
                  <h3 className="text-sm font-semibold text-ink-primary mt-1">
                    {activeIncident.villageName}, {activeIncident.blockName}
                  </h3>
                </div>
                <button
                  onClick={() => setActiveIncident(null)}
                  className="p-1 text-sage hover:text-ink-primary"
                  aria-label="Close details"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Coordinates and Hazard */}
              <div className="grid grid-cols-2 gap-2 text-xs font-mono p-2.5 bg-bg-warm rounded border border-line">
                <div>
                  <span className="text-sage block text-[10px]">Hazard Category</span>
                  <strong className="text-ink-primary">{activeIncident.hazardType}</strong>
                </div>
                <div>
                  <span className="text-sage block text-[10px]">Stranded Headcount</span>
                  <strong className="text-emergency">{activeIncident.personsStranded} Persons</strong>
                </div>
                <div className="col-span-2 pt-1 border-t border-line/60">
                  <span className="text-sage block text-[10px]">GPS Coordinates</span>
                  <span className="text-ink-primary">
                    {formatCoordinates(activeIncident.latitude, activeIncident.longitude)}
                  </span>
                </div>
              </div>

              {/* Citizen Description */}
              <div className="space-y-1">
                <span className="text-xs font-semibold text-ink-primary">Caller Narrative:</span>
                <p className="text-xs text-ink-secondary p-2.5 bg-bg-warm rounded border border-line leading-relaxed">
                  "{activeIncident.rawDescription}"
                </p>
                <div className="text-[11px] text-sage flex justify-between font-mono">
                  <span>Caller: {activeIncident.callerName}</span>
                  <span>{formatTimeAgo(activeIncident.createdAt)}</span>
                </div>
              </div>

              {/* AI Extraction Callout if available */}
              {activeIncident.aiEvaluation && (
                <div className="p-3 bg-bg-warm border-l-3 border-sage rounded text-xs space-y-1">
                  <div className="font-mono text-[10px] uppercase font-bold text-sage">
                    AI Entity Detection (Advisory)
                  </div>
                  <div className="text-ink-secondary text-[11px]">
                    Extracted water depth: {activeIncident.aiEvaluation.extractedEntities.waterDepthFeet} ft.
                    High life-threat indicators detected.
                  </div>
                </div>
              )}
            </div>

            {/* Quick Action Buttons */}
            <div className="pt-4 border-t border-line space-y-2">
              <a
                href={`/incidents/${activeIncident.id}`}
                className="w-full inline-flex items-center justify-center gap-1.5 h-9 bg-forest hover:bg-forest-dark text-white text-xs font-semibold rounded transition-colors"
              >
                <span>Open Full Incident Case File</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </a>

              <a
                href={`/verification`}
                className="w-full inline-flex items-center justify-center gap-1.5 h-8 bg-white border border-line hover:bg-bg-warm text-ink-primary text-xs font-medium rounded transition-colors"
              >
                <span>Verify in Queue</span>
              </a>
            </div>
          </aside>
        )}
      </div>
    </div>
  );
};

