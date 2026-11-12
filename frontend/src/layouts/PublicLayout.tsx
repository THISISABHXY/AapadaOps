import React from 'react';
import { Outlet, Link } from 'react-router-dom';
import { ShieldAlert, PhoneCall, LogIn, Building2, ExternalLink } from 'lucide-react';

export const PublicLayout: React.FC = () => {
  return (
    <div className="min-h-screen bg-bg-warm flex flex-col text-ink-primary font-sans antialiased">
      {/* Top Emergency Advisory Bar */}
      <div className="bg-emergency text-white text-xs px-4 py-2 font-medium flex items-center justify-between shadow-xs sticky top-0 z-40">
        <div className="max-w-6xl mx-auto w-full flex items-center justify-between gap-3">
          <div className="flex items-center gap-2 truncate">
            <span className="font-bold uppercase tracking-wider text-[10px] bg-white/20 px-1.5 py-0.5 rounded-full font-mono flex items-center gap-1.5 flex-shrink-0">
              <span className="w-1.5 h-1.5 rounded-full bg-white animate-pulse" />
              STATE DISASTER ADVISORY
            </span>
            <span className="truncate text-xs">
              Severe Cyclonic Storm Alert across coastal belt. Coastal residents urged to move to nearest Cyclone Shelter.
            </span>
          </div>
          <div className="hidden md:flex items-center gap-4 text-xs font-mono flex-shrink-0">
            <span>TOLL FREE: <strong>1070</strong> (State)</span>
            <span><strong>1077</strong> (Puri EOC)</span>
            <span><strong>112</strong> (ERSS)</span>
          </div>
        </div>
      </div>

      {/* Main Public Navigation Header */}
      <header className="bg-white border-b border-line shadow-2xs">
        <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3 group">
            <div className="w-9 h-9 rounded-md bg-forest flex items-center justify-center text-white font-extrabold text-sm shadow-xs group-hover:bg-forest-dark transition-colors">
              AO
            </div>
            <div>
              <div className="font-bold text-base text-ink-primary leading-tight flex items-center gap-1.5">
                <span>AapadaOps</span>
                <span className="text-xs font-normal text-sage">(ଆପଦାଅପ୍ସ)</span>
              </div>
              <div className="text-[10px] text-sage tracking-wider uppercase font-medium">
                Odisha State Disaster Management Authority
              </div>
            </div>
          </Link>

          <div className="flex items-center gap-2.5 sm:gap-3">
            <Link
              to="/#shelters"
              className="hidden sm:inline-flex items-center gap-1.5 text-xs font-medium text-ink-primary hover:text-forest px-3 py-1.5 rounded-md transition-colors"
            >
              <Building2 className="w-3.5 h-3.5 text-forest" />
              <span>Cyclone Shelters</span>
            </Link>

            <Link
              to="/sos"
              className="inline-flex items-center gap-1.5 text-xs font-bold bg-emergency text-white px-3.5 py-2 rounded-md shadow-xs hover:bg-emergency-dark active:scale-[0.985] transition-all cursor-pointer"
            >
              <ShieldAlert className="w-4 h-4" />
              <span>Report Emergency (SOS)</span>
            </Link>

            <Link
              to="/login"
              className="inline-flex items-center gap-1.5 text-xs font-semibold bg-bg-warm hover:bg-bg-subtle text-ink-primary border border-line px-3 py-2 rounded-md transition-all active:scale-[0.985]"
            >
              <LogIn className="w-3.5 h-3.5 text-sage" />
              <span>Staff Login</span>
            </Link>
          </div>
        </div>
      </header>

      {/* Public Main Body */}
      <main className="flex-1 max-w-6xl w-full mx-auto p-4 sm:p-6">
        <Outlet />
      </main>

      {/* Government Footer */}
      <footer className="bg-white border-t border-line text-xs text-sage py-8 px-4 mt-8">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="text-center md:text-left space-y-1">
            <div className="font-bold text-ink-primary text-sm flex items-center justify-center md:justify-start gap-2">
              <span>AapadaOps — State Emergency Management Platform</span>
              <span className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-forest-subtle text-forest border border-forest/20">
                OFFICIAL
              </span>
            </div>
            <p className="text-[11.5px] text-ink-secondary leading-relaxed">
              Special Relief Commissioner (SRC) & Odisha State Disaster Management Authority (OSDMA).
              <br className="hidden sm:inline" /> Rajiv Bhawan, Unit-5, Bhubaneswar - 751001, Odisha, India.
            </p>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-3 font-mono text-xs">
            <a
              href="tel:1070"
              className="px-3 py-1.5 rounded-md border border-line hover:border-forest hover:text-forest bg-bg-warm flex items-center gap-1.5 transition-colors"
            >
              <PhoneCall className="w-3.5 h-3.5 text-forest" />
              <span>1070 (State EOC)</span>
            </a>
            <a
              href="tel:1077"
              className="px-3 py-1.5 rounded-md border border-line hover:border-forest hover:text-forest bg-bg-warm flex items-center gap-1.5 transition-colors"
            >
              <PhoneCall className="w-3.5 h-3.5 text-forest" />
              <span>1077 (Puri EOC)</span>
            </a>
            <a
              href="tel:112"
              className="px-3 py-1.5 rounded-md border border-line hover:border-emergency hover:text-emergency bg-bg-warm flex items-center gap-1.5 transition-colors"
            >
              <PhoneCall className="w-3.5 h-3.5 text-emergency" />
              <span>112 (ERSS Emergency)</span>
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
};


