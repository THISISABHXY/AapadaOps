import { z } from 'zod';

export const citizenIncidentSchema = z.object({
  callerName: z.string().min(2, 'Name is required (ଅତିକମରେ ୨ଟି ଅକ୍ଷର)'),
  callerPhone: z
    .string()
    .min(10, 'Valid 10-digit mobile number required (୧୦-ଅଙ୍କ ମୋବାଇଲ ନମ୍ବର)')
    .regex(/^[6-9]\d{9}$/, 'Must be a valid Indian mobile number starting with 6, 7, 8, or 9'),
  districtName: z.string().min(1, 'District selection required (ଜିଲ୍ଲା ଚୟନ କରନ୍ତୁ)'),
  blockName: z.string().optional(),
  villageName: z.string().min(2, 'Village/Locality name required (ଗ୍ରାମ/ସାହି ନାମ)'),
  latitude: z.number().min(17.5).max(23.0, 'Coordinates must be within Odisha bounds'),
  longitude: z.number().min(81.0).max(88.0, 'Coordinates must be within Odisha bounds'),
  hazardType: z.enum([
    'CYCLONE',
    'FLOOD',
    'WATERLOGGING',
    'EMBANKMENT_BREACH',
    'STRUCTURAL_COLLAPSE',
    'MEDICAL_EMERGENCY',
    'HEATWAVE',
    'OTHER',
  ]),
  reportedSeverity: z.enum(['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']),
  personsStranded: z.coerce.number().min(0, 'Cannot be negative').default(1),
  hasVulnerablePeople: z.boolean().default(false),
  hasInfants: z.boolean().default(false),
  hasPregnantWomen: z.boolean().default(false),
  hasElderly: z.boolean().default(false),
  hasInjured: z.boolean().default(false),
  rawDescription: z
    .string()
    .min(5, 'Please provide brief details (ସଂକ୍ଷିପ୍ତ ବିବରଣୀ ପ୍ରଦାନ କରନ୍ତୁ)'),
  photoUrls: z.array(z.string()).optional(),
});

export type CitizenIncidentFormData = z.infer<typeof citizenIncidentSchema>;

export const verifyIncidentSchema = z.object({
  status: z.enum(['VERIFIED', 'REJECTED', 'DISPUTED']),
  verifiedPriority: z.enum(['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']),
  verificationNotes: z.string().min(3, 'Verification notes are required'),
  rejectionReason: z.string().optional(),
});

export type VerifyIncidentFormData = z.infer<typeof verifyIncidentSchema>;
