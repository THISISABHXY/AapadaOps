import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import {
  ListTodo,
  Building2,
  Camera,
  Navigation,
  CheckCircle2,
  PhoneCall,
  Wifi,
  WifiOff,
  ArrowLeft,
  AlertTriangle,
} from 'lucide-react';
import { GovCard } from '../components/ui/GovCard';
import { GovBadge } from '../components/ui/GovBadge';
import { GovButton } from '../components/ui/GovButton';
import { useToast } from '../contexts/ToastContext';
import { taskService } from '../services/taskService';
import { evidenceService } from '../services/evidenceService';
import { DEMO_TASKS, DEMO_SHELTERS } from '../services/demoDataService';
import { Task, TaskStatus } from '../types/task';
import { formatCoordinates } from '../utilities/formatters';

export const MobileFieldPage: React.FC = () => {
  const { showToast } = useToast();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<'TASKS' | 'SHELTER' | 'REPORT'>('TASKS');
  const [isOnline, setIsOnline] = useState<boolean>(true);
  const [evidenceModalOpen, setEvidenceModalOpen] = useState(false);
  const [activeTask, setActiveTask] = useState<Task | null>(null);

  const { data: tasks = DEMO_TASKS.slice(0, 3) } = useQuery({
    queryKey: ['field-tasks'],
    queryFn: () => taskService.getTasks(),
    refetchInterval: 10000,
  });

  const handleAdvanceTask = async (taskId: string, currentStatus: TaskStatus) => {
    let next: TaskStatus = 'EN_ROUTE';
    if (currentStatus === 'ASSIGNED') next = 'EN_ROUTE';
    else if (currentStatus === 'EN_ROUTE') next = 'ON_SCENE';
    else if (currentStatus === 'ON_SCENE') next = 'RESOLVED';

    try {
      await taskService.updateTaskStatus(taskId, next, `Updated from field PWA to ${next}`);
      queryClient.invalidateQueries({ queryKey: ['field-tasks'] });
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      showToast('success', 'Field Status Updated', `Mission updated to ${next}. Synced with State EOC.`);
    } catch {
      showToast('info', 'Offline Mode', `Saved locally. Will sync when network restores.`);
    }
  };

  return (
    <div className="max-w-md mx-auto min-h-screen bg-bg-warm flex flex-col font-sans pb-16">
      {/* 1. Mobile PWA Header */}
      <div className="bg-[#202B32] text-white p-3 flex items-center justify-between sticky top-0 z-30 select-none">
        <div className="flex items-center gap-2">
          <Link to="/dashboard" className="p-1 rounded text-sage hover:text-white">
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <div className="font-bold text-xs leading-tight">ODRAF Mobile Responder PWA</div>
            <div className="text-[10px] text-sage font-mono">Unit 03 (Puri Police Staging)</div>
          </div>
        </div>

        {/* Offline / Online Toggle Simulation */}
        <button
          onClick={() => {
            setIsOnline((prev) => !prev);
            showToast('info', isOnline ? 'Offline Mode Active' : 'Online Reconnected', 'Field actions cached locally');
          }}
          className={`flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
            isOnline ? 'bg-forest text-white' : 'bg-amber text-black'
          }`}
        >
          {isOnline ? <Wifi className="w-3 h-3" /> : <WifiOff className="w-3 h-3" />}
          <span>{isOnline ? 'ONLINE' : 'OFFLINE (QUEUED)'}</span>
        </button>
      </div>

      {/* Offline Alert Strip if disconnected */}
      {!isOnline && (
        <div className="bg-amber-subtle text-amber-dark border-b border-amber/40 text-[11px] p-2 flex items-center justify-between font-mono">
          <span>● Cellular tower down. Actions queued in local storage.</span>
          <span className="font-bold">2 Queued</span>
        </div>
      )}

      {/* Main Tab Content */}
      <div className="p-3 space-y-3 flex-1 overflow-y-auto">
        {/* TAB 1: Assigned Rescue Missions */}
        {activeTab === 'TASKS' && (
          <div className="space-y-3">
            <div className="flex items-center justify-between text-xs px-1">
              <span className="font-bold text-ink-primary uppercase tracking-wider text-[11px]">
                Assigned Unit Missions ({tasks.length})
              </span>
              <span className="font-mono text-[10px] text-sage">SLA Priority Sorted</span>
            </div>

            {tasks.map((task) => (
              <GovCard key={task.id} padding="sm" className="space-y-2 border-line">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-bold text-forest">{task.taskCode}</span>
                  <GovBadge
                    variant={task.priority === 'CRITICAL' ? 'emergency' : 'amber'}
                    size="sm"
                  >
                    {task.status}
                  </GovBadge>
                </div>

                <h3 className="text-xs font-bold text-ink-primary leading-tight">{task.title}</h3>

                <div className="p-2 bg-bg-warm rounded text-xs font-mono space-y-0.5">
                  <div className="flex justify-between">
                    <span className="text-sage">Target:</span>
                    <strong className="text-ink-primary">{task.targetVillage}</strong>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sage">GPS:</span>
                    <span className="text-ink-primary">{formatCoordinates(task.targetLatitude, task.targetLongitude)}</span>
                  </div>
                </div>

                {/* Mobile Large Touch Action Buttons */}
                <div className="pt-2 flex items-center gap-2">
                  <a
                    href={`https://www.google.com/maps/dir/?api=1&destination=${task.targetLatitude},${task.targetLongitude}`}
                    target="_blank"
                    rel="noreferrer"
                    className="flex-1 inline-flex items-center justify-center gap-1.5 h-10 bg-white border border-line rounded text-xs font-bold text-ink-primary hover:bg-bg-warm"
                  >
                    <Navigation className="w-4 h-4 text-forest" />
                    <span>Navigate GPS</span>
                  </a>

                  {task.status !== 'RESOLVED' ? (
                    <GovButton
                      variant="primary"
                      size="md"
                      className="flex-1 h-10 text-xs font-bold"
                      onClick={() => handleAdvanceTask(task.id, task.status)}
                    >
                      {task.status === 'ASSIGNED' && 'Mark En Route'}
                      {task.status === 'EN_ROUTE' && 'Mark On Scene'}
                      {task.status === 'ON_SCENE' && 'Complete Rescue ✓'}
                    </GovButton>
                  ) : (
                    <div className="flex-1 h-10 flex items-center justify-center gap-1 font-mono text-xs font-bold text-forest bg-forest-subtle rounded">
                      <CheckCircle2 className="w-4 h-4" /> Rescued
                    </div>
                  )}
                </div>
              </GovCard>
            ))}
          </div>
        )}

        {/* TAB 2: Shelter Quick Check-in */}
        {activeTab === 'SHELTER' && (
          <div className="space-y-3">
            <span className="font-bold text-ink-primary uppercase tracking-wider text-[11px] block px-1">
              Field Shelter Headcount & Lifeline Audit
            </span>

            {DEMO_SHELTERS.slice(0, 3).map((shelter) => (
              <GovCard key={shelter.id} padding="sm" className="space-y-2">
                <div className="flex justify-between items-start">
                  <div>
                    <span className="font-mono text-[10px] text-sage">{shelter.code}</span>
                    <h4 className="text-xs font-bold text-ink-primary">{shelter.name}</h4>
                    <span className="text-[11px] text-sage">{shelter.blockName} Block</span>
                  </div>
                  <GovBadge variant="forest" size="sm">
                    {Math.round(shelter.occupancyRate * 100)}% Cap
                  </GovBadge>
                </div>

                <div className="p-2 bg-bg-warm rounded text-xs font-mono grid grid-cols-3 text-center">
                  <div>
                    <span className="text-sage block text-[10px]">Headcount</span>
                    <strong className="text-ink-primary">{shelter.currentOccupancy}</strong>
                  </div>
                  <div>
                    <span className="text-sage block text-[10px]">Water (L)</span>
                    <strong className="text-forest">{shelter.waterSupplyLitres}</strong>
                  </div>
                  <div>
                    <span className="text-sage block text-[10px]">Rations</span>
                    <strong className="text-ink-primary">{shelter.dryRationsDays}d</strong>
                  </div>
                </div>

                <GovButton
                  variant="secondary"
                  size="sm"
                  className="w-full text-xs font-semibold h-9"
                  onClick={() => showToast('success', 'Headcount Confirmed', `Logged ${shelter.currentOccupancy} evacuees at ${shelter.name}`)}
                >
                  Confirm Shelter Lifelines Safe ✓
                </GovButton>
              </GovCard>
            ))}
          </div>
        )}

        {/* TAB 3: Fast Hazard Log */}
        {activeTab === 'REPORT' && (
          <div className="space-y-3">
            <span className="font-bold text-ink-primary uppercase tracking-wider text-[11px] block px-1">
              Frontline Tactical Hazard Report
            </span>

            <GovCard padding="sm" className="space-y-3">
              <div>
                <label className="text-xs font-semibold text-ink-primary block mb-1">
                  Hazard Observation
                </label>
                <select className="w-full text-xs h-9 px-2.5 bg-white border border-line rounded">
                  <option>Road Blocked by Fallen Tree (NH/SH)</option>
                  <option>Embankment Breach / High Inundation</option>
                  <option>High Voltage Wire Snapped</option>
                  <option>Bridge Submerged / Impassable</option>
                </select>
              </div>

              <div>
                <label className="text-xs font-semibold text-ink-primary block mb-1">
                  Field Coordinates
                </label>
                <input
                  type="text"
                  readOnly
                  value="19.8135° N, 85.8312° E (Puri Sector)"
                  className="w-full text-xs h-9 px-2.5 bg-bg-warm border border-line rounded font-mono text-ink-primary"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-ink-primary block mb-1">
                  Photo Evidence (Geotagged)
                </label>
                <button
                  type="button"
                  onClick={() => showToast('info', 'Camera Activated', 'Photo attached with GPS EXIF')}
                  className="w-full h-12 border border-dashed border-line rounded flex items-center justify-center gap-2 text-xs text-sage hover:bg-bg-warm"
                >
                  <Camera className="w-4 h-4 text-forest" />
                  <span>Tap to Capture Camera Photo</span>
                </button>
              </div>

              <GovButton
                variant="primary"
                size="md"
                className="w-full font-bold h-10"
                onClick={() => showToast('success', 'Field Report Transmitted', 'Logged in DEOC tactical situation map')}
              >
                Transmit Field Hazard to DEOC
              </GovButton>
            </GovCard>
          </div>
        )}
      </div>

      {/* 3. Single-Thumb Mobile Bottom Navigation Bar */}
      <nav className="fixed bottom-0 left-0 right-0 max-w-md mx-auto bg-white border-t border-line h-14 flex items-center justify-around z-30 select-none">
        <button
          onClick={() => setActiveTab('TASKS')}
          className={`flex flex-col items-center justify-center flex-1 h-full cursor-pointer ${
            activeTab === 'TASKS' ? 'text-forest font-bold' : 'text-sage'
          }`}
        >
          <ListTodo className="w-5 h-5 mb-0.5" />
          <span className="text-[10px]">My Tasks</span>
        </button>

        <button
          onClick={() => setActiveTab('SHELTER')}
          className={`flex flex-col items-center justify-center flex-1 h-full cursor-pointer ${
            activeTab === 'SHELTER' ? 'text-forest font-bold' : 'text-sage'
          }`}
        >
          <Building2 className="w-5 h-5 mb-0.5" />
          <span className="text-[10px]">Shelters</span>
        </button>

        <button
          onClick={() => setActiveTab('REPORT')}
          className={`flex flex-col items-center justify-center flex-1 h-full cursor-pointer ${
            activeTab === 'REPORT' ? 'text-forest font-bold' : 'text-sage'
          }`}
        >
          <Camera className="w-5 h-5 mb-0.5" />
          <span className="text-[10px]">Report Hazard</span>
        </button>
      </nav>
    </div>
  );
};

