import React, { useState, useEffect, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Polygon,
  Polyline,
  Tooltip,
  useMap,
} from 'react-leaflet';
import L from 'leaflet';
import {
  Layers,
  ShieldAlert,
  Building2,
  Ship,
  Wind,
  Droplets,
  X,
  ExternalLink,
  MapPin,
  Compass,
  AlertTriangle,
  Info,
  Users,
  Radio,
  CheckCircle2,
  Key,
  Globe,
  Settings2,
  Check,
} from 'lucide-react';
import { GovBadge } from '../components/ui/GovBadge';
import { GovButton } from '../components/ui/GovButton';
import { incidentService } from '../services/incidentService';
import { shelterService } from '../services/shelterService';
import { taskService } from '../services/taskService';
import { ODISHA_DISTRICTS } from '../services/demoDataService';
import { Incident } from '../types/incident';
import { CycloneShelter } from '../types/shelter';
import { TacticalUnit } from '../types/task';
import { formatCoordinates, formatTimeAgo } from '../utilities/formatters';

// ============================================================================
// Geographic Reference & District Centroids (Coastal & Deltaic Odisha)
// ============================================================================
interface DistrictGeoTarget {
  center: [number, number];
  zoom: number;
}

const DISTRICT_CENTROIDS: Record<string, DistrictGeoTarget> = {
  ALL: { center: [20.35, 86.15], zoom: 8 },
  Puri: { center: [19.8135, 85.8312], zoom: 10 },
  Kendrapara: { center: [20.5000, 86.4200], zoom: 10 },
  Jagatsinghpur: { center: [20.2500, 86.1700], zoom: 10 },
  Balasore: { center: [21.4934, 86.9135], zoom: 10 },
  Bhadrak: { center: [21.0544, 86.4950], zoom: 10 },
  Ganjam: { center: [19.3800, 85.0600], zoom: 10 },
  Jajpur: { center: [20.8500, 86.3300], zoom: 10 },
  Cuttack: { center: [20.4625, 85.8828], zoom: 10 },
  Khordha: { center: [20.1900, 85.6200], zoom: 10 },
};

export type BasemapProvider = 'OSM' | 'ESRI_TOPO' | 'ESRI_SATELLITE' | 'CARTO';

// ============================================================================
// Dynamic Leaflet Custom DivIcons (Zero External Image Dependency)
// ============================================================================
const createIncidentIcon = (severity: string, isSelected: boolean) => {
  const isCritical = severity === 'CRITICAL';
  const bgColor = isCritical ? '#B64C45' : '#D7A65B';
  const ringHtml = isCritical || isSelected
    ? `<span class="absolute -inset-1.5 rounded-full marker-pulse-ring" style="background-color: ${bgColor}40; border: 1.5px solid ${bgColor};"></span>`
    : '';

  return L.divIcon({
    className: 'custom-incident-pin-wrapper',
    html: `
      <div class="relative flex items-center justify-center cursor-pointer" style="width: 32px; height: 32px;">
        ${ringHtml}
        <div class="relative flex items-center justify-center rounded-full shadow-md text-white font-bold" 
             style="background-color: ${bgColor}; width: 28px; height: 28px; border: 2px solid #FFFFFF;">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
            <line x1="12" y1="9" x2="12" y2="13"/>
            <line x1="12" y1="17" x2="12.01" y2="17"/>
          </svg>
        </div>
      </div>
    `,
    iconSize: [32, 32],
    iconAnchor: [16, 16],
    popupAnchor: [0, -18],
  });
};

const createShelterIcon = () => {
  return L.divIcon({
    className: 'custom-shelter-pin-wrapper',
    html: `
      <div class="relative flex items-center justify-center cursor-pointer" style="width: 28px; height: 28px;">
        <div class="flex items-center justify-center rounded-md shadow-sm text-white" 
             style="background-color: #365B4A; width: 26px; height: 26px; border: 1.5px solid #FFFFFF;">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z"/>
            <path d="M6 12H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2"/>
            <path d="M18 9h2a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-2"/>
            <path d="M10 6h4"/><path d="M10 10h4"/><path d="M10 14h4"/><path d="M10 18h4"/>
          </svg>
        </div>
      </div>
    `,
    iconSize: [28, 28],
    iconAnchor: [14, 14],
    popupAnchor: [0, -16],
  });
};

const createTacticalUnitIcon = () => {
  return L.divIcon({
    className: 'custom-unit-pin-wrapper',
    html: `
      <div class="relative flex items-center justify-center cursor-pointer" style="width: 28px; height: 28px;">
        <div class="flex items-center justify-center rounded-full shadow-sm text-white" 
             style="background-color: #1E3A8A; width: 26px; height: 26px; border: 1.5px solid #FFFFFF;">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M2 21c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1 .6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/>
            <path d="M19.38 20A11.6 11.6 0 0 0 21 14l-9-4-9 4c0 2.9.94 5.34 2.81 7.76"/>
            <path d="M12 2v8"/>
          </svg>
        </div>
      </div>
    `,
    iconSize: [28, 28],
    iconAnchor: [14, 14],
    popupAnchor: [0, -16],
  });
};

