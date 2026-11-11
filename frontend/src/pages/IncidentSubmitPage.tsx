import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import {
  ShieldAlert,
  MapPin,
  CheckCircle2,
  Navigation,
  PhoneCall,
  Camera,
  AlertTriangle,
  User,
  Users,
} from 'lucide-react';
import { citizenIncidentSchema, CitizenIncidentFormData } from '../schemas/incidentSchema';
import { incidentService } from '../services/incidentService';
import { useGeolocation } from '../hooks/useGeolocation';
import { useToast } from '../contexts/ToastContext';
import { GovCard } from '../components/ui/GovCard';
import { GovInput } from '../components/ui/GovInput';
import { GovButton } from '../components/ui/GovButton';
import { ODISHA_DISTRICTS } from '../services/demoDataService';

export const IncidentSubmitPage: React.FC = () => {
  const { showToast } = useToast();
  const [lang, setLang] = useState<'EN' | 'OR'>('OR'); // Default to Odia for rural citizen accessibility
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submittedCode, setSubmittedCode] = useState<string | null>(null);

  const { latitude, longitude, loading: geoLoading, error: geoError, getPosition } = useGeolocation();

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm<CitizenIncidentFormData>({
    resolver: zodResolver(citizenIncidentSchema),
    defaultValues: {
      callerName: '',
      callerPhone: '',
      districtName: 'Puri',
      blockName: 'Krushnaprasad',
      villageName: '',
      latitude: 19.8135,
      longitude: 85.8312,
      hazardType: 'FLOOD',
      reportedSeverity: 'HIGH',
      personsStranded: 1,
      hasVulnerablePeople: false,
      hasInfants: false,
      hasPregnantWomen: false,
      hasElderly: false,
      hasInjured: false,
      rawDescription: '',
    },
  });

  const selectedHazard = watch('hazardType');
  const personsStranded = watch('personsStranded');

  useEffect(() => {
    if (latitude && longitude) {
      setValue('latitude', Number(latitude.toFixed(4)));
      setValue('longitude', Number(longitude.toFixed(4)));
      showToast('success', 'GPS Synced', `Location locked: ${latitude.toFixed(4)}° N, ${longitude.toFixed(4)}° E`);
    }
  }, [latitude, longitude, setValue, showToast]);

  const onSubmit = async (data: CitizenIncidentFormData) => {
    setIsSubmitting(true);
    try {
      const result = await incidentService.submitIncident({
        callerName: data.callerName,
        callerPhone: data.callerPhone,
        districtName: data.districtName,
        blockName: data.blockName,
        villageName: data.villageName,
        latitude: data.latitude,
        longitude: data.longitude,
        hazardType: data.hazardType,
        reportedSeverity: data.reportedSeverity,
        personsStranded: data.personsStranded,
        hasVulnerablePeople: data.hasVulnerablePeople,
        rawDescription: data.rawDescription,
        source: 'CITIZEN_WEB',
      });
      setSubmittedCode(result.incidentCode);
      showToast('success', 'Emergency SOS Dispatched', `Tracking ID: ${result.incidentCode}`);
    } catch {
      showToast('error', 'Transmission Failed', 'Unable to transmit emergency request. Please dial 1077.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // 1. Success Receipt Screen
  if (submittedCode) {
    return (
      <div className="max-w-lg mx-auto py-8">
        <GovCard className="text-center p-6 border-forest/40">
          <div className="w-14 h-14 bg-forest-subtle rounded-full flex items-center justify-center text-forest mx-auto mb-3">
            <CheckCircle2 className="w-8 h-8" />
          </div>

          <span className="font-mono text-xs uppercase tracking-wider text-forest font-bold">
            {lang === 'OR' ? 'ଜରୁରୀ ସହାୟତା ପଞ୍ଜୀକୃତ ହେଲା' : 'Emergency SOS Received'}
          </span>

          <h2 className="text-2xl font-bold font-mono text-ink-primary mt-1">
            {submittedCode}
          </h2>

          <p className="text-xs text-ink-secondary mt-2 leading-relaxed">
            {lang === 'OR'
              ? 'ଆପଣଙ୍କର ବିପର୍ଯ୍ୟୟ ରିପୋର୍ଟ ସ୍ଥାନୀୟ ଜିଲ୍ଲା ଜରୁରୀକାଳୀନ କକ୍ଷ (DEOC) ଏବଂ ODRAF ୟୁନିଟକୁ ପ୍ରେରଣ କରାଯାଇଛି । ଦୟାକରି ସୁରକ୍ଷିତ ସ୍ଥାନରେ ରୁହନ୍ତୁ ।'
              : 'Your emergency report has been transmitted directly to District EOC (Puri) and assigned tactical rescue forces. Please remain at your current safe location.'}
          </p>

          <div className="mt-4 p-3 bg-bg-warm rounded border border-line text-left text-xs font-mono space-y-1">
            <div className="flex justify-between">
              <span className="text-sage">Status:</span>
              <strong className="text-amber-dark">QUEUED FOR VERIFICATION</strong>
            </div>
            <div className="flex justify-between">
              <span className="text-sage">Dedicated DEOC Helpline:</span>
              <strong className="text-ink-primary">1077 (Toll Free)</strong>
            </div>
            <div className="flex justify-between">
              <span className="text-sage">State EOC Helpline:</span>
              <strong className="text-ink-primary">1070</strong>
            </div>
          </div>

          <div className="mt-6 flex flex-col gap-2">
            <a
              href="tel:1077"
              className="inline-flex items-center justify-center gap-2 h-10 bg-emergency hover:bg-emergency-dark text-white font-bold text-xs rounded transition-colors"
            >
              <PhoneCall className="w-4 h-4" />
              <span>{lang === 'OR' ? 'ଜିଲ୍ଲା କଣ୍ଟ୍ରୋଲ ରୁମକୁ କଲ୍ କରନ୍ତୁ (1077)' : 'Call District Control Room (1077)'}</span>
            </a>

            <button
              onClick={() => setSubmittedCode(null)}
              className="text-xs text-sage hover:text-ink-primary py-2 underline"
            >
              {lang === 'OR' ? 'ଅନ୍ୟ ଏକ ରିପୋର୍ଟ ଦାଖଲ କରନ୍ତୁ' : 'Submit another report'}
            </button>
          </div>
        </GovCard>
      </div>
    );
  }

  return (
    <div className="max-w-xl mx-auto py-4 space-y-4">
      {/* Language Switcher Bar */}
      <div className="flex items-center justify-between pb-2 border-b border-line">
        <div className="flex items-center gap-2">
          <ShieldAlert className="w-5 h-5 text-emergency" />
          <h1 className="text-base font-bold text-ink-primary">
            {lang === 'OR' ? 'ଜରୁରୀ ସହାୟତା ପଞ୍ଜୀକରଣ (SOS)' : 'Emergency Citizen SOS Reporting'}
          </h1>
        </div>

        <div className="flex items-center gap-1 font-mono text-xs">
          <button
            type="button"
            onClick={() => setLang('OR')}
            className={`px-2.5 py-1 rounded cursor-pointer ${
              lang === 'OR' ? 'bg-forest text-white font-bold' : 'bg-bg-warm text-ink-primary border border-line'
            }`}
          >
            ଓଡ଼ିଆ
          </button>
          <button
            type="button"
            onClick={() => setLang('EN')}
            className={`px-2.5 py-1 rounded cursor-pointer ${
              lang === 'EN' ? 'bg-forest text-white font-bold' : 'bg-bg-warm text-ink-primary border border-line'
            }`}
          >
            English
          </button>
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        {/* Step 1: Location & Coordinates */}
        <GovCard
          header={
            <span className="font-semibold text-xs uppercase tracking-wider text-sage">
              1. {lang === 'OR' ? 'ଆପଣଙ୍କ ସ୍ଥାନ (Location & GPS)' : 'Your Location'}
            </span>
          }
        >
          <div className="space-y-3">
            <div className="flex items-center justify-between p-2.5 bg-bg-warm rounded border border-line">
              <div className="text-xs">
                <span className="font-semibold text-ink-primary block">
                  {lang === 'OR' ? 'ଫୋନ GPS ଦ୍ୱାରା ଚିହ୍ନଟ କରନ୍ତୁ' : 'Auto-detect Device GPS Coordinates'}
                </span>
                <span className="font-mono text-[11px] text-sage">
                  {watch('latitude')}° N, {watch('longitude')}° E
                </span>
              </div>
              <GovButton
                type="button"
                variant="secondary"
                size="sm"
                onClick={getPosition}
                isLoading={geoLoading}
                leftIcon={<Navigation className="w-3.5 h-3.5 text-forest" />}
              >
                {lang === 'OR' ? 'ସ୍ଥାନ ଚିହ୍ନଟ' : 'Locate Me'}
              </GovButton>
            </div>

            {geoError && (
              <div className="text-xs text-emergency bg-emergency-subtle p-2 rounded border border-emergency/20">
                {geoError}
              </div>
            )}

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-semibold text-ink-primary block mb-1">
                  {lang === 'OR' ? 'ଜିଲ୍ଲା (District)' : 'District'} *
                </label>
                <select
                  {...register('districtName')}
                  className="w-full text-xs h-9 px-2.5 bg-white border border-line rounded text-ink-primary"
                >
                  {ODISHA_DISTRICTS.map((d) => (
                    <option key={d} value={d}>
                      {d}
                    </option>
                  ))}
                </select>
              </div>

              <GovInput
                label={lang === 'OR' ? 'ବ୍ଲକ (Block)' : 'Block'}
                error={errors.blockName?.message}
                {...register('blockName')}
                placeholder="e.g. Krushnaprasad"
              />
            </div>

            <GovInput
              label={lang === 'OR' ? 'ଗ୍ରାମ / ସାହି / ଠିକଣା (Village / Landmark)' : 'Village / Area'}
              required
              error={errors.villageName?.message}
              {...register('villageName')}
              placeholder={lang === 'OR' ? 'ଉଦାହରଣ: ସାତପଡ଼ା ମନ୍ଦିର ନିକଟ' : 'e.g. Near Satapada High School'}
            />
          </div>
        </GovCard>

        {/* Step 2: Nature of Emergency */}
        <GovCard
          header={
            <span className="font-semibold text-xs uppercase tracking-wider text-sage">
              2. {lang === 'OR' ? 'ବିପର୍ଯ୍ୟୟର ପ୍ରକାର (Nature of Hazard)' : 'Nature of Hazard'}
            </span>
          }
        >
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
            {[
              { id: 'FLOOD', labelEn: 'Trapped by Flood', labelOr: 'ବନ୍ୟା ଘେରରେ' },
              { id: 'CYCLONE', labelEn: 'Cyclone Damage', labelOr: 'ବାତ୍ୟା କ୍ଷୟକ୍ଷତି' },
              { id: 'EMBANKMENT_BREACH', labelEn: 'River Breach', labelOr: 'ନଦୀବନ୍ଧ ଭାଙ୍ଗିବା' },
              { id: 'STRUCTURAL_COLLAPSE', labelEn: 'House Collapse', labelOr: 'ଘର ଭାଙ୍ଗିବା' },
              { id: 'MEDICAL_EMERGENCY', labelEn: 'Medical Crisis', labelOr: 'ଚିକିତ୍ସା ସହାୟତା' },
              { id: 'OTHER', labelEn: 'Road Block / Other', labelOr: 'ରାସ୍ତା ଅବରୋଧ / ଅନ୍ୟାନ୍ୟ' },
            ].map((hazard) => (
              <button
                key={hazard.id}
                type="button"
                onClick={() => setValue('hazardType', hazard.id as any)}
                className={`p-2.5 rounded border text-left text-xs transition-colors cursor-pointer ${
                  selectedHazard === hazard.id
                    ? 'border-forest bg-forest-subtle font-bold text-forest ring-1 ring-forest'
                    : 'border-line bg-white text-ink-primary hover:bg-bg-warm'
                }`}
              >
                <div className="font-semibold">{lang === 'OR' ? hazard.labelOr : hazard.labelEn}</div>
                <div className="text-[10px] text-sage font-mono uppercase">{hazard.id.replace('_', ' ')}</div>
              </button>
            ))}
          </div>

          {/* Stranded Count Stepper */}
          <div className="mt-4 pt-3 border-t border-line flex items-center justify-between">
            <div>
              <span className="text-xs font-semibold text-ink-primary block">
                {lang === 'OR' ? 'ଫସିରହିଥିବା ଲୋକଙ୍କ ସଂଖ୍ୟା' : 'People Needing Rescue'}
              </span>
              <span className="text-[11px] text-sage">
                {lang === 'OR' ? 'ସମୁଦାୟ ଫସିଥିବା ଲୋକ' : 'Total stranded headcount'}
              </span>
            </div>

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setValue('personsStranded', Math.max(1, personsStranded - 1))}
                className="w-8 h-8 rounded border border-line bg-white text-ink-primary font-mono text-base font-bold flex items-center justify-center hover:bg-bg-warm"
              >
                -
              </button>
              <span className="w-10 text-center font-mono text-base font-bold text-ink-primary">
                {personsStranded}
              </span>
              <button
                type="button"
                onClick={() => setValue('personsStranded', personsStranded + 1)}
                className="w-8 h-8 rounded border border-line bg-white text-ink-primary font-mono text-base font-bold flex items-center justify-center hover:bg-bg-warm"
              >
                +
              </button>
            </div>
          </div>

          {/* Vulnerability Checklist */}
          <div className="mt-3 pt-3 border-t border-line space-y-2">
            <span className="text-xs font-semibold text-ink-primary block">
              {lang === 'OR' ? 'ବିଶେଷ ସହାୟତା ଆବଶ୍ୟକ କରୁଥିବା ବ୍ୟକ୍ତି:' : 'Vulnerable Persons Present:'}
            </span>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <label className="flex items-center gap-2 cursor-pointer p-2 bg-bg-warm rounded border border-line">
                <input
                  type="checkbox"
                  {...register('hasInfants')}
                  className="rounded text-forest focus:ring-forest"
                />
                <span>{lang === 'OR' ? 'ଶିଶୁ (Infants / Babies)' : 'Infants / Babies'}</span>
              </label>

              <label className="flex items-center gap-2 cursor-pointer p-2 bg-bg-warm rounded border border-line">
                <input
                  type="checkbox"
                  {...register('hasPregnantWomen')}
                  className="rounded text-forest focus:ring-forest"
                />
                <span>{lang === 'OR' ? 'ଗର୍ଭବତୀ ମହିଳା' : 'Pregnant Women'}</span>
              </label>

              <label className="flex items-center gap-2 cursor-pointer p-2 bg-bg-warm rounded border border-line">
                <input
                  type="checkbox"
                  {...register('hasElderly')}
                  className="rounded text-forest focus:ring-forest"
                />
                <span>{lang === 'OR' ? 'ବରିଷ୍ଠ ନାଗରିକ' : 'Elderly (60+ yrs)'}</span>
              </label>

              <label className="flex items-center gap-2 cursor-pointer p-2 bg-bg-warm rounded border border-line">
                <input
                  type="checkbox"
                  {...register('hasInjured')}
                  className="rounded text-forest focus:ring-forest"
                />
                <span>{lang === 'OR' ? 'ଆହତ ବ୍ୟକ୍ତି' : 'Injured / Sick'}</span>
              </label>
            </div>
          </div>
        </GovCard>

        {/* Step 3: Contact & Description */}
        <GovCard
          header={
            <span className="font-semibold text-xs uppercase tracking-wider text-sage">
              3. {lang === 'OR' ? 'ଯୋଗାଯୋଗ ଓ ସୂଚନା (Contact & Details)' : 'Contact & Details'}
            </span>
          }
        >
          <div className="space-y-3">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <GovInput
                label={lang === 'OR' ? 'ଆପଣଙ୍କ ନାମ (Your Name)' : 'Your Full Name'}
                required
                error={errors.callerName?.message}
                {...register('callerName')}
                placeholder={lang === 'OR' ? 'ଉଦାହରଣ: ପ୍ରକାଶ ନାୟକ' : 'Prakash Nayak'}
              />

              <GovInput
                label={lang === 'OR' ? 'ମୋବାଇଲ ନମ୍ବର (Mobile Number)' : '10-Digit Mobile Number'}
                required
                type="tel"
                error={errors.callerPhone?.message}
                {...register('callerPhone')}
                placeholder="9861012345"
              />
            </div>

            <div>
              <label className="text-xs font-semibold text-ink-primary block mb-1">
                {lang === 'OR' ? 'ବିସ୍ତୃତ ସୂଚନା ଦିଅନ୍ତୁ (Describe Emergency Situation)' : 'Situation Description'} *
              </label>
              <textarea
                rows={3}
                {...register('rawDescription')}
                placeholder={
                  lang === 'OR'
                    ? 'କେତେ ଉଚ୍ଚର ପାଣି ପଶିଛି? କେଉଁଠି ଆଶ୍ରୟ ନେଇଛନ୍ତି? କି ସହାୟତା ଦରକାର?'
                    : 'Describe water height, location in building, and immediate assistance required...'
                }
                className="w-full p-2.5 text-xs bg-white border border-line rounded text-ink-primary focus:outline-none focus:ring-1 focus:ring-forest"
              />
              {errors.rawDescription && (
                <span className="text-xs text-emergency mt-1 block font-medium">
                  {errors.rawDescription.message}
                </span>
              )}
            </div>
          </div>
        </GovCard>

        {/* Submit SOS Button */}
        <GovButton
          type="submit"
          variant="danger"
          size="lg"
          className="w-full text-base font-bold h-12 shadow-md cursor-pointer"
          isLoading={isSubmitting}
        >
          <ShieldAlert className="w-5 h-5 mr-2" />
          <span>
            {lang === 'OR' ? 'ଜରୁରୀ ସହାୟତା ପଠାନ୍ତୁ (DISPATCH RESCUE SOS)' : 'TRANSMIT EMERGENCY SOS DISPATCH'}
          </span>
        </GovButton>

        <p className="text-center text-[11px] text-sage">
          {lang === 'OR'
            ? 'ମିଥ୍ୟା ସୂଚନା ଦେବା ଦଣ୍ଡନୀୟ ଅପରାଧ । ଜରୁରୀକାଳୀନ କର୍ମଚାରୀ ଆପଣଙ୍କୁ ଯୋଗାଯୋଗ କରିବେ ।'
            : 'Frivolous emergency reporting is punishable under the Disaster Management Act 2005.'}
        </p>
      </form>
    </div>
  );
};

