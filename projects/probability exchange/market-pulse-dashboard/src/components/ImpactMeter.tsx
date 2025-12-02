interface Impact {
  score: number;  // 0 to 1
  confidence: number;  // 0 to 1
  predicted_direction: 'up' | 'down' | 'neutral';
}

interface ImpactMeterProps {
  impact: Impact;
}

export default function ImpactMeter({ impact }: ImpactMeterProps) {
  const directionSymbols = {
    up: '↑',
    down: '↓',
    neutral: '→',
  };

  const directionColors = {
    up: 'text-green-400',
    down: 'text-red-400',
    neutral: 'text-yellow-400',
  };

  const impactPercent = impact.score * 100;
  const confidencePercent = impact.confidence * 100;

  // Determine impact level label
  let impactLabel = 'Low';
  let impactColor = 'text-zinc-400';
  if (impactPercent > 70) {
    impactLabel = 'High';
    impactColor = 'text-red-400';
  } else if (impactPercent > 40) {
    impactLabel = 'Medium';
    impactColor = 'text-yellow-400';
  }

  return (
    <div className="flex items-center gap-3 group relative">
      {/* Impact Score */}
      <div className="flex items-center gap-1.5">
        <span className={`text-2xl font-bold ${directionColors[impact.predicted_direction]}`}>
          {directionSymbols[impact.predicted_direction]}
        </span>
        <div className="text-right">
          <div className={`text-xs font-semibold ${impactColor}`}>{impactLabel}</div>
          <div className="text-[10px] text-zinc-500">{impactPercent.toFixed(0)}%</div>
        </div>
      </div>

      {/* Tooltip on hover */}
      <div className="absolute bottom-full right-0 mb-2 px-3 py-2 bg-zinc-800 border border-zinc-700 rounded text-xs opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity whitespace-nowrap z-10">
        <div className="space-y-1">
          <div className="flex justify-between gap-4">
            <span className="text-zinc-400">Impact:</span>
            <span className="text-white font-semibold">{impactPercent.toFixed(1)}%</span>
          </div>
          <div className="flex justify-between gap-4">
            <span className="text-zinc-400">Confidence:</span>
            <span className="text-white font-semibold">{confidencePercent.toFixed(1)}%</span>
          </div>
          <div className="flex justify-between gap-4">
            <span className="text-zinc-400">Direction:</span>
            <span className={`font-semibold ${directionColors[impact.predicted_direction]}`}>
              {impact.predicted_direction.toUpperCase()} {directionSymbols[impact.predicted_direction]}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
