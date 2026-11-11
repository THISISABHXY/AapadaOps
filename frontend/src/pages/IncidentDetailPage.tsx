import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  ShieldAlert,
  MapPin,
  Clock,
  UserCheck,
  Building2,
  FileText,
  CheckCircle2,
  AlertOctagon,
  Copy,
} from 'lucide-react';
import { GovCard } from '../components/ui/GovCard';
import { GovBadge } from '../components/ui/GovBadge';
import { GovButton } from '../components/ui/GovButton';
import { AIAdvisoryCallout } from '../components/ui/AIAdvisoryCallout';
import { incidentService } from '../services/incidentService';
import { useToast } from '../contexts/ToastContext';
import { Incident, PriorityLevel } from '../types/incident';
import { formatCoordinates, formatDate, formatMaskedPhone } from '../utilities/formatters';

export const IncidentDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [incident, setIncident] = useState<Incident | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Administrative Action Form State
  const [selectedStatus, setSelectedStatus] = useState<'VERIFIED' | 'REJECTED' | 'DISPUTED'>('VERIFIED');
  const [selectedPriority, setSelectedPriority] = useState<PriorityLevel>('CRITICAL');
  const [verificationNotes, setVerificationNotes] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  useEffect(() => {
    if (id) {
      incidentService.getIncidentById(id).then((data) => {
        setIncident(data);
        if (data?.verifiedPriority) setSelectedPriority(data.verifiedPriority);
        setLoading(false);
      });
    }
  }, [id]);

  const handleAuditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!incident) return;
    setIsSubmitting(true);
    try {
      const updated = await incidentService.verifyIncident(incident.id, {
        status: selectedStatus,
        verifiedPriority: selectedPriority,
        verificationNotes,
      });
      setIncident(updated);
      showToast('success', 'Incident Status Updated', `Case file ${incident.incidentCode} transitioned to ${selectedStatus}`);
    } catch {
      showToast('error', 'Update Failed', 'Unable to record verification status');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="p-8 text-center font-mono text-xs text-sage">
        Loading case record from persistent database...
      </div>
    );
  }

  if (!incident) {
    return (
      <GovCard className="text-center p-8">
        <h3 className="text-base font-semibold text-ink-primary">Incident Record Not Found</h3>
        <p className="text-xs text-sage mt-1 mb-4">
          The requested disaster case code does not exist in the active district database.
        </p>
        <Link to="/verification">
          <GovButton variant="primary" size="sm">Back to Verification Queue</GovButton>
        </Link>
      </GovCard>
    );
  }

  return (
    <div className="space-y-4">
      {/* 1. Breadcrumbs and Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-line">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate(-1)}
            className="p-1 rounded text-sage hover:text-ink-primary hover:bg-white border border-line"
            aria-label="Back"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-lg font-bold text-ink-primary">
                {incident.incidentCode}
              </span>
              <GovBadge
                variant={
                  incident.status === 'VERIFIED'
                    ? 'forest'
                    : incident.status === 'NEEDS_VERIFICATION'
                    ? 'amber'
                    : incident.status === 'REJECTED'
                    ? 'emergency'
                    : 'sage'
                }
              >
                {incident.status}
              </GovBadge>
              <GovBadge
                variant={incident.reportedSeverity === 'CRITICAL' ? 'emergency' : 'amber'}
                size="sm"
              >
                {incident.hazardType}
              </GovBadge>
            </div>
            <p className="text-xs text-sage mt-0.5">
              Logged via {incident.source} • Registered on {formatDate(incident.createdAt)}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Link to={`/coordination`}>
            <GovButton variant="primary" size="sm">
              Mobilize Tactical Unit
            </GovButton>
          </Link>
        </div>
      </div>

      {/* 2. Main Two-Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Left Column: Narrative, Geotag, Evidence & AI Advisory (7 Cols) */}
        <div className="lg:col-span-7 space-y-4">
          {/* Citizen Distress Narrative */}
          <GovCard
            header={
              <div className="flex items-center justify-between w-full">
                <span className="font-semibold text-xs uppercase tracking-wider text-sage">
                  Distress Report Narrative
                </span>
                <span className="font-mono text-xs text-sage">
                  Stranded: <strong className="text-emergency">{incident.personsStranded} Persons</strong>
                </span>
              </div>
            }
          >
            <p className="text-sm text-ink-primary leading-relaxed bg-bg-warm p-3 rounded border border-line">
              "{incident.rawDescription}"
            </p>

            <div className="mt-3 grid grid-cols-2 gap-3 text-xs">
              <div className="p-2.5 bg-bg-warm rounded border border-line space-y-1">
                <span className="text-sage block text-[11px]">Reporting Citizen / Caller:</span>
                <strong className="text-ink-primary block">{incident.callerName}</strong>
                <span className="font-mono text-sage text-[11px]">
                  Phone: {formatMaskedPhone(incident.callerPhone)}
                </span>
              </div>

              <div className="p-2.5 bg-bg-warm rounded border border-line space-y-1">
                <span className="text-sage block text-[11px]">Ground Jurisdiction:</span>
                <strong className="text-ink-primary block">{incident.villageName}</strong>
                <span className="text-sage text-[11px]">
                  {incident.blockName} Block, {incident.districtName}
                </span>
              </div>
            </div>

            <div className="mt-3 flex items-center justify-between text-xs font-mono p-2 bg-white rounded border border-line">
              <span className="text-sage flex items-center gap-1">
                <MapPin className="w-3.5 h-3.5 text-forest" /> Coordinates:
              </span>
              <strong className="text-ink-primary">
                {formatCoordinates(incident.latitude, incident.longitude)}
              </strong>
            </div>
          </GovCard>

          {/* AI Decision Support Advisory Box */}
          {incident.aiEvaluation ? (
            <AIAdvisoryCallout
              confidenceScore={incident.aiEvaluation.confidenceScore}
              suggestedPriority={incident.aiEvaluation.suggestedPriority}
              entities={incident.aiEvaluation.extractedEntities}
              rationale="Language model extracted high vulnerability indicators ('infants', '5.5 feet water depth', 'rising canal spate') from caller narrative. Requires officer verification."
            />
          ) : (
            <div className="p-3 bg-bg-warm rounded border border-line text-xs text-sage font-mono">
              AI Decision Support: No high-risk NLP anomalies flagged for this ticket.
            </div>
          )}

          {/* Photographic Evidence Attachment */}
          <GovCard
            header={
              <span className="font-semibold text-xs uppercase tracking-wider text-sage">
                Field Evidence Attachments
              </span>
            }
          >
            <div className="grid grid-cols-2 gap-3">
              <div className="h-32 bg-bg-subtle rounded border border-line flex flex-col items-center justify-center p-3 text-center">
                <FileText className="w-8 h-8 text-sage mb-1" />
                <span className="text-xs font-mono text-ink-primary">satapada_flood_01.jpg</span>
                <span className="text-[10px] text-sage">Uploaded by Citizen • Geotag Verified</span>
              </div>
              <div className="h-32 bg-bg-subtle rounded border border-dashed border-line flex flex-col items-center justify-center p-3 text-center">
                <span className="text-xs text-sage">No secondary photo attached</span>
              </div>
            </div>
          </GovCard>
        </div>

        {/* Right Column: Verification Action Form & Case Audit Timeline (5 Cols) */}
        <div className="lg:col-span-5 space-y-4">
          {/* Administrative Verification Form */}
          <GovCard
            header={
              <div className="flex items-center gap-1.5 font-semibold text-xs uppercase tracking-wider text-forest">
                <UserCheck className="w-4 h-4" />
                <span>Officer Audit & Action Form</span>
              </div>
            }
          >
            <form onSubmit={handleAuditSubmit} className="space-y-3">
              <div>
                <label className="text-xs font-semibold text-ink-primary block mb-1">
                  Determination State:
                </label>
                <div className="grid grid-cols-3 gap-1.5 text-xs">
                  <button
                    type="button"
                    onClick={() => setSelectedStatus('VERIFIED')}
                    className={`py-1.5 px-2 rounded font-semibold border cursor-pointer ${
                      selectedStatus === 'VERIFIED'
                        ? 'bg-forest text-white border-forest'
                        : 'bg-white text-ink-primary border-line hover:bg-bg-warm'
                    }`}
                  >
                    Verify
                  </button>
                  <button
                    type="button"
                    onClick={() => setSelectedStatus('DISPUTED')}
                    className={`py-1.5 px-2 rounded font-semibold border cursor-pointer ${
                      selectedStatus === 'DISPUTED'
                        ? 'bg-amber text-white border-amber'
                        : 'bg-white text-ink-primary border-line hover:bg-bg-warm'
                    }`}
                  >
                    Dispute
                  </button>
                  <button
                    type="button"
                    onClick={() => setSelectedStatus('REJECTED')}
                    className={`py-1.5 px-2 rounded font-semibold border cursor-pointer ${
                      selectedStatus === 'REJECTED'
                        ? 'bg-emergency text-white border-emergency'
                        : 'bg-white text-ink-primary border-line hover:bg-bg-warm'
                    }`}
                  >
                    Reject
                  </button>
                </div>
              </div>

              <div>
                <label className="text-xs font-semibold text-ink-primary block mb-1">
                  Verified Priority Level:
                </label>
                <select
                  value={selectedPriority}
                  onChange={(e) => setSelectedPriority(e.target.value as PriorityLevel)}
                  className="w-full text-xs h-9 px-3 bg-white border border-line rounded text-ink-primary font-medium"
                >
                  <option value="CRITICAL">CRITICAL (Immediate Life Threat)</option>
                  <option value="HIGH">HIGH (Severe Hazard / Impending Threat)</option>
                  <option value="MEDIUM">MEDIUM (Property / Infrastructure)</option>
                  <option value="LOW">LOW (Advisory / Non-Urgent)</option>
                </select>
              </div>

              <div>
                <label className="text-xs font-semibold text-ink-primary block mb-1">
                  Verification Audit Remarks:
                </label>
                <textarea
                  rows={3}
                  value={verificationNotes}
                  onChange={(e) => setVerificationNotes(e.target.value)}
                  placeholder="Cross-checked with Sarpanch / Local Police. 14 people confirmed stranded at community hall roof..."
                  className="w-full p-2.5 text-xs bg-white border border-line rounded text-ink-primary focus:outline-none focus:ring-1 focus:ring-forest"
                  required
                />
              </div>

              <GovButton
                type="submit"
                variant="primary"
                size="sm"
                className="w-full"
                isLoading={isSubmitting}
              >
                Sign Off & Record in SDRF Audit
              </GovButton>
            </form>
          </GovCard>

          {/* Case Audit Timeline */}
          <GovCard
            header={
              <span className="font-semibold text-xs uppercase tracking-wider text-sage">
                Tamper-Evident Audit Trail
              </span>
            }
          >
            <div className="space-y-3 relative before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-line text-xs font-mono">
              <div className="pl-6 relative">
                <span className="w-2.5 h-2.5 rounded-full bg-forest absolute left-1 top-1 ring-2 ring-white" />
                <span className="text-sage block text-[10px]">{formatDate(incident.createdAt)}</span>
                <strong className="text-ink-primary">Incident Created (SUBMITTED)</strong>
                <p className="text-sage text-[11px] font-sans mt-0.5">
                  Captured via {incident.source} from caller {incident.callerName}.
                </p>
              </div>

              {incident.aiEvaluation && (
                <div className="pl-6 relative">
                  <span className="w-2.5 h-2.5 rounded-full bg-sage absolute left-1 top-1 ring-2 ring-white" />
                  <span className="text-sage block text-[10px]">{formatDate(incident.aiEvaluation.evaluatedAt)}</span>
                  <strong className="text-ink-primary">AI Natural Language Triage</strong>
                  <p className="text-sage text-[11px] font-sans mt-0.5">
                    Entities extracted. Advisory Priority: {incident.aiEvaluation.suggestedPriority}.
                  </p>
                </div>
              )}

              {incident.verifiedAt && (
                <div className="pl-6 relative">
                  <span className="w-2.5 h-2.5 rounded-full bg-forest absolute left-1 top-1 ring-2 ring-white" />
                  <span className="text-sage block text-[10px]">{formatDate(incident.verifiedAt)}</span>
                  <strong className="text-ink-primary">Verified as Genuine Ground Truth</strong>
                  <p className="text-sage text-[11px] font-sans mt-0.5">
                    Authorized by: {incident.verifiedByName}. Priority locked to {incident.verifiedPriority}.
                  </p>
                </div>
              )}
            </div>
          </GovCard>
        </div>
      </div>
    </div>
  );
};
