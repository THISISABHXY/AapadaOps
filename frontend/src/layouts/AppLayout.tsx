import React, { useState } from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Map as MapIcon,
  CheckSquare,
  Copy,
  Package,
  Radio,
  ListTodo,
  BarChart3,
  Users,
  Settings,
  Menu,
  X,
  ShieldAlert,
  Smartphone,
  LogOut,
  ChevronDown,
  ExternalLink,
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useDemoMode } from '../contexts/DemoModeContext';
import { UserRole } from '../types/user';

export const AppLayout: React.FC = () => {
  const { user, logout, switchDemoRole } = useAuth();
  const { isDemoMode, toggleDemoMode } = useDemoMode();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [roleDropdownOpen, setRoleDropdownOpen] = useState(false);

  const navigationItems = [
    { name: 'Command Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Incident GIS Map', path: '/map', icon: MapIcon },
    { name: 'Verification Queue', path: '/verification', icon: CheckSquare, badge: '14' },
    { name: 'Duplicate Review', path: '/duplicates', icon: Copy, badge: '3' },
    { name: 'Resource Management', path: '/resources', icon: Package },
    { name: 'Response Coordination', path: '/coordination', icon: Radio },
    { name: 'Team Task Board', path: '/tasks', icon: ListTodo, badge: '6' },
    { name: 'Shelters & Lifelines', path: '/shelters', icon: ShieldAlert },
    { name: 'Analytics & SitRep', path: '/analytics', icon: BarChart3 },
    { name: 'User Management', path: '/users', icon: Users },
    { name: 'System Settings', path: '/settings', icon: Settings },
  ];

  const currentTime = new Intl.DateTimeFormat('en-IN', {
    timeZone: 'Asia/Kolkata',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  }).format(new Date());

  return (
    <div className="min-h-screen bg-bg-warm flex flex-col text-ink-primary font-sans">
      {/* 1. Global Operational Status Bar */}
      <header className="bg-[#202B32] text-white text-xs border-b border-black/20 select-none z-40">
        <div className="max-w-[1920px] mx-auto px-3 sm:px-4 h-9 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 font-bold tracking-tight text-white">
              <span className="w-2.5 h-2.5 rounded-full bg-emergency animate-pulse" />
              <span>AapadaOps</span>
              <span className="font-normal text-sage text-[11px] hidden sm:inline">| OSDMA / SRC</span>
            </div>

            <div className="hidden md:flex items-center gap-2 pl-3 border-l border-white/15">
              <span className="bg-emergency/80 text-white font-mono px-1.5 py-0.5 rounded text-[10px] uppercase font-bold">
                STATE ALERT: RED
              </span>
              <span className="text-sage text-[11px]">Cyclonic Landfall Protocol Active</span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Live / Demo Mode Toggle */}
            <button
              onClick={toggleDemoMode}
              className={`flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-mono border transition-colors cursor-pointer ${
                isDemoMode
                  ? 'bg-amber-subtle text-amber-dark border-amber/60 font-semibold'
                  : 'bg-forest-subtle text-forest border-forest/50'
              }`}
              title="Click to toggle between Demo Data and Live Backend API"
            >
              <span>{isDemoMode ? '● DEMO DATA MODE' : '● LIVE API MODE'}</span>
            </button>

            {/* Current IST Time */}
            <div className="hidden lg:flex items-center gap-1 font-mono text-[11px] text-sage">
              <span>IST</span>
              <strong className="text-white">{currentTime}</strong>
            </div>

            {/* Quick Link to Mobile Field PWA */}
            <Link
              to="/field"
              className="flex items-center gap-1 text-[11px] text-sage hover:text-white px-2 py-0.5 rounded hover:bg-white/10"
              title="Open Mobile Field Worker Interface"
            >
              <Smartphone className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Field PWA</span>
            </Link>

            {/* Public SOS Link */}
            <Link
              to="/sos"
              className="flex items-center gap-1 text-[11px] text-amber hover:text-amber-subtle px-2 py-0.5 rounded hover:bg-white/10"
            >
              <ExternalLink className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Citizen SOS</span>
            </Link>

            {/* Role Switcher Dropdown for Prototype Testing */}
            <div className="relative">
              <button
                onClick={() => setRoleDropdownOpen((prev) => !prev)}
                className="flex items-center gap-1.5 text-[11px] text-white bg-white/10 hover:bg-white/20 px-2 py-1 rounded transition-colors"
              >
                <span className="font-semibold">{user?.role}</span>
                <ChevronDown className="w-3 h-3 text-sage" />
              </button>

              {roleDropdownOpen && (
                <div
                  className="absolute right-0 mt-1 w-56 bg-white text-ink-primary rounded border border-line shadow-md py-1 z-50 text-xs"
                  onClick={() => setRoleDropdownOpen(false)}
                >
                  <div className="px-3 py-1.5 border-b border-line text-[11px] text-sage font-medium">
                    Switch Test Persona:
                  </div>
                  {(
                    [
                      ['DISTRICT_ADMIN', 'District Collector (Puri)'],
                      ['VERIFICATION_OFFICER', 'Tahasildar (Krushnaprasad)'],
                      ['RESPONSE_COORDINATOR', 'BDO (Kakatpur)'],
                      ['FIELD_WORKER', 'ODRAF Unit 03 Commander'],
                      ['SUPER_ADMIN', 'OSDMA State Director'],
                      ['OBSERVER', 'NDMA Liaison Officer'],
                    ] as [UserRole, string][]
                  ).map(([role, label]) => (
                    <button
                      key={role}
                      onClick={() => switchDemoRole(role)}
                      className={`w-full text-left px-3 py-1.5 hover:bg-bg-warm flex items-center justify-between ${
                        user?.role === role ? 'font-bold text-forest bg-forest-subtle/50' : ''
                      }`}
                    >
                      <span>{label}</span>
                      <span className="font-mono text-[10px] text-sage">{role}</span>
                    </button>
                  ))}
                  <div className="border-t border-line mt-1 pt-1">
                    <button
                      onClick={logout}
                      className="w-full text-left px-3 py-1.5 text-emergency hover:bg-emergency-subtle flex items-center gap-1.5"
                    >
                      <LogOut className="w-3.5 h-3.5" />
                      <span>Sign Out</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* 2. Demo Mode Warning Banner if enabled */}
      {isDemoMode && (
        <div className="bg-[#FAF4E8] text-[#854D0E] border-b border-[#D7A65B]/40 text-xs px-4 py-1 flex items-center justify-between select-none">
          <div className="flex items-center gap-1.5">
            <span className="font-bold uppercase tracking-wider text-[10px] bg-[#D7A65B]/30 px-1 rounded">
              Prototype Environment
            </span>
            <span>
              Simulated cyclone landfall scenario active for Puri & coastal belt. All actions update local state.
            </span>
          </div>
          <button
            onClick={toggleDemoMode}
            className="text-[11px] underline font-medium hover:text-black cursor-pointer"
          >
            Switch to Live API
          </button>
        </div>
      )}

      {/* 3. Main Operational Container with Sidebar Navigation */}
      <div className="flex-1 flex max-w-[1920px] w-full mx-auto overflow-hidden">
        {/* Desktop Sidebar (Fixed 220px) */}
        <aside className="w-56 bg-white border-r border-line hidden lg:flex flex-col flex-shrink-0 select-none">
          <div className="p-3.5 border-b border-line bg-bg-warm/30">
            <div className="text-xs font-semibold text-ink-primary leading-tight truncate">
              {user?.fullName}
            </div>
            <div className="text-[11px] text-sage truncate mt-0.5 font-medium">
              {user?.department || 'District EOC, Puri'}
            </div>
          </div>

          <nav className="p-2 space-y-0.5 flex-1 overflow-y-auto">
            {navigationItems.map((item) => {
              const isActive = location.pathname === item.path;
              const Icon = item.icon;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center justify-between px-3 py-2 text-xs rounded font-medium transition-colors ${
                    isActive
                      ? 'bg-forest text-white font-semibold shadow-xs'
                      : 'text-ink-primary hover:bg-bg-warm hover:text-forest'
                  }`}
                >
                  <div className="flex items-center gap-2.5 truncate">
                    <Icon className={`w-4 h-4 flex-shrink-0 ${isActive ? 'text-white' : 'text-sage'}`} />
                    <span className="truncate">{item.name}</span>
                  </div>
                  {item.badge && (
                    <span
                      className={`font-mono text-[10px] px-1.5 py-0.2 rounded font-semibold ${
                        isActive
                          ? 'bg-white/20 text-white'
                          : 'bg-bg-subtle text-ink-secondary border border-line'
                      }`}
                    >
                      {item.badge}
                    </span>
                  )}
                </Link>
              );
            })}
          </nav>

          <div className="p-3 border-t border-line text-[11px] text-sage bg-bg-warm/20 flex items-center justify-between">
            <span>v1.0.0 (OSDMA)</span>
            <Link to="/sos" className="text-forest hover:underline font-semibold">
              Public Portal
            </Link>
          </div>
        </aside>

        {/* Mobile Navigation Header */}
        <div className="lg:hidden w-full bg-white border-b border-line px-4 py-2.5 flex items-center justify-between z-30">
          <div className="font-semibold text-sm text-ink-primary flex items-center gap-2">
            <button
              onClick={() => setMobileMenuOpen((prev) => !prev)}
              className="p-1 rounded text-ink-primary hover:bg-bg-warm"
              aria-label="Toggle navigation menu"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
            <span>AapadaOps Command</span>
          </div>
          <span className="text-xs font-mono bg-bg-subtle px-2 py-0.5 rounded border border-line">
            {user?.role}
          </span>
        </div>

        {/* Mobile Navigation Drawer */}
        {mobileMenuOpen && (
          <div
            className="lg:hidden fixed inset-0 z-40 bg-black/40"
            onClick={() => setMobileMenuOpen(false)}
          >
            <div
              className="w-64 bg-white h-full border-r border-line p-3 flex flex-col shadow-lg"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between pb-3 border-b border-line mb-2">
                <span className="font-bold text-sm text-ink-primary">Navigation</span>
                <button onClick={() => setMobileMenuOpen(false)}>
                  <X className="w-5 h-5 text-sage" />
                </button>
              </div>
              <nav className="space-y-1 flex-1 overflow-y-auto">
                {navigationItems.map((item) => {
                  const isActive = location.pathname === item.path;
                  const Icon = item.icon;
                  return (
                    <Link
                      key={item.path}
                      to={item.path}
                      onClick={() => setMobileMenuOpen(false)}
                      className={`flex items-center justify-between px-3 py-2 text-xs rounded font-medium ${
                        isActive
                          ? 'bg-forest text-white font-semibold'
                          : 'text-ink-primary hover:bg-bg-warm'
                      }`}
                    >
                      <div className="flex items-center gap-2.5">
                        <Icon className="w-4 h-4" />
                        <span>{item.name}</span>
                      </div>
                      {item.badge && (
                        <span className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-bg-subtle text-ink-secondary border border-line">
                          {item.badge}
                        </span>
                      )}
                    </Link>
                  );
                })}
              </nav>
            </div>
          </div>
        )}

        {/* 4. Active Main Content Canvas */}
        <main className="flex-1 overflow-y-auto bg-bg-warm p-3 sm:p-5">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

