// Utility functions for common operations
import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Merge className values with Tailwind-aware deduplication
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

/**
 * Format currency amount with locale-aware formatting
 */
export function formatCurrency(amount: number, currency = 'USD'): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
  }).format(amount);
}

/**
 * Format ISO datetime string to readable format
 */
export function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * Format ISO datetime string to relative time (e.g., "3 hours ago")
 */
export function formatRelativeTime(iso: string): string {
  const now = Date.now();
  const then = new Date(iso).getTime();
  const diff = now - then;

  const minutes = Math.floor(diff / 60000);
  if (minutes < 1) return 'just now';
  if (minutes < 60) return `${minutes}m ago`;

  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;

  const days = Math.floor(hours / 24);
  if (days < 30) return `${days}d ago`;

  const months = Math.floor(days / 30);
  if (months < 12) return `${months}mo ago`;

  const years = Math.floor(months / 12);
  return `${years}y ago`;
}

/**
 * Get badge color classes based on status
 */
export function getStatusBadgeColor(status: string): string {
  const normalized = status.toLowerCase();

  if (normalized.includes('critical') || normalized.includes('match')) {
    return 'bg-critical-container text-on-critical-container';
  }

  if (normalized.includes('warning') || normalized.includes('high')) {
    return 'bg-warning-container text-on-warning-container';
  }

  if (normalized.includes('success') || normalized.includes('pass') || normalized.includes('closed')) {
    return 'bg-success-container text-on-success-container';
  }

  if (normalized.includes('info') || normalized.includes('under review') || normalized.includes('investigating')) {
    return 'bg-info-container text-on-info-container';
  }

  return 'bg-surface-variant text-on-surface-variant';
}

/**
 * Get badge color classes based on risk score
 */
export function getRiskBadgeColor(score: number): string {
  if (score >= 80) {
    return 'bg-critical-container text-on-critical-container';
  }

  if (score >= 50) {
    return 'bg-warning-container text-on-warning-container';
  }

  if (score >= 30) {
    return 'bg-info-container text-on-info-container';
  }

  return 'bg-surface-variant text-on-surface-variant';
}

/**
 * Get priority label from risk score
 */
export function getPriorityLabel(score: number): string {
  if (score >= 80) return 'Critical';
  if (score >= 50) return 'High';
  if (score >= 30) return 'Medium';
  return 'Low';
}
