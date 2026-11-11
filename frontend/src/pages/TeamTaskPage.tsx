import React, { useState } from 'react';
import {
  ListTodo,
  Clock,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  Shield,
  User,
} from 'lucide-react';
import { GovCard } from '../components/ui/GovCard';
import { GovBadge } from '../components/ui/GovBadge';
import { GovButton } from '../components/ui/GovButton';
import { taskService } from '../services/taskService';
import { useToast } from '../contexts/ToastContext';
import { DEMO_TASKS } from '../services/demoDataService';
import { Task, TaskStatus } from '../types/task';
import { formatTimeAgo } from '../utilities/formatters';

export const TeamTaskPage: React.FC = () => {
  const { showToast } = useToast();
  const [tasks, setTasks] = useState<Task[]>(DEMO_TASKS);

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
      count: tasks.filter((t) => t.status === 'ON_SCENE').length,
    },
    {
      id: 'RESOLVED',
      label: 'Resolved / Safe',
      count: tasks.filter((t) => t.status === 'RESOLVED').length,
    },
  ];

  const handleAdvanceStatus = async (task: Task, nextStatus: TaskStatus) => {
    try {
      const updated = await taskService.updateTaskStatus(task.id, nextStatus);
      setTasks((prev) => prev.map((t) => (t.id === task.id ? updated : t)));
      showToast('success', 'Task Status Advanced', `Mission ${task.taskCode} is now ${nextStatus}`);
    } catch {
      showToast('error', 'Status Update Failed', 'Could not advance task state.');
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
            Active Missions: {tasks.filter((t) => t.status !== 'RESOLVED').length}
          </span>
          <span className="bg-forest-subtle text-forest border border-forest/30 px-2.5 py-1 rounded font-semibold">
            Resolved: {tasks.filter((t) => t.status === 'RESOLVED').length}
          </span>
        </div>
      </div>

      {/* 2. Four Operational Swimlanes */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 items-start">
        {columns.map((col) => {
          const colTasks = tasks.filter((t) => t.status === col.id);

          return (
            <div key={col.id} className="bg-white rounded border border-line overflow-hidden shadow-xs flex flex-col">
              {/* Column Header */}
              <div className="p-3 border-b border-line bg-bg-warm/60 flex items-center justify-between">
                <span className="text-xs font-bold text-ink-primary uppercase tracking-wider">
                  {col.label}
                </span>
                <span className="font-mono text-xs font-bold bg-white px-2 py-0.5 rounded border border-line text-ink-secondary">
                  {col.count}
                </span>
              </div>

              {/* Column Body Cards */}
              <div className="p-2 space-y-2.5 min-h-[500px] max-h-[700px] overflow-y-auto bg-bg-warm/20">
                {colTasks.length === 0 ? (
                  <div className="p-6 text-center text-xs text-sage italic">
                    No missions in this stage
                  </div>
                ) : (
                  colTasks.map((task) => (
                    <div
                      key={task.id}
                      className={`p-3 bg-white rounded border transition-all shadow-xs space-y-2 ${
                        task.isOverdue ? 'border-emergency/60 bg-emergency-subtle/20' : 'border-line hover:border-line-dark'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-mono text-xs font-bold text-forest">
                          {task.taskCode}
                        </span>
                        <GovBadge
                          variant={task.priority === 'CRITICAL' ? 'emergency' : 'amber'}
                          size="sm"
                        >
                          {task.priority}
                        </GovBadge>
                      </div>

                      <h4 className="text-xs font-semibold text-ink-primary leading-snug">
                        {task.title}
                      </h4>

                      <div className="space-y-1 text-[11px] font-mono text-sage pt-1 border-t border-line/60">
                        <div className="flex justify-between">
                          <span>Target:</span>
                          <strong className="text-ink-primary">{task.targetVillage}</strong>
                        </div>
                        <div className="flex justify-between">
                          <span>Unit:</span>
                          <span className="text-forest font-semibold">{task.assignedUnitOrg}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>SLA Status:</span>
                          <span className={task.isOverdue ? 'text-emergency font-bold' : 'text-sage'}>
                            {task.isOverdue ? '⚠ Overdue' : 'On Schedule'}
                          </span>
                        </div>
                      </div>

                      {/* Action Advance State Button */}
                      <div className="pt-2 border-t border-line">
                        {task.status === 'ASSIGNED' && (
                          <GovButton
                            variant="primary"
                            size="sm"
                            className="w-full text-xs"
                            onClick={() => handleAdvanceStatus(task, 'EN_ROUTE')}
                          >
                            Mark En Route →
                          </GovButton>
                        )}
                        {task.status === 'EN_ROUTE' && (
                          <GovButton
                            variant="primary"
                            size="sm"
                            className="w-full text-xs"
                            onClick={() => handleAdvanceStatus(task, 'ON_SCENE')}
                          >
                            Mark On Scene →
                          </GovButton>
                        )}
                        {task.status === 'ON_SCENE' && (
                          <GovButton
                            variant="primary"
                            size="sm"
                            className="w-full text-xs"
                            onClick={() => handleAdvanceStatus(task, 'RESOLVED')}
                          >
                            Mark Rescue Resolved ✓
                          </GovButton>
                        )}
                        {task.status === 'RESOLVED' && (
                          <div className="text-[11px] font-mono text-forest flex items-center justify-center gap-1 font-semibold py-1">
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            <span>Mission Accomplished</span>
                          </div>
                        )}
                      </div>
                    </div>
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
