import { Sparkles } from 'lucide-react';

interface PlanningSummaryProps {
  summary: string | null | undefined;
}

export default function PlanningSummary({ summary }: PlanningSummaryProps) {
  if (!summary) return null;

  return (
    <section>
      <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
        <Sparkles className="w-5 h-5 text-teal-600" />
        Planning Summary
      </h2>
      <div className="bg-gradient-to-br from-teal-50 to-cyan-50 rounded-xl border border-teal-100 p-6">
        <p className="text-gray-700 leading-relaxed">{summary}</p>
      </div>
    </section>
  );
}