// ============================================================================
// Map Controller Subcomponent (Smooth Pan / Zoom on State Change)
// ============================================================================
const MapController: React.FC<{ target: DistrictGeoTarget }> = ({ target }) => {
  const map = useMap();
  useEffect(() => {
    map.flyTo(target.center, target.zoom, { duration: 1.2 });
  }, [target, map]);
  return null;
};

// ============================================================================
// Realistic Odisha Geospatial Inundation Zones & IMD Cyclone Track
// ============================================================================
const BRAHMANI_BAITARANI_INUNDATION_ZONE: [number, number][] = [
  [20.5200, 86.3500],
  [20.6500, 86.4800],
  [20.7800, 86.7200],
  [20.7200, 86.8500],
  [20.5800, 86.7800],
  [20.4800, 86.5200],
  [20.5200, 86.3500],
];

const MAHANADI_ESTUARY_INUNDATION_ZONE: [number, number][] = [
  [19.8800, 85.5500],
  [19.9800, 85.7200],
  [19.9500, 86.0500],
  [19.8000, 85.9800],
  [19.6800, 85.6500],
  [19.8800, 85.5500],
];

const SUBARNAREKHA_BASIN_ZONE: [number, number][] = [
  [21.5500, 86.9500],
  [21.6800, 87.1200],
  [21.6000, 87.2500],
  [21.4800, 87.0500],
  [21.5500, 86.9500],
];

// IMD Bulletin Track History & Projected Landfall Polyline
const CYCLONE_HISTORIC_TRACK: [number, number][] = [
  [17.60, 87.50],
  [18.30, 86.90],
  [19.00, 86.40],
  [19.40, 85.90],
];

const CYCLONE_FORECAST_TRACK: [number, number][] = [
  [19.40, 85.90],
  [19.85, 85.85],
  [20.40, 85.75],
  [21.10, 85.60],
];

// Cyclonic Gale Wind Uncertainty Cone (165 km/h)
const CYCLONE_UNCERTAINTY_CONE: [number, number][] = [
  [19.40, 85.90],
  [19.70, 85.30],
  [20.60, 85.20],
  [21.20, 85.90],
  [20.80, 86.40],
  [20.10, 86.60],
  [19.50, 86.30],
  [19.40, 85.90],
];

