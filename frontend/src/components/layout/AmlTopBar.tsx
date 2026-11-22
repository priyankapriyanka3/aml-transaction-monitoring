// Reusable top app bar component matching Material 3 design system
import { useAuth } from '../../lib/auth-context';

interface AmlTopBarProps {
  title: string;
  subtitle?: string;
  eyebrow?: string;
  showUserBadge?: boolean;
  onBackClick?: () => void;
}

export function AmlTopBar({
  title,
  subtitle,
  eyebrow,
  showUserBadge = true,
  onBackClick,
}: AmlTopBarProps) {
  const { user } = useAuth();

  return (
    <header className="bg-surface border-b border-outline-variant">
      <div className="flex items-center gap-xs px-xs py-xs min-h-[64px]">
        {onBackClick && (
          <button
            type="button"
            onClick={onBackClick}
            className="touch-target flex items-center justify-center rounded-full hover:bg-surface-variant transition-colors text-primary"
            aria-label="Navigate back"
          >
            <svg
              className="w-6 h-6"
              fill="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z" />
            </svg>
          </button>
        )}

        <div className="flex-1 px-md">
          {eyebrow && (
            <p className="text-ls text-on-surface-variant uppercase mb-xs">
              {eyebrow}
            </p>
          )}
          <h1 className="text-hm font-bold text-on-surface">{title}</h1>
          {subtitle && (
            <p className="text-bs text-on-surface-variant mt-xs">{subtitle}</p>
          )}
        </div>

        {showUserBadge && user && (
          <div className="flex items-center gap-xs px-md py-xs bg-info-container rounded-sm">
            <svg
              className="w-5 h-5 text-info"
              fill="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
            </svg>
            <span className="text-lm text-on-info-container">
              {user.primary_role}
            </span>
          </div>
        )}
      </div>
    </header>
  );
}
