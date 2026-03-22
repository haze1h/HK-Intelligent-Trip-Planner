import { Map } from 'lucide-react';
import type { DayItinerary } from '../types/travelPlan';
import DayCard from './DayCard';

interface ItineraryTimelineProps {
  days: DayItinerary[];
}

export default function ItineraryTimeline({ days }: ItineraryTimelineProps) {
  if (!days || days.length === 0) {
    return null;
  }

  return (
    <section>
      <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
        <Map className="w-5 h-5 text-teal-600" />
        Your Itinerary
      </h2>
      <div className="space-y-4">
        {days.map((day, i) => (
          <DayCard key={day?.day ?? i} day={day} />
        ))}
      </div>
    </section>
  );
}
