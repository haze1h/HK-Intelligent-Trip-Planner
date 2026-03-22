import { Building2, Lightbulb, Info } from 'lucide-react';
import type { BudgetContext as BudgetContextType, FixedCostBreakdown } from '../types/travelPlan';

interface BudgetContextProps {
  context: BudgetContextType | null | undefined;
  suggestions?: string[] | null;
}

function FixedCosts({ breakdown }: { breakdown: FixedCostBreakdown | null | undefined }) {
  if (!breakdown) return null;

  const items = [
    { label: 'Accommodation', value: breakdown.accommodation },
    { label: 'Food', value: breakdown.food },
    { label: 'Transport', value: breakdown.transport },
    { label: 'Miscellaneous', value: breakdown.misc },
  ];

  return (
    <div className="bg-white rounded-xl border border-gray-100 p-5">
      <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
        <Building2 className="w-4 h-4 text-teal-500" />
        Fixed Cost Breakdown
      </h3>
      <div className="grid grid-cols-2 gap-3">
        {items.map((item) => (
          <div key={item.label} className="flex justify-between items-center py-2 px-3 bg-gray-50 rounded-lg">
            <span className="text-sm text-gray-600">{item.label}</span>
            <span className="text-sm font-semibold text-gray-800">
              {item.value != null ? `HK$${item.value.toLocaleString()}` : 'N/A'}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

function BulletList({
  title,
  items,
  icon: Icon,
}: {
  title: string;
  items: string[] | null | undefined;
  icon: typeof Info;
}) {
  if (!items || items.length === 0) return null;

  return (
    <div className="bg-white rounded-xl border border-gray-100 p-5">
      <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
        <Icon className="w-4 h-4 text-teal-500" />
        {title}
      </h3>
      <ul className="space-y-2">
        {items.map((item, i) => (
          <li key={i} className="flex gap-2 text-sm text-gray-600 leading-relaxed">
            <span className="w-1.5 h-1.5 rounded-full bg-teal-400 mt-2 flex-shrink-0" />
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function BudgetContextSection({ context, suggestions }: BudgetContextProps) {
  if (!context && (!suggestions || suggestions.length === 0)) return null;

  return (
    <section>
      <h2 className="text-xl font-bold text-gray-800 mb-4">Additional Details</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <FixedCosts breakdown={context?.fixed_cost_breakdown} />
        <BulletList
          title="Assumptions"
          items={context?.assumptions}
          icon={Info}
        />
        <BulletList
          title="Suggestions"
          items={suggestions}
          icon={Lightbulb}
        />
      </div>
    </section>
  );
}
