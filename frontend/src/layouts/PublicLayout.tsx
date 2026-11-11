import React from 'react';
import { Outlet, Link } from 'react-router-dom';
import { ShieldAlert, PhoneCall, LogIn } from 'lucide-react';

export const PublicLayout: React.FC = () => {
  return (
    <div className="min-h-screen bg-bg-warm flex flex-col text-ink-primary font-sans">
      {/* Top Emergency Advisory Bar */}
      <div className="bg-emergency text-white text-xs px-4 py-2 font-medium flex items-center justify-between shadow-xs">
        <div className="max-w-6xl mx-auto w-full flex items-center justify-between">
          <div className="flex items-center gap-2 truncate">
            <span className="font-bold uppercase tracking-wider text-[11px] bg-white/20 px-1.5 py-0.5 rounded">
              STATE DISASTER ADVISORY
            </span>
            <span className="truncate">
              Severe Cyclonic Storm Alert across coastal belt. Coastal residents urged to move to nearest Cyclone Shelter.
            </span>
          </div>
          <div className="hidden sm:flex items-center gap-4 text-xs font-mono">
            <span>TOLL FREE: <strong>1070</strong> (State)</span>
            <span><strong>1077</strong> (Puri District)</span>
          </div>
        </div>
      </div>

      {/* Main Public Navigation Header */}
      <header className="bg-white border-b border-line">
        <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded bg-forest flex items-center justify-center text-white font-bold text-sm">
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

          <div className="flex items-center gap-3">
            <Link
              to="/sos"
              className="inline-flex items-center gap-1.5 text-xs font-bold bg-emergency text-white px-3 py-1.5 rounded shadow-sm hover:bg-emergency-dark transition-colors"
            >
              <ShieldAlert className="w-4 h-4" />
              <span>Report Emergency (SOS)</span>
            </Link>

            <Link
              to="/login"
              className="inline-flex items-center gap-1.5 text-xs font-medium bg-bg-warm hover:bg-bg-subtle text-ink-primary border border-line px-3 py-1.5 rounded transition-colors"
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
      <footer className="bg-white border-t border-line text-xs text-sage py-6 px-4">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="text-center sm:text-left">
            <strong className="text-ink-primary">AapadaOps — Emergency Coordination Platform</strong>
            <p className="text-[11px] mt-0.5">
              Special Relief Commissioner (SRC) & Odisha State Disaster Management Authority (OSDMA), Rajiv Bhawan, Bhubaneswar.
            </p>
          </div>
          <div className="flex items-center gap-4 text-xs font-mono">
            <a href="tel:1070" className="hover:text-forest flex items-center gap-1">
              <PhoneCall className="w-3.5 h-3.5" /> 1070 (SEOC)
            </a>
            <a href="tel:112" className="hover:text-forest flex items-center gap-1">
              <PhoneCall className="w-3.5 h-3.5" /> 112 (ERSS)
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
};