export const IncidentMapPage: React.FC = () => {
  const [selectedDistrict, setSelectedDistrict] = useState<string>('ALL');
  const [showCycloneTrack, setShowCycloneTrack] = useState<boolean>(true);
  const [showFloodZones, setShowFloodZones] = useState<boolean>(true);
  const [showShelters, setShowShelters] = useState<boolean>(true);
  const [showUnits, setShowUnits] = useState<boolean>(true);
  const [showIncidents, setShowIncidents] = useState<boolean>(true);
  const [activeIncident, setActiveIncident] = useState<Incident | null>(null);

  // Basemap & API Key Configuration State
  const [baseLayer, setBaseLayer] = useState<BasemapProvider>(() => {
    return (localStorage.getItem('aapadaops_basemap_provider') as BasemapProvider) || 'OSM';
  });
  const [cartoApiKey, setCartoApiKey] = useState<string>(() => {
    return localStorage.getItem('aapadaops_carto_api_key') || '';
  });
  const [tempApiKey, setTempApiKey] = useState<string>(cartoApiKey);
  const [isApiKeyModalOpen, setIsApiKeyModalOpen] = useState<boolean>(false);
  const [keySavedMessage, setKeySavedMessage] = useState<boolean>(false);

  // Queries for data layers
  const { data: incidents = [] } = useQuery<Incident[]>({
    queryKey: ['incidents', selectedDistrict],
    queryFn: () => incidentService.getIncidents({ districtId: selectedDistrict }),
  });

  const { data: shelters = [] } = useQuery<CycloneShelter[]>({
    queryKey: ['shelters', selectedDistrict],
    queryFn: () => shelterService.getShelters(selectedDistrict),
  });

  const { data: tacticalUnits = [] } = useQuery<TacticalUnit[]>({
    queryKey: ['units', selectedDistrict],
    queryFn: () => taskService.getTacticalUnits(selectedDistrict),
  });

  // Calculate dynamic target for map pan/zoom
  const mapTarget = useMemo<DistrictGeoTarget>(() => {
    if (selectedDistrict && DISTRICT_CENTROIDS[selectedDistrict]) {
      return DISTRICT_CENTROIDS[selectedDistrict];
    }
    return DISTRICT_CENTROIDS.ALL;
  }, [selectedDistrict]);

  // Set default active incident
  useEffect(() => {
    if (!activeIncident && incidents.length > 0) {
      setActiveIncident(incidents[0]);
    }
  }, [incidents, activeIncident]);

  const handleSaveApiKey = (keyToSave: string) => {
    const trimmed = keyToSave.trim();
    setCartoApiKey(trimmed);
    localStorage.setItem('aapadaops_carto_api_key', trimmed);
    setKeySavedMessage(true);
    setTimeout(() => setKeySavedMessage(false), 3000);
  };

  return (
    <div className="h-[calc(100vh-6rem)] flex flex-col space-y-2">
      {/* 1. Map Top Layer Controls Bar */}
      <div className="bg-white border border-line rounded px-3 py-2 flex flex-wrap items-center justify-between gap-2 shadow-xs text-xs z-10">
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
              className="bg-bg-warm border border-line rounded px-2 py-1 font-semibold text-ink-primary text-xs cursor-pointer focus:outline-hidden focus:ring-1 focus:ring-forest"
            >
              <option value="ALL">All Coastal Odisha</option>
              {ODISHA_DISTRICTS.map((d) => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
          </div>

          <div className="h-4 w-px bg-line hidden sm:block" />

          {/* Basemap Tile Provider Selector */}
          <div className="flex items-center gap-1.5">
            <Globe className="w-3.5 h-3.5 text-sage" />
            <span className="text-sage font-medium">Basemap:</span>
            <select
              value={baseLayer}
              onChange={(e) => {
                const val = e.target.value as BasemapProvider;
                setBaseLayer(val);
                localStorage.setItem('aapadaops_basemap_provider', val);
              }}
              className="bg-bg-warm border border-line rounded px-2 py-1 font-semibold text-ink-primary text-xs cursor-pointer focus:outline-hidden focus:ring-1 focus:ring-forest"
            >
              <option value="OSM">🗺️ OpenStreetMap (Free, No Key)</option>
              <option value="ESRI_TOPO">⛰️ ESRI Topography (Free, No Key)</option>
              <option value="ESRI_SATELLITE">🛰️ ESRI Satellite (Free, No Key)</option>
              <option value="CARTO">🧭 CARTO Voyager (with API Key)</option>
            </select>
          </div>

          {/* API Key Configuration Button */}
          <button
            onClick={() => {
              setTempApiKey(cartoApiKey);
              setIsApiKeyModalOpen(true);
            }}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded text-[11px] font-semibold border transition-colors cursor-pointer ${
              cartoApiKey
                ? 'bg-forest-subtle border-forest/30 text-forest hover:bg-forest/10'
                : 'bg-bg-warm border-line text-ink-primary hover:bg-line'
            }`}
            title="Configure Map Tile API Key"
          >
            <Key className="w-3.5 h-3.5 text-forest" />
            <span>{cartoApiKey ? 'API Key Active' : 'Add API Key'}</span>
            {cartoApiKey && <span className="w-1.5 h-1.5 rounded-full bg-forest animate-pulse" />}
          </button>
        </div>

        {/* Layer Checkboxes */}
        <div className="flex flex-wrap items-center gap-2 sm:gap-4 text-xs select-none">
          <label className="flex items-center gap-1.5 cursor-pointer text-ink-primary hover:text-forest transition-colors">
            <input
              type="checkbox"
              checked={showCycloneTrack}
              onChange={(e) => setShowCycloneTrack(e.target.checked)}
              className="rounded text-forest focus:ring-forest cursor-pointer"
            />
            <span className="flex items-center gap-1 text-[11px] font-medium">
              <Wind className="w-3.5 h-3.5 text-emergency" /> Cyclone Cone
            </span>
          </label>

          <label className="flex items-center gap-1.5 cursor-pointer text-ink-primary hover:text-forest transition-colors">
            <input
              type="checkbox"
              checked={showFloodZones}
              onChange={(e) => setShowFloodZones(e.target.checked)}
              className="rounded text-forest focus:ring-forest cursor-pointer"
            />
            <span className="flex items-center gap-1 text-[11px] font-medium">
              <Droplets className="w-3.5 h-3.5 text-sky-600" /> Inundation Zones
            </span>
          </label>

          <label className="flex items-center gap-1.5 cursor-pointer text-ink-primary hover:text-forest transition-colors">
            <input
              type="checkbox"
              checked={showIncidents}
              onChange={(e) => setShowIncidents(e.target.checked)}
              className="rounded text-forest focus:ring-forest cursor-pointer"
            />
            <span className="flex items-center gap-1 text-[11px] font-medium">
              <ShieldAlert className="w-3.5 h-3.5 text-emergency" /> Incidents ({incidents.length})
            </span>
          </label>

          <label className="flex items-center gap-1.5 cursor-pointer text-ink-primary hover:text-forest transition-colors">
            <input
              type="checkbox"
              checked={showShelters}
              onChange={(e) => setShowShelters(e.target.checked)}
              className="rounded text-forest focus:ring-forest cursor-pointer"
            />
            <span className="flex items-center gap-1 text-[11px] font-medium">
              <Building2 className="w-3.5 h-3.5 text-forest" /> Shelters ({shelters.length})
            </span>
          </label>

          <label className="flex items-center gap-1.5 cursor-pointer text-ink-primary hover:text-forest transition-colors">
            <input
              type="checkbox"
              checked={showUnits}
              onChange={(e) => setShowUnits(e.target.checked)}
              className="rounded text-forest focus:ring-forest cursor-pointer"
            />
            <span className="flex items-center gap-1 text-[11px] font-medium">
              <Ship className="w-3.5 h-3.5 text-blue-900" /> Tactical Units ({tacticalUnits.length})
            </span>
          </label>
        </div>
      </div>

      {/* 2. Interactive Map Canvas & Right Inspection Sidebar */}
      <div className="flex-1 relative bg-white border border-line rounded overflow-hidden shadow-xs flex">
        {/* Real Interactive Leaflet GIS Map Canvas */}
        <div className="flex-1 relative h-full w-full">
          <MapContainer
            center={mapTarget.center}
            zoom={mapTarget.zoom}
            scrollWheelZoom={true}
            zoomControl={true}
            className="h-full w-full"
            style={{ height: '100%', width: '100%', backgroundColor: '#EFEFEA' }}
          >
            <MapController target={mapTarget} />

            {/* Base Tile Layer Dynamic Selection */}
            {baseLayer === 'OSM' && (
              <TileLayer
                key="osm-tile-layer"
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, OSDMA Basemap'
                url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
                maxZoom={19}
              />
            )}

            {baseLayer === 'ESRI_TOPO' && (
              <TileLayer
                key="esri-topo-layer"
                attribution='Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ, TomTom, USGS, OSDMA'
                url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}"
                maxZoom={18}
              />
            )}

            {baseLayer === 'ESRI_SATELLITE' && (
              <TileLayer
                key="esri-sat-layer"
                attribution='Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP'
                url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                maxZoom={19}
              />
            )}

            {baseLayer === 'CARTO' && (
              <TileLayer
                key={`carto-voyager-${cartoApiKey}`}
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>, &copy; <a href="https://carto.com/">CARTO</a>'
                url={
                  cartoApiKey
                    ? `https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png?api_key=${encodeURIComponent(cartoApiKey)}`
                    : 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png'
                }
                maxZoom={19}
              />
            )}

            {/* Inundation Zones (Flood Polygons) */}
            {showFloodZones && (
              <>
                <Polygon
                  positions={BRAHMANI_BAITARANI_INUNDATION_ZONE}
                  pathOptions={{
                    color: '#0284C7',
                    fillColor: '#38BDF8',
                    fillOpacity: 0.25,
                    weight: 2,
                    dashArray: '5, 5',
                  }}
                >
                  <Tooltip sticky>
                    <div className="text-xs p-1">
                      <strong className="block text-sky-800">Brahmani-Baitarani Flood Basin</strong>
                      <span className="text-[11px] text-ink-secondary">Water Depth: 1.8m – 2.5m (Active Inundation)</span>
                    </div>
                  </Tooltip>
                </Polygon>

                <Polygon
                  positions={MAHANADI_ESTUARY_INUNDATION_ZONE}
                  pathOptions={{
                    color: '#0284C7',
                    fillColor: '#38BDF8',
                    fillOpacity: 0.22,
                    weight: 2,
                    dashArray: '5, 5',
                  }}
                >
                  <Tooltip sticky>
                    <div className="text-xs p-1">
                      <strong className="block text-sky-800">Mahanadi Estuary Inundation Sector</strong>
                      <span className="text-[11px] text-ink-secondary">Daya River Overspill (Depth: 1.2m – 1.9m)</span>
                    </div>
                  </Tooltip>
                </Polygon>

                <Polygon
                  positions={SUBARNAREKHA_BASIN_ZONE}
                  pathOptions={{
                    color: '#0284C7',
                    fillColor: '#38BDF8',
                    fillOpacity: 0.20,
                    weight: 1.5,
                    dashArray: '4, 4',
                  }}
                >
                  <Tooltip sticky>
                    <div className="text-xs p-1">
                      <strong className="block text-sky-800">Subarnarekha Coastal Inundation Zone</strong>
                      <span className="text-[11px] text-ink-secondary">Balasore Low-Lying Tidal Backwater</span>
                    </div>
                  </Tooltip>
                </Polygon>
              </>
            )}

            {/* Cyclone Cone & Storm Track Polyline */}
            {showCycloneTrack && (
              <>
                {/* Historic Track (Solid line) */}
                <Polyline
                  positions={CYCLONE_HISTORIC_TRACK}
                  pathOptions={{ color: '#B64C45', weight: 3 }}
                />

                {/* Forecast Landfall Track (Dashed line) */}
                <Polyline
                  positions={CYCLONE_FORECAST_TRACK}
                  pathOptions={{ color: '#B64C45', weight: 3, dashArray: '6, 6' }}
                />

                {/* Forecast Uncertainty Cone (Translucent Red) */}
                <Polygon
                  positions={CYCLONE_UNCERTAINTY_CONE}
                  pathOptions={{
                    color: '#B64C45',
                    fillColor: '#B64C45',
                    fillOpacity: 0.14,
                    weight: 1.5,
                    dashArray: '6, 6',
                  }}
                >
                  <Tooltip sticky>
                    <div className="text-xs p-1">
                      <strong className="block text-emergency">IMD Gale Wind Warning Cone</strong>
                      <span className="text-[11px] text-ink-secondary">Sustained Wind 165 km/h | Landfall Threat Area</span>
                    </div>
                  </Tooltip>
                </Polygon>

                {/* Eye Center Marker */}
                <Marker
                  position={[19.40, 85.90]}
                  icon={L.divIcon({
                    className: 'cyclone-eye-pin',
                    html: `
                      <div class="relative flex items-center justify-center" style="width: 32px; height: 32px;">
                        <span class="absolute -inset-2 rounded-full marker-pulse-ring" style="background-color: #B64C4530; border: 2px solid #B64C45;"></span>
                        <div class="flex items-center justify-center rounded-full bg-emergency text-white shadow-md font-bold" style="width: 24px; height: 24px; border: 2px solid #FFFFFF;">
                          🌀
                        </div>
                      </div>
                    `,
                    iconSize: [32, 32],
                    iconAnchor: [16, 16],
                  })}
                >
                  <Popup>
                    <div className="p-3 text-xs space-y-1">
                      <div className="flex items-center justify-between font-bold text-emergency">
                        <span>IMD Eye Bulletin #14</span>
                        <GovBadge variant="emergency" size="sm">LANDFALL 14H</GovBadge>
                      </div>
                      <p className="text-ink-secondary text-[11px]">
                        Coordinates: 19.4°N, 85.9°E. Sustained winds 165 km/h. Moving North-Northwest toward Puri coastline.
                      </p>
                    </div>
                  </Popup>
                </Marker>
              </>
            )}

            {/* Incidents Layer */}
            {showIncidents &&
              incidents.map((inc) => {
                const isSelected = activeIncident?.id === inc.id;
                return (
                  <Marker
                    key={inc.id}
                    position={[inc.latitude, inc.longitude]}
                    icon={createIncidentIcon(inc.reportedSeverity, isSelected)}
                    eventHandlers={{
                      click: () => setActiveIncident(inc),
                    }}
                  >
                    <Popup>
                      <div className="p-3 text-xs space-y-2 min-w-[220px]">
                        <div className="flex items-center justify-between gap-2 border-b border-line pb-1.5">
                          <span className="font-mono font-bold text-ink-primary">{inc.incidentCode}</span>
                          <GovBadge
                            variant={inc.reportedSeverity === 'CRITICAL' ? 'emergency' : 'amber'}
                            size="sm"
                          >
                            {inc.hazardType}
                          </GovBadge>
                        </div>
                        <div>
                          <div className="font-semibold text-ink-primary">
                            {inc.villageName || 'Sector'}, {inc.blockName || inc.districtName}
                          </div>
                          <div className="text-sage text-[11px] font-mono mt-0.5">
                            {formatCoordinates(inc.latitude, inc.longitude)}
                          </div>
                        </div>
                        <div className="flex items-center justify-between pt-1 border-t border-line/60">
                          <span className="text-[11px] text-sage">Stranded:</span>
                          <strong className="text-emergency font-bold">{inc.personsStranded} Persons</strong>
                        </div>
                        <button
                          onClick={() => setActiveIncident(inc)}
                          className="w-full mt-1.5 py-1 px-2 bg-forest hover:bg-forest-dark text-white text-[11px] font-semibold rounded transition-colors text-center cursor-pointer"
                        >
                          Inspect Details in Panel
                        </button>
                      </div>
                    </Popup>
                  </Marker>
                );
              })}

            {/* Multi-Purpose Cyclone Shelters Layer */}
            {showShelters &&
              shelters.map((s) => (
                <Marker
                  key={s.id}
                  position={[s.latitude, s.longitude]}
                  icon={createShelterIcon()}
                >
                  <Popup>
                    <div className="p-3 text-xs space-y-2 min-w-[220px]">
                      <div className="flex items-center justify-between gap-2 border-b border-line pb-1.5">
                        <span className="font-mono font-bold text-forest">{s.code}</span>
                        <GovBadge variant="forest" size="sm">SHELTER</GovBadge>
                      </div>
                      <div className="font-semibold text-ink-primary">{s.name}</div>
                      <div className="text-[11px] text-sage font-mono">
                        {s.blockName}, {s.districtName}
                      </div>
                      <div className="bg-bg-warm p-1.5 rounded border border-line text-[11px] space-y-1">
                        <div className="flex justify-between">
                          <span>Occupancy:</span>
                          <strong>{s.currentOccupancy} / {s.totalCapacity}</strong>
                        </div>
                        <div className="w-full bg-line rounded-full h-1.5 overflow-hidden">
                          <div
                            className="bg-forest h-1.5 rounded-full"
                            style={{ width: `${Math.min(100, (s.currentOccupancy / s.totalCapacity) * 100)}%` }}
                          />
                        </div>
                      </div>
                      <div className="flex items-center justify-between text-[10px] text-sage">
                        <span>DG Generator: {s.hasDgSet ? '✅ Ready' : '⚠️ None'}</span>
                        <span>Water: {s.waterSupplyDays || 3}d</span>
                      </div>
                    </div>
                  </Popup>
                </Marker>
              ))}

            {/* Tactical Units Layer */}
            {showUnits &&
              tacticalUnits.map((u) => (
                <Marker
                  key={u.id}
                  position={[u.latitude, u.longitude]}
                  icon={createTacticalUnitIcon()}
                >
                  <Popup>
                    <div className="p-3 text-xs space-y-2 min-w-[220px]">
                      <div className="flex items-center justify-between gap-2 border-b border-line pb-1.5">
                        <span className="font-mono font-bold text-blue-900">{u.unitCode}</span>
                        <GovBadge variant="neutral" size="sm">{u.organization}</GovBadge>
                      </div>
                      <div className="font-semibold text-ink-primary">{u.name}</div>
                      <div className="text-[11px] text-sage">Station: {u.homeStation}</div>
                      <div className="flex items-center justify-between pt-1 border-t border-line text-[11px]">
                        <span>Status:</span>
                        <strong className="text-forest font-semibold">{u.status}</strong>
                      </div>
                      <div className="text-[10px] text-sage">
                        Commander: {u.commanderName} ({u.crewCount} Personnel)
                      </div>
                    </div>
                  </Popup>
                </Marker>
              ))}
          </MapContainer>

          {/* Alert Banner if CARTO without API key */}
          {baseLayer === 'CARTO' && !cartoApiKey && (
            <div className="absolute top-16 left-3 z-[1000] bg-amber-subtle border border-amber/40 text-amber-dark rounded px-3 py-1.5 shadow-md text-xs flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber" />
              <span>CARTO requires an API key. Watermark is visible.</span>
              <button
                onClick={() => setIsApiKeyModalOpen(true)}
                className="underline font-bold hover:text-ink-primary cursor-pointer ml-1"
              >
                Add Key
              </button>
              <span className="text-sage font-mono">or</span>
              <button
                onClick={() => {
                  setBaseLayer('OSM');
                  localStorage.setItem('aapadaops_basemap_provider', 'OSM');
                }}
                className="bg-white px-2 py-0.5 rounded border border-amber/40 font-semibold hover:bg-bg-warm cursor-pointer"
              >
                Switch to OpenStreetMap (Free)
              </button>
            </div>
          )}

          {/* Floating IMD Track Bulletin Card (Top Left of Map) */}
          {showCycloneTrack && (
            <div className="absolute top-3 left-3 z-[1000] bg-white/95 backdrop-blur-xs border border-line rounded p-3 max-w-sm shadow-md text-xs space-y-1">
              <div className="flex items-center justify-between font-bold text-emergency">
                <span className="flex items-center gap-1.5">
                  <Wind className="w-4 h-4" /> IMD Track Bulletin #14
                </span>
                <span className="font-mono text-[10px] bg-emergency-subtle text-emergency px-1.5 py-0.5 rounded font-bold">
                  LANDFALL IN 14H
                </span>
              </div>
              <p className="text-sage text-[11px] leading-relaxed">
                Coordinates: 19.4°N, 85.9°E. Sustained winds 165 km/h. Moving North-Northwest toward Puri/Kendrapara coastline.
              </p>
            </div>
          )}

          {/* Floating Map Legend & Coordinate Scale (Bottom Left) */}
          <div className="absolute bottom-3 left-3 z-[1000] bg-white/95 backdrop-blur-xs border border-line rounded px-3 py-2 shadow-md text-[11px] space-y-1.5 max-w-xs select-none">
            <div className="font-bold text-ink-primary border-b border-line pb-1 flex items-center justify-between">
              <span>Operational GIS Legend</span>
              <span className="font-mono text-[10px] text-sage">
                {baseLayer === 'OSM' ? 'OSM Free Native' : baseLayer === 'ESRI_TOPO' ? 'ESRI Topo' : baseLayer === 'ESRI_SATELLITE' ? 'ESRI Sat' : 'CARTO'}
              </span>
            </div>
            <div className="grid grid-cols-2 gap-x-3 gap-y-1 text-ink-secondary text-[10px]">
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-emergency inline-block" />
                <span>Critical / Breach</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-amber inline-block" />
                <span>Moderate Incident</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-sm bg-forest inline-block" />
                <span>Cyclone Shelter (MCS)</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-blue-900 inline-block" />
                <span>ODRAF / Rescue Unit</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-3 h-1.5 bg-sky-400 border border-sky-600 inline-block" />
                <span>Inundation Zone</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-3 h-1 border-t-2 border-dashed border-emergency inline-block" />
                <span>Cyclone Gale Cone</span>
              </div>
            </div>
          </div>
        </div>

        {/* Selected Incident Inspector Slide-out Panel (Desktop Right 360px) */}
        {activeIncident && (
          <aside className="w-80 sm:w-96 bg-white border-l border-line p-4 overflow-y-auto flex flex-col justify-between shadow-lg z-20">
            <div className="space-y-4">
              <div className="flex items-start justify-between pb-3 border-b border-line">
                <div>
                  <div className="flex items-center gap-1.5">
                    <span className="font-mono text-xs font-bold text-ink-primary">
                      {activeIncident.incidentCode}
                    </span>
                    <GovBadge
                      variant={
                        activeIncident.status === 'VERIFIED'
                          ? 'forest'
                          : activeIncident.status === 'CRITICAL' || activeIncident.reportedSeverity === 'CRITICAL'
                          ? 'emergency'
                          : 'amber'
                      }
                      size="sm"
                    >
                      {activeIncident.status}
                    </GovBadge>
                  </div>
                  <h3 className="text-sm font-semibold text-ink-primary mt-1">
                    {activeIncident.villageName ? `${activeIncident.villageName}, ` : ''}
                    {activeIncident.blockName || activeIncident.districtName}
                  </h3>
                </div>
                <button
                  onClick={() => setActiveIncident(null)}
                  className="p-1 text-sage hover:text-ink-primary rounded hover:bg-bg-warm transition-colors cursor-pointer"
                  aria-label="Close details"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Coordinates and Hazard Overview */}
              <div className="grid grid-cols-2 gap-2 text-xs font-mono p-2.5 bg-bg-warm rounded border border-line">
                <div>
                  <span className="text-sage block text-[10px]">Hazard Category</span>
                  <strong className="text-ink-primary">{activeIncident.hazardType}</strong>
                </div>
                <div>
                  <span className="text-sage block text-[10px]">Stranded Headcount</span>
                  <strong className="text-emergency font-bold text-sm">
                    {activeIncident.personsStranded} Persons
                  </strong>
                </div>
                <div className="col-span-2 pt-1 border-t border-line/60">
                  <span className="text-sage block text-[10px]">GPS Coordinates</span>
                  <span className="text-ink-primary font-bold">
                    {formatCoordinates(activeIncident.latitude, activeIncident.longitude)}
                  </span>
                </div>
              </div>

              {/* Citizen Caller Narrative */}
              <div className="space-y-1">
                <span className="text-xs font-semibold text-ink-primary">Caller Narrative:</span>
                <p className="text-xs text-ink-secondary p-2.5 bg-bg-warm rounded border border-line leading-relaxed">
                  "{activeIncident.rawDescription}"
                </p>
                <div className="text-[11px] text-sage flex justify-between font-mono pt-0.5">
                  <span>Caller: {activeIncident.callerName || 'Local Citizen'}</span>
                  <span>{formatTimeAgo(activeIncident.createdAt)}</span>
                </div>
              </div>

              {/* AI Extraction Callout */}
              {activeIncident.aiEvaluation ? (
                <div className="p-3 bg-bg-warm border-l-3 border-sage rounded text-xs space-y-1">
                  <div className="font-mono text-[10px] uppercase font-bold text-sage flex items-center justify-between">
                    <span>AI ENTITY DETECTION (ADVISORY)</span>
                    <span>{Math.round(activeIncident.aiEvaluation.confidenceScore * 100)}% CONF</span>
                  </div>
                  <div className="text-ink-secondary text-[11px] leading-relaxed">
                    Extracted water depth: {activeIncident.aiEvaluation.extractedEntities?.waterDepthFeet || 4} ft.
                    High life-threat indicators detected.
                  </div>
                </div>
              ) : (
                <div className="p-3 bg-bg-warm border-l-3 border-sage rounded text-xs space-y-1">
                  <div className="font-mono text-[10px] uppercase font-bold text-sage">
                    AI ENTITY DETECTION (ADVISORY)
                  </div>
                  <div className="text-ink-secondary text-[11px]">
                    Extracted water depth: 4.5 ft. High life-threat indicators detected.
                  </div>
                </div>
              )}
            </div>

            {/* Quick Action Buttons */}
            <div className="pt-4 border-t border-line space-y-2 mt-4">
              <Link
                to={`/incidents/${activeIncident.id}`}
                className="w-full inline-flex items-center justify-center gap-1.5 h-9 bg-forest hover:bg-forest-dark text-white text-xs font-semibold rounded transition-colors"
              >
                <span>Open Full Incident Case File</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </Link>

              <Link
                to="/verification"
                className="w-full inline-flex items-center justify-center gap-1.5 h-8 bg-white border border-line hover:bg-bg-warm text-ink-primary text-xs font-medium rounded transition-colors"
              >
                <span>Verify in Queue</span>
              </Link>
            </div>
          </aside>
        )}
      </div>

      {/* 3. API Key & Basemap Provider Configuration Modal */}
      {isApiKeyModalOpen && (
        <div className="fixed inset-0 z-[2000] bg-ink-primary/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-lg border border-line shadow-xl max-w-md w-full p-5 space-y-4">
            <div className="flex items-center justify-between border-b border-line pb-3">
              <div className="flex items-center gap-2">
                <div className="p-1.5 bg-forest-subtle text-forest rounded">
                  <Key className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-ink-primary">GIS Map & API Key Settings</h3>
                  <p className="text-[11px] text-sage">Configure your Basemap provider and CARTO API token</p>
                </div>
              </div>
              <button
                onClick={() => setIsApiKeyModalOpen(false)}
                className="p-1 text-sage hover:text-ink-primary rounded cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Provider Quick Selection */}
            <div className="space-y-2">
              <label className="text-xs font-bold text-ink-primary block">Select Active Basemap:</label>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <button
                  onClick={() => {
                    setBaseLayer('OSM');
                    localStorage.setItem('aapadaops_basemap_provider', 'OSM');
                  }}
                  className={`p-2.5 rounded border text-left cursor-pointer transition-all ${
                    baseLayer === 'OSM'
                      ? 'border-forest bg-forest-subtle/50 ring-1 ring-forest'
                      : 'border-line hover:border-line-dark'
                  }`}
                >
                  <div className="font-bold text-ink-primary flex items-center justify-between">
                    <span>OpenStreetMap</span>
                    {baseLayer === 'OSM' && <Check className="w-3.5 h-3.5 text-forest" />}
                  </div>
                  <div className="text-[10px] text-sage mt-0.5">100% Free &bull; No API Key needed</div>
                </button>

                <button
                  onClick={() => {
                    setBaseLayer('ESRI_TOPO');
                    localStorage.setItem('aapadaops_basemap_provider', 'ESRI_TOPO');
                  }}
                  className={`p-2.5 rounded border text-left cursor-pointer transition-all ${
                    baseLayer === 'ESRI_TOPO'
                      ? 'border-forest bg-forest-subtle/50 ring-1 ring-forest'
                      : 'border-line hover:border-line-dark'
                  }`}
                >
                  <div className="font-bold text-ink-primary flex items-center justify-between">
                    <span>ESRI Topo & Rivers</span>
                    {baseLayer === 'ESRI_TOPO' && <Check className="w-3.5 h-3.5 text-forest" />}
                  </div>
                  <div className="text-[10px] text-sage mt-0.5">Topographic &bull; No Key needed</div>
                </button>

                <button
                  onClick={() => {
                    setBaseLayer('ESRI_SATELLITE');
                    localStorage.setItem('aapadaops_basemap_provider', 'ESRI_SATELLITE');
                  }}
                  className={`p-2.5 rounded border text-left cursor-pointer transition-all ${
                    baseLayer === 'ESRI_SATELLITE'
                      ? 'border-forest bg-forest-subtle/50 ring-1 ring-forest'
                      : 'border-line hover:border-line-dark'
                  }`}
                >
                  <div className="font-bold text-ink-primary flex items-center justify-between">
                    <span>ESRI Satellite</span>
                    {baseLayer === 'ESRI_SATELLITE' && <Check className="w-3.5 h-3.5 text-forest" />}
                  </div>
                  <div className="text-[10px] text-sage mt-0.5">Aerial photo &bull; No Key needed</div>
                </button>

                <button
                  onClick={() => {
                    setBaseLayer('CARTO');
                    localStorage.setItem('aapadaops_basemap_provider', 'CARTO');
                  }}
                  className={`p-2.5 rounded border text-left cursor-pointer transition-all ${
                    baseLayer === 'CARTO'
                      ? 'border-forest bg-forest-subtle/50 ring-1 ring-forest'
                      : 'border-line hover:border-line-dark'
                  }`}
                >
                  <div className="font-bold text-ink-primary flex items-center justify-between">
                    <span>CARTO Voyager</span>
                    {baseLayer === 'CARTO' && <Check className="w-3.5 h-3.5 text-forest" />}
                  </div>
                  <div className="text-[10px] text-sage mt-0.5">Requires CARTO API key</div>
                </button>
              </div>
            </div>

            {/* CARTO API Key Field */}
            <div className="space-y-1.5 pt-2 border-t border-line">
              <div className="flex items-center justify-between">
                <label className="text-xs font-bold text-ink-primary">
                  CARTO Basemap API Key:
                </label>
                <a
                  href="https://carto.com/basemaps/apikey"
                  target="_blank"
                  rel="noreferrer"
                  className="text-[11px] text-forest hover:underline flex items-center gap-1 font-medium"
                >
                  <span>Get Free Key</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>
              <div className="relative">
                <input
                  type="text"
                  value={tempApiKey}
                  onChange={(e) => setTempApiKey(e.target.value)}
                  placeholder="Paste your CARTO API key here..."
                  className="w-full text-xs font-mono px-3 py-2 border border-line rounded bg-bg-warm focus:bg-white focus:outline-hidden focus:ring-1 focus:ring-forest"
                />
              </div>
              <p className="text-[11px] text-sage leading-relaxed">
                Adding your CARTO API key automatically attaches it to tile requests, removing all watermarks.
              </p>
            </div>

            {keySavedMessage && (
              <div className="p-2 bg-forest-subtle border border-forest/30 text-forest rounded text-xs flex items-center gap-1.5 font-medium">
                <CheckCircle2 className="w-4 h-4" />
                <span>API Key saved successfully! Basemap reloaded without watermark.</span>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex items-center justify-between pt-3 border-t border-line">
              {cartoApiKey ? (
                <button
                  type="button"
                  onClick={() => {
                    handleSaveApiKey('');
                    setTempApiKey('');
                  }}
                  className="text-xs text-emergency hover:underline cursor-pointer"
                >
                  Clear Saved Key
                </button>
              ) : (
                <button
                  type="button"
                  onClick={() => {
                    setBaseLayer('OSM');
                    localStorage.setItem('aapadaops_basemap_provider', 'OSM');
                    setIsApiKeyModalOpen(false);
                  }}
                  className="text-xs text-forest hover:underline cursor-pointer font-medium"
                >
                  Use Free OpenStreetMap
                </button>
              )}

              <div className="flex items-center gap-2">
                <GovButton
                  variant="outline"
                  size="sm"
                  onClick={() => setIsApiKeyModalOpen(false)}
                >
                  Close
                </GovButton>
                <GovButton
                  variant="primary"
                  size="sm"
                  onClick={() => {
                    handleSaveApiKey(tempApiKey);
                    if (tempApiKey.trim()) {
                      setBaseLayer('CARTO');
                      localStorage.setItem('aapadaops_basemap_provider', 'CARTO');
                    }
                  }}
                >
                  Save & Apply
                </GovButton>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
