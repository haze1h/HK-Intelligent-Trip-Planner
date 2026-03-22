import { Clock, MapPin, DollarSign } from 'lucide-react';
import type { Activity } from '../types/travelPlan';

interface ActivityCardProps {
  activity: Activity | null | undefined;
  timeSlot: string;
}

const TIME_SLOT_STYLES: Record<string, { bg: string; accent: string; icon: string }> = {
  Morning: { bg: 'bg-amber-50', accent: 'border-amber-200', icon: 'text-amber-500' },
  Afternoon: { bg: 'bg-sky-50', accent: 'border-sky-200', icon: 'text-sky-500' },
  Evening: { bg: 'bg-slate-50', accent: 'border-slate-300', icon: 'text-slate-500' },
};

export default function ActivityCard({ activity, timeSlot }: ActivityCardProps) {
  const styles = TIME_SLOT_STYLES[timeSlot] || TIME_SLOT_STYLES.Morning;

  if (!activity) {
    return (
      <div className={`rounded-lg border ${styles.accent} ${styles.bg} p-4 opacity-60`}>
        <span className="text-xs font-semibold uppercase tracking-wider text-gray-400">
          {timeSlot}
        </span>
        <p className="text-sm text-gray-400 mt-1">No activity planned</p>
      </div>
    );
  }

  return (
    <div
      className={`rounded-lg border ${styles.accent} ${styles.bg} p-4
                  hover:shadow-md transition-all group`}
    >
      <div className="flex items-center justify-between mb-2">
        <span className={`text-xs font-semibold uppercase tracking-wider ${styles.icon}`}>
          {timeSlot}
        </span>
        {activity.category && (
          <span className="px-2 py-0.5 rounded-full bg-white/80 text-xs font-medium text-gray-600 border border-gray-200">
            {activity.category}
          </span>
        )}
      </div>

      <h4 className="font-semibold text-gray-800 mb-2 group-hover:text-teal-700 transition-colors">
        {activity.activity_name || 'N/A'}
      </h4>

      <div className="flex flex-wrap gap-3 text-xs text-gray-500 mb-3">
        {activity.area && (
          <span className="flex items-center gap-1">
            <MapPin className="w-3.5 h-3.5" />
            {activity.area}
          </span>
        )}
        {activity.duration_hours != null && (
          <span className="flex items-center gap-1">
            <Clock className="w-3.5 h-3.5" />
            {activity.duration_hours}h
          </span>
        )}
        <span className="flex items-center gap-1">
          <DollarSign className="w-3.5 h-3.5" />
          {activity.estimated_cost_hkd != null
            ? activity.estimated_cost_hkd === 0
              ? 'Free'
              : `HK$${activity.estimated_cost_hkd.toLocaleString()}`
            : 'N/A'}
        </span>
      </div>

      {activity.reason && (
        <p className="text-xs text-gray-500 leading-relaxed italic">
          {activity.reason}
        </p>
      )}
    </div>
  );
}
