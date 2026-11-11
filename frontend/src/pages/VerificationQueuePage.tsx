import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  CheckSquare,
  Filter,
  CheckCircle2,
  XCircle,
  Copy,
  AlertTriangle,
  MapPin,
  Clock,
  ArrowRight,
  ShieldCheck,
} from 'lucide-react';
import { GovCard } from '../components/ui/GovCard';
import { GovBadge } from '../components/ui/GovBadge';
import { GovButton } from '../components/ui/GovButton';
import { GovModal } from '../components/ui/GovModal';
import { AIAdvisoryCallout } from '../components/ui/AIAdvisoryCallout';
import { EmptyState } from '../components/ui/EmptyState';
import { incidentService } from '../services/incidentService';
import { useToast } from '../contexts/ToastContext';
import { Incident, PriorityLevel } from '../types/incident';
import { formatCoordinates, formatTimeAgo, formatMaskedPhone } from '../utilities/formatters';

export const VerificationQueuePage: React.FC = () => {
  const { showToast } = useToast();
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Rejection Modal State
  const [rejectModalOpen, setRejectModalOpen] = useState(false);
  const [rejectionReason, setRejectionReason] = useState('HOAX_REPORT');
  const [rejectionNotes, setRejectionNotes] = useState('');

  const loadQueue = async () => {
    setLoading(true);
    const data = await incidentService.getIncidents({ status: 'NEEDS_VERIFICATION' });
    setIncidents(data);
    setSelectedIncident(data[0] || null);
    setLoading(false);
  };

  useEffect(() => {
    loadQueue();
  }, []);

  const handleVerify = async (priority: PriorityLevel = 'CRITICAL') => {
    if (!selectedIncident) return;
    try {
      await incidentService.verifyIncident(selectedIncident.id, {
        status: 'VERIFIED',
        verifiedPriority: priority,
        verificationNotes: 'Ground truth confirmed with local Revenue Inspector and Sarpanch.',
      });
      showToast('success', 'Incident Verified', `Report ${selectedIncident.incidentCode} marked as verified ground truth.`);
      loadQueue();
    } catch {
      showToast('error', 'Action Failed', 'Could not verify incident.');
    }
  };

  const handleRejectSubmit = async () => {
    if (!selectedIncident) return;
    try {
      await incidentService.verifyIncident(selectedIncident.id, {
        status: 'REJECTED',
        verifiedPriority: 'LOW',
        verificationNotes: rejectionNotes,
        rejectionReason: `${rejectionReason}: ${rejectionNotes}`,
      });
      showToast('info', 'Report Rejected', `Case ${selectedIncident.incidentCode} rejected and archived with justification.`);
      setRejectModalOpen(false);
      setRejectionNotes('');
      loadQueue();
    } catch {
      showToast('error', 'Action Failed', 'Could not record rejection.');
    }
  };

  return (
    <div className="space-y-4">
      {/* 1. Header with Queue Counters */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-line">
        <div>
          <div className="flex items-center gap-2">
            <CheckSquare className="w-5 h-5 text-forest" />
            <h1 className="text-xl font-bold text-ink-primary tracking-tight">
              Incident Verification & Ground Truth Queue
            </h1>
          </div>
          <p className="text-xs text-sage mt-0.5">
            Role: Incident Verification Officer (Tahasildar / Revenue Inspector). Filter unverified incoming reports, eliminate duplicates, and certify genuine emergencies.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="font-mono text-xs px-2.5 py-1 bg-amber-subtle text-amber-dark border border-amber/40 rounded font-bold">
            Pending Audit: {incidents.length}
          </span>
          <Link to="/duplicates">
            <GovButton variant="secondary" size="sm" leftIcon={<Copy className="w-3.5 h-3.5" />}>
              Review Duplicate Clusters
            </GovButton>
          </Link>
        </div>
      </div>

      {/* 2. Main Workbench: Left List + Right Ground Truth Audit Panel */}
      {incidents.length === 0 && !loading ? (
        <EmptyState
          icon="shield"
          title="Verification Queue Clear"
          description="All incoming citizen SOS calls and field reports in Puri District have been verified or resolved."
          action={
            <Link to="/dashboard">
              <GovButton variant="primary" size="sm">
                Return to EOC Dashboard
              </GovButton>
            </Link>
          }
        />
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
          {/* Left Column: Queue List (5 Cols) */}
          <div className="lg:col-span-5 space-y-2">
            <div className="text-xs font-semibold text-sage uppercase tracking-wider flex justify-between items-center px-1">
              <span>Unverified Submissions ({incidents.length})</span>
              <span className="font-mono text-[11px]">Oldest First</span>
            </div>

            <div className="space-y-2 max-h-[700px] overflow-y-auto pr-1">
              {incidents.map((inc) => (
                <div
                  key={inc.id}
                  onClick={() => setSelectedIncident(inc)}
                  className={`p-3.5 rounded border transition-all cursor-pointer text-left ${
                    selectedIncident?.id === inc.id
                      ? 'bg-white border-forest ring-2 ring-forest/20 shadow-xs'
                      : 'bg-white border-line hover:border-line-dark'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-xs font-bold text-ink-primary">
                      {inc.incidentCode}
                    </span>
                    <div className="flex items-center gap-1.5">
                      <GovBadge
                        variant={inc.reportedSeverity === 'CRITICAL' ? 'emergency' : 'amber'}
                        size="sm"
                      >
                        {inc.reportedSeverity}
                      </GovBadge>
                      <span className="text-[11px] font-mono text-sage">
                        {formatTimeAgo(inc.createdAt)}
                      </span>
                    </div>
                  </div>

                  <div className="text-xs font-semibold text-ink-primary mt-1">
                    {inc.villageName}, {inc.blockName}
                  </div>

                  <p className="text-xs text-ink-secondary line-clamp-2 mt-1 leading-relaxed">
                    {inc.rawDescription}
                  </p>

                  <div className="mt-2 pt-2 border-t border-line/60 flex items-center justify-between text-[11px] font-mono text-sage">
                    <span>
                      Stranded: <strong className="text-ink-primary">{inc.personsStranded}</strong>
                    </span>
                    <span>Source: {inc.source}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Right Column: Ground Truth Audit Panel (7 Cols) */}
          {selectedIncident && (
            <div className="lg:col-span-7 space-y-4">
              <GovCard
                header={
                  <div className="flex items-center justify-between w-full">
                    <div>
                      <span className="font-mono text-xs font-bold text-ink-primary">
                        Case File: {selectedIncident.incidentCode}
                      </span>
                      <span className="text-xs text-sage ml-2">
                        {selectedIncident.villageName}, {selectedIncident.blockName}
                      </span>
                    </div>

                    <div className="flex items-center gap-1.5">
                      <GovBadge variant="amber" size="sm">
                        NEEDS VERIFICATION
                      </GovBadge>
                    </div>
                  </div>
                }
              >
                {/* Caller & Location Strip */}
                <div className="grid grid-cols-2 gap-3 text-xs p-3 bg-bg-warm rounded border border-line">
                  <div>
                    <span className="text-sage block text-[11px]">Caller Information:</span>
                    <strong className="text-ink-primary block">{selectedIncident.callerName}</strong>
                    <span className="font-mono text-sage text-[11px]">
                      Phone: {formatMaskedPhone(selectedIncident.callerPhone)}
                    </span>
                  </div>

                  <div>
                    <span className="text-sage block text-[11px]">GPS Coordinates:</span>
                    <strong className="text-ink-primary block font-mono">
                      {formatCoordinates(selectedIncident.latitude, selectedIncident.longitude)}
                    </strong>
                    <span className="text-forest text-[11px] font-medium">Inside Satapada Floodplain</span>
                  </div>
                </div>

                {/* Citizen Raw Narrative */}
                <div className="mt-3 space-y-1">
                  <span className="text-xs font-semibold text-ink-primary block">
                    Citizen Narrative Transcript:
                  </span>
                  <div className="p-3 bg-white rounded border border-line text-xs leading-relaxed text-ink-primary">
                    "{selectedIncident.rawDescription}"
                  </div>
                </div>

                {/* AI Entity Advisory Comparison */}
                {selectedIncident.aiEvaluation && (
                  <div className="mt-3">
                    <AIAdvisoryCallout
                      confidenceScore={selectedIncident.aiEvaluation.confidenceScore}
                      suggestedPriority={selectedIncident.aiEvaluation.suggestedPriority}
                      entities={selectedIncident.aiEvaluation.extractedEntities}
                      rationale="AI analysis detected life-safety keywords: 'infants', '5.5 feet water'. Suggested Priority: CRITICAL."
                    />
                  </div>
                )}

                {/* Three Action Buttons: Verify / Duplicate / Reject */}
                <div className="mt-6 pt-4 border-t border-line flex flex-wrap items-center justify-between gap-3">
                  <div className="flex items-center gap-2">
                    <GovButton
                      variant="primary"
                      size="md"
                      onClick={() => handleVerify('CRITICAL')}
                      leftIcon={<CheckCircle2 className="w-4 h-4" />}
                    >
                      Verify as Genuine Life Threat (CRITICAL)
                    </GovButton>

                    <Link to="/duplicates">
                      <GovButton
                        variant="secondary"
                        size="md"
                        leftIcon={<Copy className="w-4 h-4 text-amber-dark" />}
                      >
                        Merge Duplicate
                      </GovButton>
                    </Link>
                  </div>

                  <GovButton
                    variant="danger"
                    size="md"
                    onClick={() => setRejectModalOpen(true)}
                    leftIcon={<XCircle className="w-4 h-4" />}
                  >
                    Reject Report
                  </GovButton>
                </div>
              </GovCard>
            </div>
          )}
        </div>
      )}

      {/* Mandatory Rejection Reason Modal */}
      <GovModal
        isOpen={rejectModalOpen}
        onClose={() => setRejectModalOpen(false)}
        title="Reject & Archive Incident Report"
        description="Every rejection requires an explicit administrative reason logged into the SDRF compliance audit trail."
        footer={
          <>
            <GovButton variant="secondary" size="sm" onClick={() => setRejectModalOpen(false)}>
              Cancel
            </GovButton>
            <GovButton variant="danger" size="sm" onClick={handleRejectSubmit}>
              Confirm Rejection & Archive
            </GovButton>
          </>
        }
      >
        <div className="space-y-3">
          <div>
            <label className="text-xs font-semibold text-ink-primary block mb-1">
              Standard Rejection Category *
            </label>
            <select
              value={rejectionReason}
              onChange={(e) => setRejectionReason(e.target.value)}
              className="w-full text-xs h-9 px-3 bg-white border border-line rounded text-ink-primary"
            >
              <option value="HOAX_REPORT">Hoax / False Report (Disproved by Local Ground Check)</option>
              <option value="OUTSIDE_JURISDICTION">Outside District Jurisdiction / Wrong Location</option>
              <option value="ALREADY_RESOLVED">Historical Report / Hazard Already Resolved</option>
              <option value="DUPLICATE_CALL">Redundant Duplicate Call (Use Duplicate Tool)</option>
              <option value="INSUFFICIENT_DETAILS">Incomplete Information / Unable to Contact</option>
            </select>
          </div>

          <div>
            <label className="text-xs font-semibold text-ink-primary block mb-1">
              Field Officer Justification Notes *
            </label>
            <textarea
              rows={3}
              value={rejectionNotes}
              onChange={(e) => setRejectionNotes(e.target.value)}
              placeholder="State details of ground check, officer spoken to, or evidence confirming rejection..."
              className="w-full p-2.5 text-xs bg-white border border-line rounded text-ink-primary"
              required
            />
          </div>
        </div>
      </GovModal>
    </div>
  );
};
