import React, { createContext, useContext, useState, useEffect } from 'react';

interface DemoModeContextType {
  isDemoMode: boolean;
  toggleDemoMode: () => void;
  setDemoMode: (val: boolean) => void;
}

const DemoModeContext = createContext<DemoModeContextType | undefined>(undefined);

export const DemoModeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isDemoMode, setIsDemoMode] = useState<boolean>(() => {
    const saved = localStorage.getItem('aapadaops_demo_mode');
    return saved !== null ? saved === 'true' : true; // Default to demo mode enabled during initial frontend review
  });

  useEffect(() => {
    localStorage.setItem('aapadaops_demo_mode', String(isDemoMode));
  }, [isDemoMode]);

  const toggleDemoMode = () => setIsDemoMode((prev) => !prev);
  const setDemoMode = (val: boolean) => setIsDemoMode(val);

  return (
    <DemoModeContext.Provider value={{ isDemoMode, toggleDemoMode, setDemoMode }}>
      {children}
    </DemoModeContext.Provider>
  );
};

export const useDemoMode = () => {
  const context = useContext(DemoModeContext);
  if (!context) {
    throw new Error('useDemoMode must be used within a DemoModeProvider');
  }
  return context;
};
