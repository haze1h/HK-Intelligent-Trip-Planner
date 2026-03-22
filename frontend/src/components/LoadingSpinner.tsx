import { Loader2 } from 'lucide-react';

export default function LoadingSpinner() {
  return (
    <div className="flex flex-col items-center justify-center py-20 px-4">
      <Loader2 className="w-12 h-12 text-teal-500 animate-spin mb-5" />
      <p className="text-gray-600 font-medium text-lg">
        Crafting your perfect itinerary...
      </p>
      <p className="text-gray-400 text-sm mt-2">
        This may take a moment
      </p>
    </div>
  );
}
