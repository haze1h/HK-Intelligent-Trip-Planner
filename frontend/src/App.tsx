import { useState, useCallback } from 'react';
import type { TripRequest, NormalizedResponse } from './types/travelPlan';
import { fetchTravelPlan, normalizeResponse } from './api/travelPlan';
import { mockResponse } from './data/mockData';
import HeroSection from './components/HeroSection';
import PlannerForm from './components/PlannerForm';
import LoadingSpinner from './components/LoadingSpinner';
import EmptyState from './components/EmptyState';
import ErrorState from './components/ErrorState';
import SummaryCards from './components/SummaryCards';
import BudgetOverview from './components/BudgetOverview';
import ItineraryTimeline from './components/ItineraryTimeline';
import PlanningSummary from './components/PlanningSummary';
import BudgetContextSection from './components/BudgetContext';

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';

export default function App() {
  const [result, setResult] = useState<NormalizedResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = useCallback(async (request: TripRequest) => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      if (USE_MOCK) {
        await new Promise((resolve) => setTimeout(resolve, 1200));
        setResult(normalizeResponse(mockResponse));
      } else {
        const data = await fetchTravelPlan(request);
        setResult(data);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleRetry = () => {
    setError(null);
  };

  const itinerary = result?.itinerary;
  const budgetSummary = result?.budgetSummary;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="relative overflow-hidden bg-gradient-to-b from-white to-gray-50 border-b border-gray-100">
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-24 -right-24 w-96 h-96 bg-teal-50 rounded-full opacity-60 blur-3xl" />
          <div className="absolute -bottom-32 -left-32 w-96 h-96 bg-cyan-50 rounded-full opacity-60 blur-3xl" />
        </div>

        <div className="relative max-w-3xl mx-auto px-4 pt-12 pb-10">
          <HeroSection />
          <div className="bg-white rounded-2xl shadow-xl shadow-gray-200/50 border border-gray-100 p-6 sm:p-8">
            <PlannerForm onSubmit={handleSubmit} isLoading={isLoading} />
          </div>
        </div>
      </div>

      <main className="max-w-5xl mx-auto px-4 py-10 space-y-8">
        {isLoading && <LoadingSpinner />}

        {error && <ErrorState message={error} onRetry={handleRetry} />}

        {!isLoading && !error && !result && <EmptyState />}

        {!isLoading && !error && result && itinerary && (
          <>
            <SummaryCards itinerary={itinerary} />

            {budgetSummary && <BudgetOverview budget={budgetSummary} />}

            <ItineraryTimeline days={itinerary.itinerary ?? []} />

            <PlanningSummary summary={itinerary.planning_summary} />

            <BudgetContextSection
              context={itinerary.budget_context}
              suggestions={budgetSummary?.suggestions}
            />
          </>
        )}
      </main>

      <footer className="border-t border-gray-100 py-6 text-center text-xs text-gray-400">
        HK Intelligent Trip Planner
      </footer>
    </div>
  );
}
