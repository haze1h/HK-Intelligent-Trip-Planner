export interface Activity {
  activity_name: string;
  area: string;
  category: string;
  estimated_cost_hkd: number;
  duration_hours: number;
  reason: string;
}

export interface DayItinerary {
  day: number;
  notes: string;
  morning: Activity;
  afternoon: Activity;
  evening: Activity;
  daily_cost_hkd: number;
}

export interface FixedCostBreakdown {
  accommodation: number;
  food: number;
  transport: number;
  misc: number;
}

export interface BudgetContext {
  total_budget_hkd: number;
  budget_style: string;
  fixed_cost_estimate_hkd: number;
  activity_budget_hkd: number;
  fixed_cost_breakdown: FixedCostBreakdown;
  assumptions: string[];
}

export interface Itinerary {
  destination: string;
  days: number;
  activity_budget_hkd: number;
  total_estimated_activity_cost_hkd: number;
  activities_within_budget: boolean;
  itinerary: DayItinerary[];
  planning_summary: string;
  budget_context: BudgetContext;
}

export interface BudgetBreakdown {
  activities: number;
  accommodation: number;
  food: number;
  transport: number;
  misc: number;
}

export interface BudgetSummary {
  total_budget_hkd: number;
  budget_style: string;
  fixed_cost_estimate_hkd: number;
  activity_budget_hkd: number;
  activity_total_estimated_cost_hkd: number;
  total_trip_estimated_cost_hkd: number;
  activities_within_budget: boolean;
  total_trip_within_budget: boolean;
  activity_over_budget_by_hkd: number;
  total_over_budget_by_hkd: number;
  breakdown: BudgetBreakdown;
  assumptions: string[];
  suggestions: string[];
}

export interface TravelPlanResponseA {
  itinerary: Itinerary;
  budget_summary: BudgetSummary;
}

export type TravelPlanResponse = TravelPlanResponseA | Itinerary;

export interface NormalizedResponse {
  itinerary: Itinerary;
  budgetSummary: BudgetSummary | null;
}

export interface TripRequest {
  destination: string;
  days: number;
  total_budget_hkd: number;
  preferences: string[];
  pace: string;
  must_include: string[];
  avoid: string[];
  travelers: number;
  budget_style: string;
}
