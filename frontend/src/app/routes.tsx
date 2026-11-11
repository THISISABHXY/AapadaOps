import React from 'react';
import { createBrowserRouter, Navigate } from 'react-router-dom';
import { AppLayout } from '../layouts/AppLayout';
import { PublicLayout } from '../layouts/PublicLayout';

import { LandingPage } from '../pages/LandingPage';
import { LoginPage } from '../pages/LoginPage';
import { DashboardPage } from '../pages/DashboardPage';
import { IncidentMapPage } from '../pages/IncidentMapPage';
import { IncidentDetailPage } from '../pages/IncidentDetailPage';
import { IncidentSubmitPage } from '../pages/IncidentSubmitPage';
import { VerificationQueuePage } from '../pages/VerificationQueuePage';
import { DuplicateReviewPage } from '../pages/DuplicateReviewPage';
import { ResourceManagementPage } from '../pages/ResourceManagementPage';
import { ResponseCoordinationPage } from '../pages/ResponseCoordinationPage';
import { TeamTaskPage } from '../pages/TeamTaskPage';
import { SheltersPage } from '../pages/SheltersPage';
import { AnalyticsPage } from '../pages/AnalyticsPage';
import { UserManagementPage } from '../pages/UserManagementPage';
import { SystemSettingsPage } from '../pages/SystemSettingsPage';
import { MobileFieldPage } from '../pages/MobileFieldPage';

export const router = createBrowserRouter([
  // Public Portal Routes
  {
    path: '/',
    element: <PublicLayout />,
    children: [
      { index: true, element: <LandingPage /> },
      { path: 'sos', element: <IncidentSubmitPage /> },
    ],
  },
  // Dedicated Standalone Public & Mobile Screens
  { path: '/login', element: <LoginPage /> },
  { path: '/field', element: <MobileFieldPage /> },

  // Protected EOC Administrative Shell
  {
    path: '/',
    element: <AppLayout />,
    children: [
      { path: 'dashboard', element: <DashboardPage /> },
      { path: 'map', element: <IncidentMapPage /> },
      { path: 'incidents/:id', element: <IncidentDetailPage /> },
      { path: 'verification', element: <VerificationQueuePage /> },
      { path: 'duplicates', element: <DuplicateReviewPage /> },
      { path: 'resources', element: <ResourceManagementPage /> },
      { path: 'coordination', element: <ResponseCoordinationPage /> },
      { path: 'tasks', element: <TeamTaskPage /> },
      { path: 'shelters', element: <SheltersPage /> },
      { path: 'analytics', element: <AnalyticsPage /> },
      { path: 'users', element: <UserManagementPage /> },
      { path: 'settings', element: <SystemSettingsPage /> },
      { path: '*', element: <Navigate to="/dashboard" replace /> },
    ],
  },
]);
