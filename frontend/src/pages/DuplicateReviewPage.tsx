import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Copy,
  CheckCircle2,
  Split,
  MapPin,
  Clock,
  ArrowRight,
  ShieldCheck,
  Building2,
} from 'lucide-react';
import { GovCard } from '../components/ui/GovCard';
import { GovBadge } from '../components/ui/GovBadge';
import { GovButton } from '../components/ui/GovButton';
import { incidentService } from '../services/incidentService';
import { useToast } from '../contexts/ToastContext';
import { DEMO_INCIDENTS } from '../services/demoDataService';
import { formatCoordinates, formatTimeAgo, formatMaskedPhone } from '../utilities/formatters';

export const DuplicateReviewPage: React.FC = () => {
  const { showToast } = useToast();

  const masterIncident = DEMO_INCIDENTS[0]; // OD-2026-0492 Satapada
  const candidateDuplicate = DEMO_INCIDENTS[1]; // OD-2026-0493 Satapada

  const [merged, setMerged] = useState<boolean>(candidateDuplicate.status === 'DUPLICATE');

  const handleMerge = async () => {
    try {
      await incidentService.linkDuplicate(candidateDuplicate.id, masterIncident.id);
      setMerged(true);
      showToast(
        'success',
        'Duplicate Merged Successfully',
        `Linked ${candidateDuplicate.incidentCode} under Master Incident ${masterIncident.incidentCode}`
      );
    } catch {
      showToast('error', 'Merge Failed', 'Could not link duplicate reports.');
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
            Cluster Radius: 250 Meters
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
                {masterIncident.incidentCode}
              </span>
            </div>
          }
          className="border-forest/50"
        >
          <div className="space-y-3">
            <div className="p-3 bg-forest-subtle/50 rounded border border-forest/20 text-xs font-mono space-y-1">
              <div className="flex justify-between">
                <span className="text-sage">Location:</span>
                <strong className="text-ink-primary">
                  {masterIncident.villageName}, {masterIncident.blockName}
                </strong>
              </div>
              <div className="flex justify-between">
                <span className="text-sage">Reported By:</span>
                <span className="text-ink-primary">{masterIncident.callerName}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sage">Caller Contact:</span>
                <span className="text-ink-primary">{formatMaskedPhone(masterIncident.callerPhone)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sage">GPS Coordinates:</span>
                <span className="text-ink-primary font-bold">
                  {formatCoordinates(masterIncident.latitude, masterIncident.longitude)}
                </span>
              </div>
              <div className="flex justify-between pt-1 border-t border-forest/20">
                <span className="text-sage">Stranded Headcount:</span>
                <strong className="text-emergency">{masterIncident.personsStranded} Persons</strong>
              </div>
            </div>

            <div className="space-y-1 text-xs">
              <span className="font-semibold text-ink-primary">Parent Distress Narrative:</span>
              <p className="p-2.5 bg-bg-warm rounded border border-line text-ink-secondary leading-relaxed">
                "{masterIncident.rawDescription}"
              </p>
            </div>
          </div>
        </GovCard>

        {/* Candidate Duplicate Report */}
        <GovCard
          header={
            <div className="flex items-center justify-between w-full">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-amber" />
                <span className="font-bold text-xs uppercase tracking-wider text-amber-dark">
                  CANDIDATE DUPLICATE SUBMISSION
                </span>
              </div>
              <span className="font-mono text-xs font-bold text-ink-primary">
                {candidateDuplicate.incidentCode}
              </span>
            </div>
          }
          className={merged ? 'border-line opacity-75' : 'border-amber/60'}
        >
          <div className="space-y-3">
            <div className="p-3 bg-amber-subtle/50 rounded border border-amber/20 text-xs font-mono space-y-1">
              <div className="flex justify-between">
                <span className="text-sage">Location:</span>
                <strong className="text-ink-primary">
                  {candidateDuplicate.villageName}, {candidateDuplicate.blockName}
                </strong>
              </div>
              <div className="flex justify-between">
                <span className="text-sage">Reported By:</span>
                <span className="text-ink-primary">{candidateDuplicate.callerName}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sage">Caller Contact:</span>
                <span className="text-ink-primary">{formatMaskedPhone(candidateDuplicate.callerPhone)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sage">Distance from Parent:</span>
                <strong className="text-amber-dark font-bold">45 Meters Apart</strong>
              </div>
              <div className="flex justify-between pt-1 border-t border-amber/20">
                <span className="text-sage">Time Delta:</span>
                <strong className="text-ink-primary">Received 3m 15s later</strong>
              </div>
            </div>

            <div className="space-y-1 text-xs">
              <span className="font-semibold text-ink-primary">Candidate Narrative:</span>
              <p className="p-2.5 bg-bg-warm rounded border border-line text-ink-secondary leading-relaxed">
                "{candidateDuplicate.rawDescription}"
              </p>
            </div>

            {/* AI Spatial Similarity Score */}
            <div className="p-2.5 bg-bg-warm rounded border border-line text-xs font-mono flex items-center justify-between">
              <span className="text-sage">Spatial-Textual Correlation:</span>
              <strong className="text-forest">92% Match Probability</strong>
            </div>

            {/* Merge Actions */}
            <div className="pt-2 flex items-center gap-2">
              {merged ? (
                <div className="w-full p-2 text-center text-xs font-semibold bg-forest-subtle text-forest rounded border border-forest/30 flex items-center justify-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Successfully Merged under {masterIncident.incidentCode}</span>
                </div>
              ) : (
                <>
                  <GovButton
                    variant="primary"
                    size="sm"
                    className="flex-1"
                    onClick={handleMerge}
                    leftIcon={<Copy className="w-3.5 h-3.5" />}
                  >
                    Merge into Master Ticket
                  </GovButton>

                  <GovButton
                    variant="secondary"
                    size="sm"
                    className="flex-1"
                    onClick={() => showToast('info', 'Incident Split', 'Retained as distinct emergency')}
                    leftIcon={<Split className="w-3.5 h-3.5" />}
                  >
                    Keep Separate
                  </GovButton>
                </>
              )}
            </div>
          </div>
        </GovCard>
      </div>

      {/* 3. Deduplication Administrative Rules Info */}
      <GovCard>
        <div className="text-xs text-sage space-y-1 leading-relaxed">
          <strong className="text-ink-primary block mb-1">
            Odisha Disaster Management Authority — Deduplication Protocol:
          </strong>
          <p>
            1. Merging a duplicate does <strong>not delete</strong> the child record. The caller contact number and audio recording are preserved under the parent ticket for rescue team communications.
          </p>
          <p>
            2. The cumulative stranded headcount is updated automatically to ensure tactical rescue boats have adequate passenger capacity.
          </p>
        </div>
      </GovCard>
    </div>
  );
};

