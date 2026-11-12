# AapadaOps Disaster Incident Evaluation Datasets

## Overview
This directory contains the ground-truth annotated benchmark datasets used to empirically evaluate the **AapadaOps** AI advisory, bilingual information extraction, spatial deduplication, prioritization, and resource optimization engines.

## Dataset Files
- `odisha_160_incidents.json`: 160 meticulously labelled disaster incident reports reflecting real Odisha disaster geography across all 30 districts.

## Structure of Each Incident Record
```json
{
  "id": "INC-OD-2026-0001",
  "category": "EMBANKMENT_BREACH",
  "district": "Jajpur",
  "village": "Kantapada",
  "river": "Baitarani",
  "english_text": "River Baitarani embankment breached near Kantapada village in Jajpur...",
  "odia_text": "ଯାଜପୁର ଜିଲ୍ଲାର କଣ୍ଟାପଡ଼ା ନିକଟରେ ବୈତରଣୀ ନଦୀର ବନ୍ଧ ଭାଙ୍ଗିଯାଇଛି...",
  "latitude": 20.8500,
  "longitude": 86.3300,
  "expected_severity": "CRITICAL",
  "expected_stranded": 45,
  "has_medical_urgency": false,
  "is_coastal": true
}
```

## Geographic & Linguistic Coverage
- **Districts Represented:** All 30 districts of Odisha (Angul, Balasore, Bargarh, Bhadrak, Balangir, Boudh, Cuttack, Deogarh, Dhenkanal, Gajapati, Ganjam, Jagatsinghpur, Jajpur, Jharsuguda, Kalahandi, Kandhamal, Kendrapara, Keonjhar, Khordha, Koraput, Malkangiri, Mayurbhanj, Nabarangpur, Nayagarh, Nuapada, Puri, Rayagada, Sambalpur, Subarnapur, Sundargarh).
- **Linguistic Balance:** 100% paired Odia and English text with authentic disaster vocabularies.
- **Hazard Classes:** Embankment Breach, Cyclone Wind, Flood Inundation, Fallen Tree / Road Block, Medical Emergency, Stranded Persons.

