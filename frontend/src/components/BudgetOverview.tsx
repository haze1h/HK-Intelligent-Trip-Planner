import { PieChart, TrendingUp, TrendingDown, DollarSign } from 'lucide-react';
import type { BudgetSummary } from '../types/travelPlan';

interface BudgetOverviewProps {
  budget: BudgetSummary;
}

function formatHKD(val: number | null | undefined): string {
  if (val == null) return 'N/A';
  return `HK$${val.toLocaleString()}`;
}

function BudgetBadge({ withinBudget }: { withinBudget: boolean | null | undefined }) {
  if (withinBudget == null) {
    return <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-gray-100 text-gray-600">N/A</span>;
  }
  return withinBudget ? (
    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-700">
      <TrendingDown className="w-3 h-3" />
      Within Budget
    </span>
  ) : (
    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-red-100 text-red-700">
      <TrendingUp className="w-3 h-3" />
      Over Budget
    </span>
  );
}

export default function BudgetOverview({ budget }: BudgetOverviewProps) {
  const breakdown = budget?.breakdown;
  const breakdownEntries = breakdown
    ? Object.entries(breakdown).map(([key, val]) => ({
        label: key.charAt(0).toUpperCase() + key.slice(1),
        value: val as number,
      }))
    : [];

  const totalBreakdown = breakdownEntries.reduce((sum, e) => sum + (e.value || 0), 0);

  const barColors = [
    'bg-teal-500',
    'bg-blue-500',
    'bg-amber-500',
    'bg-cyan-500',
    'bg-rose-400',
  ];

  return (
    <section>
      <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
        <PieChart className="w-5 h-5 text-teal-600" />
        Budget Overview
      </h2>

      <div className="bg-white rounded-xl border border-gray-100 overflow-hidden">
        <div className="grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-gray-100">
          <div className="p-5 space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-500">Total Budget</span>
              <span className="text-sm font-bold text-gray-800">{formatHKD(budget?.total_budget_hkd)}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-500">Fixed Cost Estimate</span>
              <span className="text-sm font-semibold text-gray-700">{formatHKD(budget?.fixed_cost_estimate_hkd)}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-500">Activity Budget</span>
              <span className="text-sm font-semibold text-gray-700">{formatHKD(budget?.activity_budget_hkd)}</span>
            </div>
            <div className="h-px bg-gray-100" />
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-500">Est. Trip Cost</span>
              <span className="text-sm font-bold text-gray-800">{formatHKD(budget?.total_trip_estimated_cost_hkd)}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-500">Activities Within Budget</span>
              <BudgetBadge withinBudget={budget?.activities_within_budget} />
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-500">Total Trip Within Budget</span>
              <BudgetBadge withinBudget={budget?.total_trip_within_budget} />
            </div>
            {(budget?.activity_over_budget_by_hkd ?? 0) > 0 && (
              <div className="flex justify-between items-center">
                <span className="text-sm text-red-500">Activity Over By</span>
                <span className="text-sm font-semibold text-red-600">
                  {formatHKD(budget.activity_over_budget_by_hkd)}
                </span>
              </div>
            )}
            {(budget?.total_over_budget_by_hkd ?? 0) > 0 && (
              <div className="flex justify-between items-center">
                <span className="text-sm text-red-500">Total Over By</span>
                <span className="text-sm font-semibold text-red-600">
                  {formatHKD(budget.total_over_budget_by_hkd)}
                </span>
              </div>
            )}
          </div>

          <div className="p-5">
            <p className="text-sm font-medium text-gray-700 mb-3 flex items-center gap-1.5">
              <DollarSign className="w-4 h-4 text-teal-500" />
              Cost Breakdown
            </p>
            {breakdownEntries.length > 0 ? (
              <div className="space-y-2.5">
                {breakdownEntries.map((entry, idx) => {
                  const pct = totalBreakdown > 0 ? (entry.value / totalBreakdown) * 100 : 0;
                  return (
                    <div key={entry.label}>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-600">{entry.label}</span>
                        <span className="font-medium text-gray-800">{formatHKD(entry.value)}</span>
                      </div>
                      <div className="w-full bg-gray-100 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${barColors[idx % barColors.length]} transition-all duration-500`}
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="text-sm text-gray-400">No breakdown available</p>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
