import React from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import {
  ListTodo,
  Clock,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  Shield,
  User,
  Navigation,
} from 'lucide-react';
import { GovCard } from '../components/ui/GovCard';
import { GovBadge } from '../components/ui/GovBadge';
import { GovButton } from '../components/ui/GovButton';
import { taskService } from '../services/taskService';
import { useToast } from '../contexts/ToastContext';
import { Task, TaskStatus } from '../types/task';
import { formatTimeAgo } from '../utilities/formatters';

export const TeamTaskPage: React.FC = () => {
  const { showToast } = useToast();
  const queryClient = useQueryClient();

  const { data: tasks = [], isLoading } = useQuery({
    queryKey: ['tasks'],
    queryFn: () => taskService.getTasks(),
    refetchInterval: 10000,
  });

  const columns: { id: TaskStatus; label: string; count: number }[] = [
    {
      id: 'ASSIGNED',
      label: 'Assigned / Mobilizing',
      count: tasks.filter((t) => t.status === 'ASSIGNED').length,
    },
    {
      id: 'EN_ROUTE',
      label: 'En Route',
      count: tasks.filter((t) => t.status === 'EN_ROUTE').length,
    },
    {
      id: 'ON_SCENE',
      label: 'On Scene / Active Rescue',
      count: tasks.filter((t) => t.status === 'ON_SCENE' || t.status === 'IN_PROGRESS').length,
    },
    {
      id: 'RESOLVED',
      label: 'Resolved / Completed',
      count: tasks.filter((t) => t.status === 'RESOLVED' || t.status === 'COMPLETED').length,
    },
  ];

  const handleAdvanceStatus = async (task: Task, nextStatus: TaskStatus) => {
    try {
      await taskService.updateTaskStatus(task.id, nextStatus, `Advanced to ${nextStatus} by on-ground controller.`);
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      queryClient.invalidateQueries({ queryKey: ['incidents'] });
      showToast('success', 'Task Status Advanced', `Mission ${task.taskCode} is now ${nextStatus}`);
    } catch (err: any) {
      showToast('error', 'Status Update Failed', err?.message || 'Could not advance task state.');
    }
  };

  return (
    <div className="space-y-4">
      {/* 1. Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-line">
        <div>
          <div className="flex items-center gap-2">
            <ListTodo className="w-5 h-5 text-forest" />
            <h1 className="text-xl font-bold text-ink-primary tracking-tight">
              Operational Team Task Board & Rescue Missions
            </h1>
          </div>
          <p className="text-xs text-sage mt-0.5">
            Real-time status of all active tactical rescue and road clearance missions assigned to ODRAF, NDRF, and Fire Services.
          </p>
        </div>

        <div className="flex items-center gap-2 text-xs font-mono">
          <span className="bg-white border border-line px-2.5 py-1 rounded font-semibold text-ink-primary">
            Active Missions: {tasks.filter((t) => t.status !== 'RESOLVED' && t.status !== 'COMPLETED').length}
          </span>
          <span className="bg-forest-subtle text-forest border border-forest/30 px-2.5 py-1 rounded font-semibold">
            Resolved: {tasks.filter((t) => t.status === 'RESOLVED' || t.status === 'COMPLETED').length}
          </span>
        </div>
      </div>

      {/* 2. Four-Column Kanban Board */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
        {columns.map((col) => {
          const colTasks = tasks.filter((t) => {
            if (col.id === 'ON_SCENE') return t.status === 'ON_SCENE' || t.status === 'IN_PROGRESS';
            if (col.id === 'RESOLVED') return t.status === 'RESOLVED' || t.status === 'COMPLETED';
            return t.status === col.id;
          });

          return (
            <div key={col.id} className="bg-bg-warm/80 rounded border border-line p-2.5 flex flex-col min-h-[500px]">
              {/* Column Header */}
              <div className="flex items-center justify-between pb-2 mb-2 border-b border-line">
                <span className="text-xs font-bold text-ink-primary tracking-tight">
                  {col.label}
                </span>
                <span className="w-5 h-5 rounded-full bg-white border border-line font-mono text-[11px] font-bold text-ink-primary flex items-center justify-center">
                  {colTasks.length}
                </span>
              </div>

              {/* Tasks List in Column */}
              <div className="space-y-2 flex-1 overflow-y-auto">
                {colTasks.length === 0 ? (
                  <div className="text-center py-10 text-xs text-sage font-mono">
                    No active tasks
                  </div>
                ) : (
                  colTasks.map((task) => (
                    <GovCard key={task.id} padding="sm" className="bg-white hover:border-line-dark transition-colors">
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="font-mono text-[11px] font-bold text-ink-primary">
                            {task.taskCode}
                          </span>
                          <GovBadge
                            variant={task.priority === 'CRITICAL' ? 'emergency' : 'amber'}
                            size="sm"
                          >
                            {task.priority}
                          </GovBadge>
                        </div>

                        <h4 className="text-xs font-semibold text-ink-primary leading-tight line-clamp-2">
                          {task.title}
                        </h4>

                        <div className="text-[11px] text-sage flex items-center gap-1 font-mono">
                          <Shield className="w-3 h-3 text-forest" />
                          <span>{task.assignedUnitName}</span>
                        </div>

                        <div className="pt-2 border-t border-line text-[10px] text-sage flex items-center justify-between font-mono">
                          <span>SLA: {task.slaHours || 4} Hours</span>
                          <span>Target: {task.targetVillage}</span>
                        </div>

                        {/* Lifecycle Steppers */}
                        <div className="pt-2 flex items-center justify-between gap-1">
                          {task.status === 'ASSIGNED' && (
                            <GovButton
                              variant="secondary"
                              size="sm"
                              className="w-full text-[10px] h-7"
                              onClick={() => handleAdvanceStatus(task, 'EN_ROUTE')}
                            >
                              Mobilize En Route →
                            </GovButton>
                          )}
                          {task.status === 'EN_ROUTE' && (
                            <GovButton
                              variant="primary"
                              size="sm"
                              className="w-full text-[10px] h-7"
                              onClick={() => handleAdvanceStatus(task, 'ON_SCENE')}
                            >
                              Arrived On Scene →
                            </GovButton>
                          )}
                          {(task.status === 'ON_SCENE' || task.status === 'IN_PROGRESS') && (
                            <GovButton
                              variant="primary"
                              size="sm"
                              className="w-full text-[10px] h-7 bg-forest hover:bg-forest/90"
                              onClick={() => handleAdvanceStatus(task, 'COMPLETED')}
                            >
                              Mark Completed ✓
                            </GovButton>
                          )}
                          {(task.status === 'RESOLVED' || task.status === 'COMPLETED') && (
                            <span className="text-[10px] text-forest font-semibold flex items-center gap-1 mx-auto py-1">
                              <CheckCircle2 className="w-3.5 h-3.5" /> Mission Secured
                            </span>
                          )}
                        </div>
                      </div>
                    </GovCard>
                  ))
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
