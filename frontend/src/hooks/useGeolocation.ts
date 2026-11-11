import { useState, useCallback } from 'react';

interface GeolocationState {
  latitude: number | null;
  longitude: number | null;
  accuracy: number | null;
  loading: boolean;
  error: string | null;
}

export function useGeolocation() {
  const [state, setState] = useState<GeolocationState>({
    latitude: null,
    longitude: null,
    accuracy: null,
    loading: false,
    error: null,
  });

  const getPosition = useCallback(() => {
    if (!navigator.geolocation) {
      setState((prev) => ({
        ...prev,
        error: 'Geolocation is not supported by your browser (ଜିଓଲୋକେସନ ସମର୍ଥିତ ନୁହେଁ)',
      }));
      return;
    }

    setState((prev) => ({ ...prev, loading: true, error: null }));

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setState({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy,
          loading: false,
          error: null,
        });
      },
      (error) => {
        let msg = 'Unable to retrieve location (ସ୍ଥାନ ଚିହ୍ନଟ ହୋଇପାରିଲା ନାହିଁ)';
        if (error.code === error.PERMISSION_DENIED) {
          msg = 'Location permission denied. Please allow GPS access or place pin on map.';
        }
        setState((prev) => ({ ...prev, loading: false, error: msg }));
      },
      {
        enableHighAccuracy: true,
        timeout: 12000,
        maximumAge: 30000,
      }
    );
  }, []);

  return { ...state, getPosition };
}

