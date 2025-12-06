import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, ArrowRight } from 'lucide-react';

const TOP_MOVERS = [
  { id: 1, name: "Bitcoin > $100k", change: 0.12, price: 0.42, direction: 'up' },
  { id: 2, name: "Fed Rate Cut Q2", change: -0.08, price: 0.55, direction: 'down' },
  { id: 3, name: "GOP Nominee", change: 0.05, price: 0.88, direction: 'up' },
];

export default function DashboardSnippet() {
  return (
    <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-4">
      <h3 className="text-sm font-semibold text-zinc-400 mb-3 uppercase tracking-wider">
        Biggest Movers (24h)
      </h3>
      <div className="space-y-3">
        {TOP_MOVERS.map((mover) => (
          <div key={mover.id} className="flex items-center justify-between group cursor-pointer">
            <div className="flex flex-col">
              <span className="font-medium text-zinc-200 text-sm group-hover:text-blue-400 transition-colors">
                {mover.name}
              </span>
              <span className="text-xs text-zinc-500">
                Current: {(mover.price * 100).toFixed(0)}%
              </span>
            </div>
            <div className={`flex items-center gap-1 text-sm font-bold ${
              mover.direction === 'up' ? 'text-green-400' : 'text-red-400'
            }`}>
              {mover.direction === 'up' ? '+' : ''}{(mover.change * 100).toFixed(0)}%
              {mover.direction === 'up' ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
            </div>
          </div>
        ))}
      </div>
      <button className="w-full mt-4 py-2 text-xs font-medium text-zinc-400 hover:text-white bg-zinc-800/50 hover:bg-zinc-800 rounded transition-colors flex items-center justify-center gap-1">
        View All Movers <ArrowRight className="w-3 h-3" />
      </button>
    </div>
  );
}
