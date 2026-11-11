import { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error in component tree:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-[300px] flex items-center justify-center p-6">
          <div className="max-w-md w-full bg-white border border-emergency/30 rounded p-6 text-center shadow-sm">
            <div className="inline-flex p-3 bg-emergency-subtle rounded-full text-emergency mb-3">
              <AlertTriangle className="w-6 h-6" />
            </div>
            <h3 className="text-base font-semibold text-ink-primary mb-1">
              Operational Interface Error
            </h3>
            <p className="text-xs text-sage mb-4">
              An unexpected error occurred while rendering this module. Operational safety logs have been preserved.
            </p>
            {this.state.error && (
              <pre className="text-left font-mono text-[11px] p-2.5 bg-bg-warm rounded border border-line overflow-x-auto text-emergency mb-4 max-h-28">
                {this.state.error.message}
              </pre>
            )}
            <button
              onClick={() => this.setState({ hasError: false })}
              className="inline-flex items-center gap-1.5 px-4 py-2 bg-forest text-white text-xs font-semibold rounded hover:bg-forest-dark transition-colors cursor-pointer"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              Reload Module
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
