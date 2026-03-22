import type {
  TripRequest,
  TravelPlanResponse,
  NormalizedResponse,
  Itinerary,
  TravelPlanResponseA,
} from '../types/travelPlan';

export const API_URL = import.meta.env.VITE_API_URL || '/api/travel-plan';

function isResponseA(data: TravelPlanResponse): data is TravelPlanResponseA {
  return 'itinerary' in data && 'budget_summary' in data;
}

function isItinerary(data: TravelPlanResponse): data is Itinerary {
  return 'itinerary' in data && 'planning_summary' in data && !('budget_summary' in data);
}

export function normalizeResponse(data: TravelPlanResponse): NormalizedResponse {
  if (isResponseA(data)) {
    return {
      itinerary: data.itinerary,
      budgetSummary: data.budget_summary,
    };
  }

  if (isItinerary(data)) {
    return {
      itinerary: data,
      budgetSummary: null,
    };
  }

  return {
    itinerary: data as Itinerary,
    budgetSummary: null,
  };
}

export async function fetchTravelPlan(request: TripRequest): Promise<NormalizedResponse> {
  const response = await fetch(API_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;
    try {
      const errorData = await response.json();
      if (typeof errorData?.detail === 'string' && errorData.detail.trim()) {
        message = errorData.detail;
      }
    } catch {
      // ignore non-JSON error bodies
    }
    throw new Error(message);
  }

  const data: TravelPlanResponse = await response.json();
  return normalizeResponse(data);
}
