import { useState } from 'react';
import { Send, Plus, X } from 'lucide-react';
import type { TripRequest } from '../types/travelPlan';

interface PlannerFormProps {
  onSubmit: (request: TripRequest) => void;
  isLoading: boolean;
}

const PACE_OPTIONS = [
  { label: 'Relaxed', value: 'relaxed' },
  { label: 'Moderate', value: 'moderate' },
  { label: 'Packed', value: 'packed' },
];

const BUDGET_STYLE_OPTIONS = [
  { label: 'Budget', value: 'budget' },
  { label: 'Standard', value: 'standard' },
  { label: 'Premium', value: 'premium' },
  { label: 'Luxury', value: 'luxury' },
];

const PREFERENCE_SUGGESTIONS = [
  'Nature',
  'Culture',
  'Food',
  'Shopping',
  'Nightlife',
  'History',
  'Adventure',
  'Photography',
];

function TagInput({
  label,
  tags,
  onAdd,
  onRemove,
  placeholder,
  suggestions,
}: {
  label: string;
  tags: string[];
  onAdd: (tag: string) => void;
  onRemove: (index: number) => void;
  placeholder: string;
  suggestions?: string[];
}) {
  const [input, setInput] = useState('');

  const handleAdd = () => {
    const trimmed = input.trim();
    if (trimmed && !tags.includes(trimmed)) {
      onAdd(trimmed);
      setInput('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAdd();
    }
  };

  const availableSuggestions = suggestions?.filter((s) => !tags.includes(s));

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1.5">
        {label}
      </label>
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm
                     focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent
                     bg-white placeholder:text-gray-400"
        />
        <button
          type="button"
          onClick={handleAdd}
          className="px-3 py-2 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200
                     transition-colors flex items-center gap-1 text-sm"
        >
          <Plus className="w-4 h-4" />
        </button>
      </div>
      {tags.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mt-2">
          {tags.map((tag, i) => (
            <span
              key={i}
              className="inline-flex items-center gap-1 px-2.5 py-1 bg-teal-50 text-teal-700
                         rounded-full text-xs font-medium"
            >
              {tag}
              <button
                type="button"
                onClick={() => onRemove(i)}
                className="hover:text-teal-900 transition-colors"
              >
                <X className="w-3 h-3" />
              </button>
            </span>
          ))}
        </div>
      )}
      {availableSuggestions && availableSuggestions.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-2">
          {availableSuggestions.map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => onAdd(s)}
              className="px-2 py-0.5 text-xs text-gray-500 border border-gray-200 rounded-full
                         hover:border-teal-300 hover:text-teal-600 hover:bg-teal-50
                         transition-colors"
            >
              + {s}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export default function PlannerForm({ onSubmit, isLoading }: PlannerFormProps) {
  const [destination, setDestination] = useState('Hong Kong');
  const [days, setDays] = useState(2);
  const [totalBudget, setTotalBudget] = useState(6000);
  const [preferences, setPreferences] = useState<string[]>([]);
  const [pace, setPace] = useState('moderate');
  const [mustInclude, setMustInclude] = useState<string[]>([]);
  const [avoid, setAvoid] = useState<string[]>([]);
  const [travelers, setTravelers] = useState(1);
  const [budgetStyle, setBudgetStyle] = useState('standard');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      destination,
      days,
      total_budget_hkd: totalBudget,
      preferences,
      pace,
      must_include: mustInclude,
      avoid,
      travelers,
      budget_style: budgetStyle,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">
            Destination
          </label>
          <input
            type="text"
            value={destination}
            onChange={(e) => setDestination(e.target.value)}
            required
            className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm
                       focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent
                       bg-white"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">
            Number of Days
          </label>
          <input
            type="number"
            min={1}
            max={30}
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
            required
            className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm
                       focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent
                       bg-white"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">
            Total Budget (HKD)
          </label>
          <input
            type="number"
            min={0}
            step={100}
            value={totalBudget}
            onChange={(e) => setTotalBudget(Number(e.target.value))}
            required
            className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm
                       focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent
                       bg-white"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">
            Travelers
          </label>
          <input
            type="number"
            min={1}
            max={20}
            value={travelers}
            onChange={(e) => setTravelers(Number(e.target.value))}
            required
            className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm
                       focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent
                       bg-white"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">
            Budget Style
          </label>
          <select
            value={budgetStyle}
            onChange={(e) => setBudgetStyle(e.target.value)}
            className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm
                       focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent
                       bg-white"
          >
            {BUDGET_STYLE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Pace
        </label>
        <div className="flex gap-2">
          {PACE_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              type="button"
              onClick={() => setPace(opt.value)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all
                ${
                  pace === opt.value
                    ? 'bg-teal-600 text-white shadow-sm'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      <TagInput
        label="Preferences"
        tags={preferences}
        onAdd={(t) => setPreferences([...preferences, t])}
        onRemove={(i) => setPreferences(preferences.filter((_, idx) => idx !== i))}
        placeholder="e.g. Nature, Food, Culture..."
        suggestions={PREFERENCE_SUGGESTIONS}
      />

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <TagInput
          label="Must Include"
          tags={mustInclude}
          onAdd={(t) => setMustInclude([...mustInclude, t])}
          onRemove={(i) => setMustInclude(mustInclude.filter((_, idx) => idx !== i))}
          placeholder="e.g. Victoria Peak"
        />
        <TagInput
          label="Avoid"
          tags={avoid}
          onAdd={(t) => setAvoid([...avoid, t])}
          onRemove={(i) => setAvoid(avoid.filter((_, idx) => idx !== i))}
          placeholder="e.g. Crowded malls"
        />
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full py-3 bg-teal-600 text-white rounded-xl font-semibold text-base
                   hover:bg-teal-700 transition-all focus:outline-none focus:ring-2
                   focus:ring-teal-500 focus:ring-offset-2 disabled:opacity-60
                   disabled:cursor-not-allowed flex items-center justify-center gap-2
                   shadow-lg shadow-teal-600/20 hover:shadow-teal-600/30"
      >
        {isLoading ? (
          <>
            <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            Planning...
          </>
        ) : (
          <>
            <Send className="w-5 h-5" />
            Plan My Trip
          </>
        )}
      </button>
    </form>
  );
}
