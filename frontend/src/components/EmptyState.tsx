import { Compass } from 'lucide-react';

export default function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center py-20 px-4 text-center">
      <div className="w-20 h-20 rounded-full bg-teal-50 flex items-center justify-center mb-6">
        <Compass className="w-10 h-10 text-teal-500" />
      </div>
      <h3 className="text-2xl font-semibold text-gray-800 mb-3">
        Ready to explore Hong Kong?
      </h3>
      <p className="text-gray-500 max-w-md leading-relaxed">
        Fill in your trip preferences above and let our intelligent planner craft
        the perfect itinerary for you.
      </p>
    </div>
  );
}
