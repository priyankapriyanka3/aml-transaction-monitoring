// Reusable sticky action footer component for bottom-fixed action buttons
import { ReactNode } from 'react';

interface StickyActionFooterProps {
  children: ReactNode;
  className?: string;
}

export function StickyActionFooter({
  children,
  className = '',
}: StickyActionFooterProps) {
  return (
    <footer
      className={`sticky bottom-0 bg-surface-container-high border-t border-outline-variant ${className}`}
    >
      <div className="flex items-center gap-md p-lg">{children}</div>
    </footer>
  );
}

interface ActionButtonProps {
  children: ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'outlined' | 'text';
  disabled?: boolean;
  fullWidth?: boolean;
  type?: 'button' | 'submit';
  className?: string;
}

export function ActionButton({
  children,
  onClick,
  variant = 'primary',
  disabled = false,
  fullWidth = false,
  type = 'button',
  className = '',
}: ActionButtonProps) {
  const baseClasses = 'touch-target inline-flex items-center justify-center gap-sm px-2xl py-md rounded text-ll transition-colors';
  
  const variantClasses = {
    primary: 'bg-primary text-on-primary hover:bg-primary/90 active:bg-primary/80',
    outlined: 'bg-surface text-primary border border-outline hover:bg-surface-variant active:bg-surface-container',
    text: 'bg-transparent text-secondary hover:bg-surface-variant active:bg-surface-container',
  };

  const disabledClasses = disabled ? 'opacity-38 cursor-not-allowed pointer-events-none' : '';
  const widthClasses = fullWidth ? 'w-full' : '';

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`${baseClasses} ${variantClasses[variant]} ${disabledClasses} ${widthClasses} ${className}`}
    >
      {children}
    </button>
  );
}
