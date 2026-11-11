/**
 * AapadaOps Administrative Data Formatters
 */

export function formatDate(isoString: string | null | undefined): string {
  if (!isoString) return '—';
  try {
    const d = new Date(isoString);
    return new Intl.DateTimeFormat('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
    }).format(d) + ' IST';
  } catch {
    return isoString;
  }
}

export function formatTimeAgo(isoString: string | null | undefined): string {
  if (!isoString) return '—';
  try {
    const d = new Date(isoString);
    const now = new Date();
    const diffMs = now.getTime() - d.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${Math.floor(diffHours / 24)}d ago`;
  } catch {
    return isoString;
  }
}

export function formatCoordinates(lat?: number, lng?: number): string {
  if (lat === undefined || lng === undefined) return '—';
  const latStr = `${Math.abs(lat).toFixed(4)}° ${lat >= 0 ? 'N' : 'S'}`;
  const lngStr = `${Math.abs(lng).toFixed(4)}° ${lng >= 0 ? 'E' : 'W'}`;
  return `${latStr}, ${lngStr}`;
}

export function formatMaskedPhone(phone?: string): string {
  if (!phone) return '—';
  const cleaned = phone.replace(/\s+/g, '');
  if (cleaned.length >= 10) {
    return cleaned.slice(0, 3) + '••••' + cleaned.slice(-3);
  }
  return phone;
}

