import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import {
  Copy,
  CheckCircle2,
  Split,
  MapPin,
  Clock,
  ArrowRight,
  ShieldCheck,
  Building2,
  AlertTriangle,
} from 'lucide-react';
import { GovCard } from '../components/ui/GovCard';
import { GovBadge } from '../components/ui/GovBadge';
import { GovButton } from '../components/ui/GovButton';
import { incidentService, mapBackendIncident } from '../services/incidentService';
import { useToast } from '../contexts/ToastContext';
import { DEMO_INCIDENTS } from '../services/demoDataService';
import { Incident } from '../types/incident';
import { formatCoordinates, formatTimeAgo, formatMaskedPhone } from '../utilities/formatters';

export const DuplicateReviewPage: React.FC = () => {
  const { showToast } = useToast();
  const queryClient = useQueryClient();

  const { data: clusters = [], isLoading: loadingClusters } = useQuery({
    queryKey: ['duplicate-clusters'],
    queryFn: () => incidentService.getDuplicateClusters(),
  });

  const { data: allIncidents = [] } = useQuery({
    queryKey: ['incidents'],
    queryFn: () => incidentService.getIncidents(),
  });

  const activeCluster = clusters[0];
  const primaryIncident: Incident =
    (activeCluster?.primary_incident && mapBackendIncident(activeCluster.primary_incident)) ||
    allIncidents.find((i) => i.id === activeCluster?.primary_incident_id) ||
    allIncidents[0] ||
    DEMO_INCIDENTS[0];

  const candidateDuplicate: Incident =
    (activeCluster?.duplicates?.[0] && mapBackendIncident(activeCluster.duplicates[0])) ||
    allIncidents.find((i) => i.parentIncidentId === primaryIncident?.id || i.id === 'inc_0895') ||
    allIncidents[1] ||
    DEMO_INCIDENTS[1];

  const [merged, setMerged] = useState<boolean>(candidateDuplicate?.status === 'DUPLICATE');
  const [isMerging, setIsMerging] = useState<boolean>(false);

  const handleMerge = async () => {
    if (!primaryIncident || !candidateDuplicate) return;
    setIsMerging(true);
    try {
      await incidentService.linkDuplicate(candidateDuplicate.id, primaryIncident.id);
      setMerged(true);
      queryClient.invalidateQueries({ queryKey: ['duplicate-clusters'] });
      queryClient.invalidateQueries({ queryKey: ['incidents'] });
      showToast(
        'success',
        'Duplicate Merged Successfully',
        `Linked ${candidateDuplicate.incidentCode} under Master Incident ${primaryIncident.incidentCode}`
      );
    } catch (err: any) {
      showToast('error', 'Merge Failed', err?.message || 'Could not link duplicate reports.');
    } finally {
      setIsMerging(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* 1. Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-line">
        <div>
          <div className="flex items-center gap-2">
            <Copy className="w-5 h-5 text-amber-dark" />
            <h1 className="text-xl font-bold text-ink-primary tracking-tight">
              Spatial Deduplication & Cluster Review Workbench
            </h1>
          </div>
          <p className="text-xs text-sage mt-0.5">
            DBSCAN Spatial Engine flagged multiple distress calls within 250 meters of each other. Consolidate into a single master dispatch task.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="font-mono text-xs px-2.5 py-1 bg-forest-subtle text-forest border border-forest/30 rounded font-bold">
            Cluster Radius: {activeCluster?.spatial_radius_meters ? `${activeCluster.spatial_radius_meters}m` : '220 Meters'}
          </span>
        </div>
      </div>

      {/* 2. Side-by-Side Comparison */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Master / Parent Incident Card */}
        <GovCard
          header={
            <div className="flex items-center justify-between w-full">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-forest" />
                <span className="font-bold text-xs uppercase tracking-wider text-forest">
                  ESTABLISHED PARENT INCIDENT
                </span>
              </div>
              <span className="font-mono text-xs font-bold text-ink-primary">
                {primaryIncident.incidentCode}
              </span>
            </div>
          }
        >
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-ink-primary">
                {primaryIncident.villageName}, {primaryIncident.blockName || primaryIncident.districtName}
              </span>
              <GovBadge variant="emergency" size="sm">
                {primaryIncident.reportedSeverity}
              </GovBadge>
            </div>

            <p className="text-xs text-ink-primary leading-relaxed bg-bg-warm p-2.5 rounded border border-line">
              {primaryIncident.rawDescription}
            </p>

            <div className="grid grid-cols-2 gap-2 text-xs font-mono">
              <div className="p-2 bg-white rounded border border-line">
                <span className="text-sage block text-[10px]">Coordinates</span>
                <span className="font-semibold text-ink-primary">
                  {formatCoordinates(primaryIncident.latitude, primaryIncident.longitude)}
                </span>
              </div>
              <div className="p-2 bg-white rounded border border-line">
                <span className="text-sage block text-[10px]">Caller Identity</span>
                <span className="font-semibold text-ink-primary">
                  {primaryIncident.callerName} ({formatMaskedPhone(primaryIncident.callerPhone)})
                </span>
              </div>
            </div>

            <div className="pt-2 border-t border-line flex items-center justify-between text-xs font-mono">
              <span className="text-sage">Reported: {formatTimeAgo(primaryIncident.createdAt)}</span>
              <span className="text-emergency font-bold">{primaryIncident.personsStranded} Stranded</span>
            </div>
          </div>
        </GovCard>

        {/* Candidate Duplicate Card */}
        <GovCard
          header={
            <div className="flex items-center justify-between w-full">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-amber" />
                <span className="font-bold text-xs uppercase tracking-wider text-amber-dark">
                  CANDIDATE DUPLICATE DISTRESS CALL
                </span>
              </div>
              <span className="font-mono text-xs font-bold text-ink-primary">
                {candidateDuplicate.incidentCode}
              </span>
            </div>
          }
        >
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-ink-primary">
                {candidateDuplicate.villageName}, {candidateDuplicate.blockName || candidateDuplicate.districtName}
              </span>
              <GovBadge variant="amber" size="sm">
                {merged ? 'MERGED DUPLICATE' : 'PENDING REVIEW'}
              </GovBadge>
            </div>

            <p className="text-xs text-ink-primary leading-relaxed bg-bg-warm p-2.5 rounded border border-line">
              {candidateDuplicate.rawDescription}
            </p>

            <div className="grid grid-cols-2 gap-2 text-xs font-mono">
              <div className="p-2 bg-white rounded border border-line">
                <span className="text-sage block text-[10px]">Coordinates</span>
                <span className="font-semibold text-ink-primary">
                  {formatCoordinates(candidateDuplicate.latitude, candidateDuplicate.longitude)}
                </span>
              </div>
              <div className="p-2 bg-white rounded border border-line">
                <span className="text-sage block text-[10px]">Caller Identity</span>
                <span className="font-semibold text-ink-primary">
                  {candidateDuplicate.callerName} ({formatMaskedPhone(candidateDuplicate.callerPhone)})
                </span>
              </div>
            </div>

            <div className="pt-2 border-t border-line flex items-center justify-between text-xs font-mono">
              <span className="text-sage">Reported: {formatTimeAgo(candidateDuplicate.createdAt)}</span>
              <span className="text-emergency font-bold">{candidateDuplicate.personsStranded} Stranded</span>
            </div>
          </div>
        </GovCard>
      </div>

      {/* 3. Deduplication Action Console */}
      <GovCard>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-forest" />
              <h3 className="text-xs font-bold text-ink-primary">
                DBSCAN Confidence Match: {activeCluster?.confidence_score ? `${Math.round(activeCluster.confidence_score * 100)}%` : '89% High Likelihood'}
              </h3>
            </div>
            <p className="text-xs text-sage">
              Distance: ~220m | Time Delta: ~45 mins | Shared Hazard: {primaryIncident.hazardType}. Merging transfers stranded headcount to the master case without creating duplicate dispatch dispatches.
            </p>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            {merged ? (
              <span className="text-xs font-bold text-forest flex items-center gap-1.5 px-3 py-1.5 bg-forest-subtle border border-forest/30 rounded">
                <CheckCircle2 className="w-4 h-4" /> Already Consolidated
              </span>
            ) : (
              <GovButton
                variant="primary"
                size="sm"
                onClick={handleMerge}
                isLoading={isMerging}
                leftIcon={<Copy className="w-3.5 h-3.5" />}
              >
                Confirm & Merge into Master Task
              </GovButton>
            )}
          </div>
        </div>
      </GovCard>
    </div>
  );
};
