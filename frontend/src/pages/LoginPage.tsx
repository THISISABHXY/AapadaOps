import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { ShieldCheck, Lock, AlertCircle, ArrowLeft } from 'lucide-react';
import { loginSchema, LoginFormData } from '../schemas/authSchema';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../contexts/ToastContext';
import { GovInput } from '../components/ui/GovInput';
import { GovButton } from '../components/ui/GovButton';
import { UserRole } from '../types/user';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login, switchDemoRole } = useAuth();
  const { showToast } = useToast();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: 'collector.puri@nic.in',
      password: 'Password@123',
    },
  });

  const onSubmit = async (data: LoginFormData) => {
    setIsSubmitting(true);
    setErrorMessage(null);
    try {
      await login(data.email, data.password);
      showToast('success', 'Authentication Successful', 'Welcome to AapadaOps EOC Command System');
      navigate('/dashboard');
    } catch (err) {
      setErrorMessage((err as Error).message || 'Invalid government credentials');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleQuickDemo = async (role: UserRole) => {
    try {
      await switchDemoRole(role);
      showToast('info', 'Session Authenticated', `Signed in as ${role.replace('_', ' ')}`);
      navigate('/dashboard');
    } catch (err: any) {
      showToast('error', 'Login Failed', err?.message || 'Could not authenticate persona.');
    }
  };

  return (
    <div className="min-h-screen bg-bg-warm flex flex-col justify-center py-12 px-4 sm:px-6 lg:px-8 font-sans">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex justify-center mb-2">
          <div className="w-12 h-12 rounded bg-forest flex items-center justify-center text-white font-bold text-lg shadow-sm">
            AO
          </div>
        </div>
        <h2 className="text-center text-xl sm:text-2xl font-bold tracking-tight text-ink-primary">
          AapadaOps Administrative Command
        </h2>
        <p className="mt-1 text-center text-xs text-sage">
          Odisha State Disaster Management Authority & Special Relief Commissioner
        </p>
      </div>

      <div className="mt-6 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-6 px-6 sm:px-8 rounded border border-line shadow-sm space-y-5">
          {errorMessage && (
            <div className="p-3 rounded bg-emergency-subtle border border-emergency/30 text-emergency flex items-start gap-2 text-xs">
              <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
              <span>{errorMessage}</span>
            </div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <GovInput
              label="Official Email Address"
              type="email"
              required
              error={errors.email?.message}
              {...register('email')}
              placeholder="officer@nic.in or osdma.gov.in"
            />

            <GovInput
              label="Password"
              type="password"
              required
              error={errors.password?.message}
              {...register('password')}
              placeholder="••••••••••••"
            />

            <div className="flex items-center justify-between text-xs">
              <label className="flex items-center gap-2 cursor-pointer text-ink-secondary">
                <input
                  type="checkbox"
                  className="rounded border-line text-forest focus:ring-forest"
                  {...register('rememberMe')}
                />
                <span>Remember session</span>
              </label>

              <a href="#help" className="text-forest hover:underline font-medium">
                Forgot password?
              </a>
            </div>

            <GovButton
              type="submit"
              variant="primary"
              className="w-full h-10 font-bold"
              isLoading={isSubmitting}
            >
              <Lock className="w-4 h-4 mr-1.5" />
              <span>Authenticate Credentials</span>
            </GovButton>
          </form>

          {/* Quick Demo Persona Shortcuts */}
          <div className="pt-4 border-t border-line space-y-2">
            <div className="text-[11px] font-semibold text-sage uppercase tracking-wider text-center">
              Quick Test Personas (Prototype Evaluation)
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <button
                type="button"
                onClick={() => handleQuickDemo('DISTRICT_ADMIN')}
                className="p-2 text-left rounded border border-line hover:border-forest hover:bg-bg-warm transition-colors"
              >
                <strong className="block text-ink-primary">District Collector</strong>
                <span className="text-[11px] text-sage">Puri District DDMA</span>
              </button>

              <button
                type="button"
                onClick={() => handleQuickDemo('VERIFICATION_OFFICER')}
                className="p-2 text-left rounded border border-line hover:border-forest hover:bg-bg-warm transition-colors"
              >
                <strong className="block text-ink-primary">Verification Officer</strong>
                <span className="text-[11px] text-sage">Tahasildar Desk</span>
              </button>

              <button
                type="button"
                onClick={() => handleQuickDemo('RESPONSE_COORDINATOR')}
                className="p-2 text-left rounded border border-line hover:border-forest hover:bg-bg-warm transition-colors"
              >
                <strong className="block text-ink-primary">Coordinator</strong>
                <span className="text-[11px] text-sage">BDO Tactical Dispatch</span>
              </button>

              <button
                type="button"
                onClick={() => handleQuickDemo('FIELD_WORKER')}
                className="p-2 text-left rounded border border-line hover:border-forest hover:bg-bg-warm transition-colors"
              >
                <strong className="block text-ink-primary">Field Responder</strong>
                <span className="text-[11px] text-sage">ODRAF Unit Commander</span>
              </button>
            </div>
          </div>

          <div className="pt-2 text-center">
            <Link
              to="/"
              className="inline-flex items-center gap-1.5 text-xs text-sage hover:text-ink-primary"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Back to Public Disaster Portal</span>
            </Link>
          </div>
        </div>

        {/* Official IT Security Notice */}
        <div className="mt-4 text-center text-[11px] text-sage flex items-center justify-center gap-1.5">
          <ShieldCheck className="w-4 h-4 text-forest" />
          <span>Secured under the Information Technology Act & Government of Odisha Security Guidelines.</span>
        </div>
      </div>
    </div>
  );
};

