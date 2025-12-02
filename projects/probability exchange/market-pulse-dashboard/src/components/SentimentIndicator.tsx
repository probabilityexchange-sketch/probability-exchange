interface Sentiment {
  score: number;  // -1 to 1
  label: 'positive' | 'negative' | 'neutral';
}

interface SentimentIndicatorProps {
  sentiment: Sentiment;
}

export default function SentimentIndicator({ sentiment }: SentimentIndicatorProps) {
  const colors = {
    positive: {
      bg: 'bg-green-500/10',
      text: 'text-green-400',
      border: 'border-green-500/30',
      dot: 'bg-green-500',
    },
    negative: {
      bg: 'bg-red-500/10',
      text: 'text-red-400',
      border: 'border-red-500/30',
      dot: 'bg-red-500',
    },
    neutral: {
      bg: 'bg-yellow-500/10',
      text: 'text-yellow-400',
      border: 'border-yellow-500/30',
      dot: 'bg-yellow-500',
    },
  };

  const { bg, text, border, dot } = colors[sentiment.label];
  const scorePercent = Math.abs(sentiment.score) * 100;

  return (
    <div
      className={`px-3 py-1.5 rounded-lg border ${bg} ${border} flex items-center gap-2 group relative`}
      title={`Sentiment score: ${sentiment.score.toFixed(2)}`}
    >
      <div className={`w-2 h-2 rounded-full ${dot} animate-pulse`} />
      <span className={`text-xs font-semibold uppercase tracking-wide ${text}`}>
        {sentiment.label}
      </span>

      {/* Tooltip on hover */}
      <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-1 bg-zinc-800 border border-zinc-700 rounded text-xs whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity">
        Score: {sentiment.score.toFixed(2)} ({scorePercent.toFixed(0)}%)
      </div>
    </div>
  );
}
