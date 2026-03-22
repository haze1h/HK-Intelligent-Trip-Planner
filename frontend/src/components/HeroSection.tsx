import { Navigation } from 'lucide-react';

export default function HeroSection() {
  return (
    <div className="text-center mb-8">
      <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-teal-50 rounded-full text-teal-700 text-sm font-medium mb-4">
        <Navigation className="w-4 h-4" />
        AI-Powered Travel Planning
      </div>
      <h1 className="text-4xl sm:text-5xl font-extrabold text-gray-900 tracking-tight mb-3">
        HK Intelligent
        <span className="block text-teal-600">Trip Planner</span>
      </h1>
      <p className="text-gray-500 text-lg max-w-lg mx-auto leading-relaxed">
        Discover the best of Hong Kong with a personalized itinerary
        crafted to fit your budget, pace, and interests.
      </p>
    </div>
  );
}
