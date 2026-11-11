import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  ShieldAlert,
  Search,
  PhoneCall,
  Wind,
  Droplets,
  Building2,
  Navigation,
  ArrowRight,
} from 'lucide-react';
import { GovCard } from '../components/ui/GovCard';
import { GovBadge } from '../components/ui/GovBadge';
import { DEMO_SHELTERS, DEMO_ALERTS } from '../services/demoDataService';

export const LandingPage: React.FC = () => {
  const [shelterSearch, setShelterSearch] = useState('');
  const activeAlert = DEMO_ALERTS[0];

  const filteredShelters = DEMO_SHELTERS.filter(
    (s) =>
      s.name.toLowerCase().includes(shelterSearch.toLowerCase()) ||
      s.blockName.toLowerCase().includes(shelterSearch.toLowerCase()) ||
      s.code.toLowerCase().includes(shelterSearch.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* 1. Hero Emergency Action Section */}
      <div className="bg-white rounded border border-line p-6 sm:p-8 flex flex-col md:flex-row items-center justify-between gap-6 shadow-sm">
        <div className="max-w-xl">
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded bg-emergency-subtle border border-emergency/30 text-emergency text-xs font-mono font-bold mb-3 uppercase tracking-wider">
            <span className="w-2 h-2 rounded-full bg-emergency animate-ping" />
            Active Warning: Cyclonic Storm Over Bay of Bengal
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-ink-primary tracking-tight leading-tight">
            Odisha Disaster-Response & Crisis Coordination Portal
          </h1>
          <p className="text-sm text-ink-secondary mt-2 leading-relaxed">
            A centralized emergency gateway operated by OSDMA & District Emergency Operations Centers. Report life-threatening distress, find nearby reinforced cyclone shelters, and access official verification advisories.
          </p>

          <div className="mt-5 flex flex-wrap items-center gap-3">
            <Link
              to="/sos"
              className="inline-flex items-center gap-2 px-5 py-3 bg-emergency hover:bg-emergency-dark text-white font-bold text-sm rounded shadow-sm transition-colors cursor-pointer"
            >
              <ShieldAlert className="w-5 h-5" />
              <span>Report Emergency SOS (ଜରୁରୀ ସହାୟତା)</span>
            </Link>

            <a
              href="#shelters"
              className="inline-flex items-center gap-2 px-4 py-3 bg-bg-warm hover:bg-bg-subtle text-ink-primary border border-line text-sm font-semibold rounded transition-colors"
            >
              <Building2 className="w-4 h-4 text-forest" />
              <span>Find Safe Shelters</span>
            </a>
          </div>
        </div>

        {/* Live Weather / Alert Widget */}
        <div className="w-full md:w-80 bg-bg-warm p-4 rounded border border-line flex flex-col gap-3">
          <div className="flex items-center justify-between pb-2 border-b border-line">
            <span className="text-xs font-semibold text-ink-primary uppercase tracking-wider">
              Coastal Hazard Status
            </span>
            <GovBadge variant="emergency" size="sm">
              RED TIER
            </GovBadge>
          </div>

          <div className="space-y-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="text-sage flex items-center gap-1.5">
                <Wind className="w-4 h-4" /> Max Wind Speed:
              </span>
              <strong className="font-mono text-ink-primary">175 km/h</strong>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sage flex items-center gap-1.5">
                <Droplets className="w-4 h-4" /> 24h Rainfall Forecast:
              </span>
              <strong className="font-mono text-ink-primary">250 mm (Extremely Heavy)</strong>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sage flex items-center gap-1.5">
                <Navigation className="w-4 h-4" /> Threat Zones:
              </span>
              <span className="font-semibold text-ink-primary">Puri, Jagatsinghpur</span>
            </div>
          </div>

          <div className="text-[11px] text-sage pt-2 border-t border-line leading-normal">
            {activeAlert.instructionsEn.slice(0, 95)}...
          </div>
        </div>
      </div>

      {/* 2. Cyclone Shelters Directory */}
      <section id="shelters" className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h2 className="text-lg font-bold text-ink-primary">Multi-Purpose Cyclone & Flood Shelters</h2>
            <p className="text-xs text-sage">
              Showing real-time capacity and vacancy across 800+ government-engineered coastal shelters.
            </p>
          </div>

          <div className="relative w-full sm:w-72">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-sage" />
            <input
              type="text"
              placeholder="Search shelter name or block..."
              value={shelterSearch}
              onChange={(e) => setShelterSearch(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 text-xs bg-white border border-line rounded focus:outline-none focus:ring-1 focus:ring-forest text-ink-primary"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredShelters.map((shelter) => (
            <GovCard key={shelter.id} padding="sm" className="hover:border-forest/50 transition-colors">
              <div className="flex items-start justify-between gap-2 mb-2">
                <div>
                  <span className="font-mono text-[10px] text-sage block">{shelter.code}</span>
                  <h3 className="font-semibold text-sm text-ink-primary leading-snug">{shelter.name}</h3>
                  <span className="text-xs text-sage">{shelter.blockName}, {shelter.districtName}</span>
                </div>
                <GovBadge
                  variant={shelter.occupancyRate >= 0.9 ? 'emergency' : shelter.occupancyRate >= 0.7 ? 'amber' : 'forest'}
                  size="sm"
                >
                  {shelter.status}
                </GovBadge>
              </div>

              {/* Capacity Meter */}
              <div className="mt-2 space-y-1">
                <div className="flex justify-between text-xs font-mono">
                  <span className="text-sage">Capacity: {shelter.currentOccupancy} / {shelter.totalCapacity}</span>
                  <strong className="text-ink-primary">{Math.round(shelter.occupancyRate * 100)}%</strong>
                </div>
                <div className="w-full bg-bg-subtle h-2 rounded overflow-hidden">
                  <div
                    className={`h-full rounded ${
                      shelter.occupancyRate >= 0.9 ? 'bg-emergency' : shelter.occupancyRate >= 0.7 ? 'bg-amber' : 'bg-forest'
                    }`}
                    style={{ width: `${Math.min(100, shelter.occupancyRate * 100)}%` }}
                  />
                </div>
              </div>

              {/* Lifeline Indicators */}
              <div className="mt-3 pt-2.5 border-t border-line grid grid-cols-3 text-center text-[11px] font-mono">
                <div>
                  <span className="text-sage block">Drinking Water</span>
                  <strong className="text-ink-primary">{shelter.waterSupplyLitres} L</strong>
                </div>
                <div>
                  <span className="text-sage block">Dry Rations</span>
                  <strong className="text-ink-primary">{shelter.dryRationsDays} Days</strong>
                </div>
                <div>
                  <span className="text-sage block">DG Power</span>
                  <strong className="text-ink-primary">{shelter.dgFuelHours} Hrs</strong>
                </div>
              </div>

              <div className="mt-3 pt-2 border-t border-line flex items-center justify-between text-xs">
                <span className="text-sage text-[11px]">In-charge: {shelter.contactPerson}</span>
                <a
                  href={`tel:${shelter.contactPhone}`}
                  className="font-mono text-forest font-semibold hover:underline flex items-center gap-1"
                >
                  <PhoneCall className="w-3 h-3" /> Call
                </a>
              </div>
            </GovCard>
          ))}
        </div>
      </section>

      {/* 3. Official Helpline Directory */}
      <GovCard
        header={
          <div className="font-semibold text-sm text-ink-primary">
            Official Emergency Helpline & Control Room Directory
          </div>
        }
      >
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 text-xs">
          <div className="p-3 bg-bg-warm rounded border border-line">
            <span className="text-sage block text-[11px] font-medium">State EOC Toll Free</span>
            <strong className="text-xl font-mono text-ink-primary block mt-1">1070</strong>
            <span className="text-[11px] text-sage">Special Relief Commissioner, Rajiv Bhawan</span>
          </div>

          <div className="p-3 bg-bg-warm rounded border border-line">
            <span className="text-sage block text-[11px] font-medium">District EOC (Puri)</span>
            <strong className="text-xl font-mono text-ink-primary block mt-1">1077</strong>
            <span className="text-[11px] text-sage">Puri Collectorate Control Room</span>
          </div>

          <div className="p-3 bg-bg-warm rounded border border-line">
            <span className="text-sage block text-[11px] font-medium">Police, Fire & Ambulance</span>
            <strong className="text-xl font-mono text-ink-primary block mt-1">112</strong>
            <span className="text-[11px] text-sage">Unified Emergency Response Support (ERSS)</span>
          </div>

          <div className="p-3 bg-bg-warm rounded border border-line">
            <span className="text-sage block text-[11px] font-medium">ODRAF 03 Mundali Command</span>
            <strong className="text-xl font-mono text-ink-primary block mt-1">0671-2879100</strong>
            <span className="text-[11px] text-sage">Tactical Disaster Force Headquarters</span>
          </div>
        </div>
      </GovCard>
    </div>
  );
};

