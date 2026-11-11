import { useEffect, useRef } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useToast } from '../contexts/ToastContext';

export function useRealtimeNotifications(channel = 'incidents') {
  const queryClient = useQueryClient();
  const { showToast } = useToast();
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);

  useEffect(() => {
    let isMounted = true;
    const wsUrl = (import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000/api/v1') + `/ws/${channel}`;

    function connect() {
      if (!isMounted) return;

      try {
        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;

        ws.onopen = () => {
          // Send heartbeat ping
          ws.send('ping');
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (data.event === 'PONG') return;

            // Handle server event broadcasts
            if (data.event === 'INCIDENT_CREATED') {
              queryClient.invalidateQueries({ queryKey: ['incidents'] });
              queryClient.invalidateQueries({ queryKey: ['analytics'] });
              showToast(
                'warning',
                'New Incident Reported',
                `${data.incident?.title || 'Distress SOS'} in ${data.incident?.district_name || 'Odisha'}`
              );
            } else if (data.event === 'TASK_DISPATCHED' || data.event === 'TASK_UPDATED') {
              queryClient.invalidateQueries({ queryKey: ['tasks'] });
              showToast('info', 'Task Update', `Tactical mission status updated`);
            } else if (data.event === 'ALERT_BROADCAST') {
              queryClient.invalidateQueries({ queryKey: ['alerts'] });
              showToast('warning', 'SATARK Early Warning Broadcast', data.headline || 'Emergency Alert Issued');
            }
          } catch {
            // Non-JSON ping message
          }
        };

        ws.onclose = () => {
          if (isMounted) {
            // Reconnect after 5 seconds
            reconnectTimeoutRef.current = window.setTimeout(connect, 5000);
          }
        };

        ws.onerror = () => {
          ws.close();
        };
      } catch {
        // Silently schedule reconnect
        if (isMounted) {
          reconnectTimeoutRef.current = window.setTimeout(connect, 5000);
        }
      }
    }

    connect();

    // Heartbeat ping interval
    const pingInterval = setInterval(() => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send('ping');
      }
    }, 25000);

    return () => {
      isMounted = false;
      clearInterval(pingInterval);
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [channel, queryClient, showToast]);
}
