import { MapPin, Calendar, Wallet, Receipt, CheckCircle2, XCircle } from 'lucide-react';
import type { Itinerary } from '../types/travelPlan';

interface SummaryCardsProps {
  itinerary: Itinerary;
}

function safe(val: unknown, fallback = 'N/A'): string {
  if (val === null || val === undefined) return fallback;
  return String(val);
}

export default function SummaryCards({ itinerary }: SummaryCardsProps) {
  const withinBudget = itinerary?.activities_within_budget;

  const cards = [
    {
      icon: MapPin,
      label: 'Destination',
      value: safe(itinerary?.destination),
      color: 'bg-blue-50 text-blue-600',
    },
    {
      icon: Calendar,
      label: 'Days',
      value: safe(itinerary?.days),
      color: 'bg-amber-50 text-amber-600',
    },
    {
      icon: Wallet,
      label: 'Activity Budget',
      value: itinerary?.activity_budget_hkd != null
        ? `HK$${itinerary.activity_budget_hkd.toLocaleString()}`
        : 'N/A',
      color: 'bg-teal-50 text-teal-600',
    },
    {
      icon: Receipt,
      label: 'Est. Activity Cost',
      value: itinerary?.total_estimated_activity_cost_hkd != null
        ? `HK$${itinerary.total_estimated_activity_cost_hkd.toLocaleString()}`
        : 'N/A',
      color: 'bg-cyan-50 text-cyan-600',
    },
    {
      icon: withinBudget ? CheckCircle2 : XCircle,
      label: 'Budget Status',
      value: withinBudget == null ? 'N/A' : withinBudget ? 'Within Budget' : 'Over Budget',
      color: withinBudget == null
        ? 'bg-gray-50 text-gray-600'
        : withinBudget
          ? 'bg-emerald-50 text-emerald-600'
          : 'bg-red-50 text-red-600',
    },
  ];

  return (
    <section>
      <h2 className="text-xl font-bold text-gray-800 mb-4">Trip Summary</h2>
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
        {cards.map((card) => (
          <div
            key={card.label}
            className="bg-white rounded-xl border border-gray-100 p-4 hover:shadow-md
                       transition-shadow"
          >
            <div className={`w-10 h-10 rounded-lg ${card.color} flex items-center justify-center mb-3`}>
              <card.icon className="w-5 h-5" />
            </div>
            <p className="text-xs text-gray-500 font-medium uppercase tracking-wide mb-1">
              {card.label}
            </p>
            <p className="text-lg font-bold text-gray-800">{card.value}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
