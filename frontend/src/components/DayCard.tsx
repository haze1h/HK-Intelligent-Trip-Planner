import { DollarSign } from 'lucide-react';
import type { DayItinerary } from '../types/travelPlan';
import ActivityCard from './ActivityCard';

interface DayCardProps {
  day: DayItinerary;
}

export default function DayCard({ day }: DayCardProps) {
  return (
    <div className="bg-white rounded-xl border border-gray-100 overflow-hidden hover:shadow-lg transition-shadow">
      <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100 bg-gray-50/50">
        <div className="flex items-center gap-3">
          <span className="w-10 h-10 rounded-full bg-teal-600 text-white flex items-center justify-center font-bold text-sm">
            {day?.day ?? '?'}
          </span>
          <div>
            <h3 className="font-bold text-gray-800">Day {day?.day ?? '?'}</h3>
            {day?.notes && (
              <p className="text-xs text-gray-500 mt-0.5">{day.notes}</p>
            )}
          </div>
        </div>
        <div className="flex items-center gap-1 px-3 py-1.5 bg-teal-50 rounded-lg">
          <DollarSign className="w-4 h-4 text-teal-600" />
          <span className="text-sm font-bold text-teal-700">
            {day?.daily_cost_hkd != null ? `HK$${day.daily_cost_hkd.toLocaleString()}` : 'N/A'}
          </span>
        </div>
      </div>

      <div className="p-5 space-y-3">
        <ActivityCard activity={day?.morning} timeSlot="Morning" />
        <ActivityCard activity={day?.afternoon} timeSlot="Afternoon" />
        <ActivityCard activity={day?.evening} timeSlot="Evening" />
      </div>
    </div>
  );
}
