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
  CheckCircle2,
  Users,
  Compass,
  AlertCircle,
  FileCheck2,
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
    <div className="space-y-8 pb-8">
      {/* 1. Hero Emergency Action Section */}
      <div className="bg-white rounded-xl border border-line p-6 sm:p-9 shadow-xs flex flex-col lg:flex-row items-center justify-between gap-8 transition-all">
        <div className="max-w-2xl space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emergency-subtle border border-emergency/30 text-emergency text-xs font-mono font-bold uppercase tracking-wider">
            <span className="w-2 h-2 rounded-full bg-emergency animate-ping" />
            Active Warning: Cyclonic Storm Over Bay of Bengal (Landfall 14h)
          </div>
          
          <h1 className="text-2xl sm:text-4xl font-extrabold text-ink-primary tracking-tight leading-tight">
            Odisha Disaster-Response & Crisis Coordination Portal
          </h1>
          
          <p className="text-sm sm:text-base text-ink-secondary leading-relaxed font-normal">
            A unified emergency operations command maintained by OSDMA, Special Relief Commissioner, and District Emergency Operations Centers. Report acute life-threatening distress, find verified cyclone shelters, and follow real-time IMD landfall alerts.
          </p>

          <div className="pt-2 flex flex-wrap items-center gap-3">
            <Link
              to="/sos"
              className="inline-flex items-center gap-2.5 px-6 py-3.5 bg-emergency hover:bg-emergency-dark active:scale-[0.985] text-white font-bold text-sm sm:text-base rounded-lg shadow-sm hover:shadow transition-all cursor-pointer"
            >
              <ShieldAlert className="w-5 h-5" />
              <span>Report Emergency SOS (ଜରୁରୀ ସହାୟତା)</span>
            </Link>

            <a
              href="#shelters"
              className="inline-flex items-center gap-2 px-5 py-3.5 bg-bg-warm hover:bg-bg-subtle active:scale-[0.985] text-ink-primary border border-line text-sm font-semibold rounded-lg transition-all"
            >
              <Building2 className="w-4 h-4 text-forest" />
              <span>Find Safe Cyclone Shelters</span>
            </a>
          </div>
        </div>

        {/* Live Weather / Alert Widget */}
        <div className="w-full lg:w-88 bg-bg-warm/70 p-5 rounded-xl border border-line flex flex-col gap-3.5 shadow-2xs">
          <div className="flex items-center justify-between pb-2.5 border-b border-line">
            <div className="flex items-center gap-2">
              <Compass className="w-4 h-4 text-forest" />
              <span className="text-xs font-bold text-ink-primary uppercase tracking-wider font-mono">
                Coastal Threat Telemetry
              </span>
            </div>
            <GovBadge variant="emergency" size="sm" dot pulse>
              RED TIER
            </GovBadge>
          </div>

          <div className="space-y-2.5 text-xs">
            <div className="flex items-center justify-between">
              <span className="text-sage flex items-center gap-2 font-medium">
                <Wind className="w-4 h-4 text-emergency" /> Max Gust Wind:
              </span>
              <strong className="font-mono text-ink-primary font-bold text-sm">175 km/h</strong>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sage flex items-center gap-2 font-medium">
                <Droplets className="w-4 h-4 text-forest" /> 24h Rain Forecast:
              </span>
              <strong className="font-mono text-ink-primary font-bold">250 mm (Extremely Heavy)</strong>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sage flex items-center gap-2 font-medium">
                <Navigation className="w-4 h-4 text-amber-dark" /> Threat Coastlines:
              </span>
              <span className="font-bold text-ink-primary">Puri, Kendrapara, Jagatsinghpur</span>
            </div>
          </div>

          <div className="text-[11.5px] text-ink-secondary pt-2.5 border-t border-line leading-relaxed">
            {activeAlert.instructionsEn.slice(0, 110)}...
          </div>

          <div className="pt-1 flex items-center justify-between text-[11px] font-mono text-sage">
            <span>Source: IMD Bulletin #14</span>
            <span className="text-forest font-semibold">Verified Ground Station</span>
          </div>
        </div>
      </div>

      {/* 2. Real-Time Crisis Statistics Ticker */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4">
        <div className="p-4 bg-white rounded-lg border border-line shadow-2xs flex flex-col">
          <span className="text-xs font-mono text-sage uppercase tracking-wider">Active Rescues</span>
          <div className="mt-1 flex items-baseline gap-2">
            <span className="text-2xl sm:text-3xl font-extrabold font-mono text-emergency">14</span>
            <span className="text-[11px] font-medium text-sage">In Progress</span>
          </div>
          <span className="text-[11px] text-ink-secondary mt-1">ODRAF 03 deployed at Pattamundai</span>
        </div>

        <div className="p-4 bg-white rounded-lg border border-line shadow-2xs flex flex-col">
          <span className="text-xs font-mono text-sage uppercase tracking-wider">Evacuees Sheltered</span>
          <div className="mt-1 flex items-baseline gap-2">
            <span className="text-2xl sm:text-3xl font-extrabold font-mono text-forest">1,480+</span>
            <span className="text-[11px] font-medium text-forest font-semibold">Safe</span>
          </div>
          <span className="text-[11px] text-ink-secondary mt-1">Food & medical kits active</span>
        </div>

        <div className="p-4 bg-white rounded-lg border border-line shadow-2xs flex flex-col">
          <span className="text-xs font-mono text-sage uppercase tracking-wider">Functional Shelters</span>
          <div className="mt-1 flex items-baseline gap-2">
            <span className="text-2xl sm:text-3xl font-extrabold font-mono text-ink-primary">800+</span>
            <span className="text-[11px] font-medium text-sage">Coast-Wide</span>
          </div>
          <span className="text-[11px] text-ink-secondary mt-1">Multi-purpose reinforced structures</span>
        </div>

        <div className="p-4 bg-white rounded-lg border border-line shadow-2xs flex flex-col">
          <span className="text-xs font-mono text-sage uppercase tracking-wider">Tactical Force Units</span>
          <div className="mt-1 flex items-baseline gap-2">
            <span className="text-2xl sm:text-3xl font-extrabold font-mono text-ink-primary">12 Units</span>
            <span className="text-[11px] font-medium text-amber-dark font-semibold">Stationed</span>
          </div>
          <span className="text-[11px] text-ink-secondary mt-1">Boats, tree-cutters & gensets ready</span>
        </div>
      </div>

      {/* 3. Three Primary Action Portals */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Link
          to="/sos"
          className="group p-5 bg-white hover:bg-bg-warm/50 border border-line hover:border-emergency/50 rounded-xl shadow-2xs transition-all flex flex-col justify-between"
        >
          <div>
            <div className="w-10 h-10 rounded-lg bg-emergency/10 border border-emergency/20 text-emergency flex items-center justify-center mb-3 group-hover:scale-105 transition-transform">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <div className="flex items-center gap-2 mb-1">
              <h3 className="font-bold text-base text-ink-primary group-hover:text-emergency transition-colors">
                Citizen Emergency SOS
              </h3>
              <GovBadge variant="emergency" size="sm">Urgent</GovBadge>
            </div>
            <p className="text-xs text-ink-secondary leading-relaxed">
              Submit location coordinates, stranded headcount, flood height, and immediate medical needs with bilingual Odia/English guidance.
            </p>
          </div>
          <div className="mt-4 pt-3 border-t border-line flex items-center text-xs font-bold text-emergency gap-1 group-hover:translate-x-1 transition-transform">
            <span>Report Situation Now</span>
            <ArrowRight className="w-4 h-4" />
          </div>
        </Link>

        <a
          href="#shelters"
          className="group p-5 bg-white hover:bg-bg-warm/50 border border-line hover:border-forest/50 rounded-xl shadow-2xs transition-all flex flex-col justify-between"
        >
          <div>
            <div className="w-10 h-10 rounded-lg bg-forest/10 border border-forest/20 text-forest flex items-center justify-center mb-3 group-hover:scale-105 transition-transform">
              <Building2 className="w-5 h-5" />
            </div>
            <div className="flex items-center gap-2 mb-1">
              <h3 className="font-bold text-base text-ink-primary group-hover:text-forest transition-colors">
                Find Cyclone Shelter
              </h3>
              <GovBadge variant="forest" size="sm">Verified</GovBadge>
            </div>
            <p className="text-xs text-ink-secondary leading-relaxed">
              Locate nearby cyclone and flood shelters equipped with drinking water, dry rations, and generator power across all blocks.
            </p>
          </div>
          <div className="mt-4 pt-3 border-t border-line flex items-center text-xs font-bold text-forest gap-1 group-hover:translate-x-1 transition-transform">
            <span>Inspect Shelter Directory</span>
            <ArrowRight className="w-4 h-4" />
          </div>
        </a>

        <Link
          to="/login"
          className="group p-5 bg-white hover:bg-bg-warm/50 border border-line hover:border-ink-primary/30 rounded-xl shadow-2xs transition-all flex flex-col justify-between"
        >
          <div>
            <div className="w-10 h-10 rounded-lg bg-sage/15 border border-sage/30 text-ink-primary flex items-center justify-center mb-3 group-hover:scale-105 transition-transform">
              <FileCheck2 className="w-5 h-5" />
            </div>
            <div className="flex items-center gap-2 mb-1">
              <h3 className="font-bold text-base text-ink-primary">
                Officer Command Login
              </h3>
              <GovBadge variant="sage" size="sm">Admin</GovBadge>
            </div>
            <p className="text-xs text-ink-secondary leading-relaxed">
              Authorized access for District Collectors, Tahasildars, BDOs, and ODRAF response coordinators to manage the live tactical response.
            </p>
          </div>
          <div className="mt-4 pt-3 border-t border-line flex items-center text-xs font-bold text-ink-primary gap-1 group-hover:translate-x-1 transition-transform">
            <span>Access Command Cockpit</span>
            <ArrowRight className="w-4 h-4" />
          </div>
        </Link>
      </div>

      {/* 4. Cyclone Shelters Directory */}
      <section id="shelters" className="space-y-4 pt-2">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <div className="flex items-center gap-2">
              <Building2 className="w-5 h-5 text-forest" />
              <h2 className="text-xl font-bold text-ink-primary tracking-tight">
                Multi-Purpose Cyclone & Flood Shelters
              </h2>
            </div>
            <p className="text-xs text-sage mt-0.5">
              Live capacity, drinking water reserves, and emergency contact details for coastal block shelters.
            </p>
          </div>

          <div className="relative w-full sm:w-80">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-sage" />
            <input
              type="text"
              placeholder="Search shelter by name or block..."
              value={shelterSearch}
              onChange={(e) => setShelterSearch(e.target.value)}
              className="w-full pl-9 pr-3 py-2 text-xs bg-white border border-line rounded-lg focus:outline-none focus:ring-1 focus:ring-forest text-ink-primary shadow-2xs"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredShelters.map((shelter) => (
            <GovCard
              key={shelter.id}
              padding="sm"
              hoverEffect
              className="border-line hover:border-forest/50 transition-all"
            >
              <div className="flex items-start justify-between gap-2 mb-2">
                <div>
                  <span className="font-mono text-[10px] text-sage block tracking-wider uppercase font-semibold">
                    {shelter.code}
                  </span>
                  <h3 className="font-bold text-sm text-ink-primary leading-snug">{shelter.name}</h3>
                  <span className="text-xs text-sage font-medium">{shelter.blockName}, {shelter.districtName}</span>
                </div>
                <GovBadge
                  variant={shelter.occupancyRate >= 0.9 ? 'emergency' : shelter.occupancyRate >= 0.7 ? 'amber' : 'forest'}
                  size="sm"
                  dot
                >
                  {shelter.status}
                </GovBadge>
              </div>

              {/* Capacity Progress Bar */}
              <div className="mt-2.5 space-y-1">
                <div className="flex justify-between text-xs font-mono">
                  <span className="text-sage text-[11px]">
                    Occupancy: {shelter.currentOccupancy} / {shelter.totalCapacity}
                  </span>
                  <strong className="text-ink-primary font-bold">
                    {Math.round(shelter.occupancyRate * 100)}%
                  </strong>
                </div>
                <div className="w-full bg-bg-subtle h-2 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-300 ${
                      shelter.occupancyRate >= 0.9
                        ? 'bg-emergency'
                        : shelter.occupancyRate >= 0.7
                        ? 'bg-amber'
                        : 'bg-forest'
                    }`}
                    style={{ width: `${Math.min(100, shelter.occupancyRate * 100)}%` }}
                  />
                </div>
              </div>

              {/* Lifeline Indicators */}
              <div className="mt-3 pt-2.5 border-t border-line grid grid-cols-3 text-center text-[11px] font-mono bg-bg-warm/40 p-2 rounded-md">
                <div>
                  <span className="text-sage block text-[10px]">Water Supply</span>
                  <strong className="text-ink-primary font-semibold">{shelter.waterSupplyLitres} L</strong>
                </div>
                <div>
                  <span className="text-sage block text-[10px]">Dry Rations</span>
                  <strong className="text-ink-primary font-semibold">{shelter.dryRationsDays} Days</strong>
                </div>
                <div>
                  <span className="text-sage block text-[10px]">DG Generator</span>
                  <strong className="text-ink-primary font-semibold">{shelter.dgFuelHours} Hrs</strong>
                </div>
              </div>

              <div className="mt-3 pt-2 border-t border-line flex items-center justify-between text-xs">
                <span className="text-sage text-[11px] truncate">In-charge: {shelter.contactPerson}</span>
                <a
                  href={`tel:${shelter.contactPhone}`}
                  className="font-mono text-forest font-bold hover:underline flex items-center gap-1.5 flex-shrink-0 ml-2"
                >
                  <PhoneCall className="w-3.5 h-3.5" />
                  <span>Call Shelter</span>
                </a>
              </div>
            </GovCard>
          ))}
        </div>
      </section>

      {/* 5. Official Helpline Directory */}
      <GovCard
        header={
          <div className="flex items-center gap-2">
            <PhoneCall className="w-4 h-4 text-forest" />
            <span className="font-bold text-sm text-ink-primary">
              Official Emergency Helpline & State Control Room Directory
            </span>
          </div>
        }
      >
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
          <div className="p-4 bg-bg-warm/60 rounded-lg border border-line">
            <span className="text-sage block text-[11px] font-mono uppercase tracking-wider">
              State EOC Toll Free
            </span>
            <strong className="text-2xl font-mono text-ink-primary block mt-1 font-extrabold">1070</strong>
            <span className="text-[11px] text-sage block mt-0.5">
              Special Relief Commissioner, Rajiv Bhawan, Bhubaneswar
            </span>
            <a href="tel:1070" className="inline-block mt-2 text-xs font-bold text-forest hover:underline">
              Dial Toll-Free &rarr;
            </a>
          </div>

          <div className="p-4 bg-bg-warm/60 rounded-lg border border-line">
            <span className="text-sage block text-[11px] font-mono uppercase tracking-wider">
              District EOC (Puri)
            </span>
            <strong className="text-2xl font-mono text-ink-primary block mt-1 font-extrabold">1077</strong>
            <span className="text-[11px] text-sage block mt-0.5">
              Puri Collectorate 24/7 Crisis Control Center
            </span>
            <a href="tel:1077" className="inline-block mt-2 text-xs font-bold text-forest hover:underline">
              Dial District EOC &rarr;
            </a>
          </div>

          <div className="p-4 bg-bg-warm/60 rounded-lg border border-line">
            <span className="text-sage block text-[11px] font-mono uppercase tracking-wider">
              Emergency Response (ERSS)
            </span>
            <strong className="text-2xl font-mono text-ink-primary block mt-1 font-extrabold">112</strong>
            <span className="text-[11px] text-sage block mt-0.5">
              Unified Police, Fire & Medical Ambulance Support
            </span>
            <a href="tel:112" className="inline-block mt-2 text-xs font-bold text-emergency hover:underline">
              Dial ERSS &rarr;
            </a>
          </div>

          <div className="p-4 bg-bg-warm/60 rounded-lg border border-line">
            <span className="text-sage block text-[11px] font-mono uppercase tracking-wider">
              ODRAF Mundali Command
            </span>
            <strong className="text-xl font-mono text-ink-primary block mt-1 font-extrabold">
              0671-2879100
            </strong>
            <span className="text-[11px] text-sage block mt-0.5">
              Tactical Disaster Relief Force Headquarters
            </span>
            <a href="tel:06712879100" className="inline-block mt-2 text-xs font-bold text-forest hover:underline">
              Dial HQ &rarr;
            </a>
          </div>
        </div>
      </GovCard>
    </div>
  );
};
