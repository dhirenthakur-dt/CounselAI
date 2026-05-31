const CHANCE_STYLE = {
  HIGH:   { bg: 'bg-emerald-500/10', text: 'text-emerald-400', border: 'border-emerald-500/30', dot: 'bg-emerald-400' },
  MEDIUM: { bg: 'bg-amber-500/10',   text: 'text-amber-400',   border: 'border-amber-500/30',   dot: 'bg-amber-400' },
  LOW:    { bg: 'bg-red-500/10',     text: 'text-red-400',     border: 'border-red-500/30',     dot: 'bg-red-400' },
};

export default function CollegeCard({ college, rank }) {
  const s = CHANCE_STYLE[college.chance] || CHANCE_STYLE.LOW;

  return (
    <div className="bg-[#1a1f2e] border border-[#2d3748] rounded-xl p-4 hover:border-blue-500/40 transition-all duration-200">

      {/* Top row */}
      <div className="flex items-start justify-between gap-2 mb-2">
        <span className="text-[10px] font-bold text-gray-500 tracking-widest uppercase">
          #{rank}
        </span>
        <span className={`flex items-center gap-1.5 text-[11px] font-semibold px-2 py-0.5 rounded-full border ${s.bg} ${s.text} ${s.border}`}>
          <span className={`w-1.5 h-1.5 rounded-full ${s.dot}`}/>
          {college.chance}
        </span>
      </div>

      {/* College name */}
      <p className="text-[13px] font-semibold text-gray-100 leading-snug mb-1 line-clamp-2">
        {college.collegeName}
      </p>

      {/* Branch */}
      <p className="text-[12px] text-blue-400 font-medium mb-3">
        {college.branchName}
      </p>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-2">
        {[
          { label: 'Score',   value: college.totalScore },
          { label: 'Cutoff',  value: `${college.closingPercentile}%` },
          { label: 'Safety',  value: `+${college.safetyMargin}` },
        ].map(({ label, value }) => (
          <div key={label} className="bg-[#0f1117] rounded-lg p-2 text-center">
            <p className="text-[10px] text-gray-500 mb-0.5">{label}</p>
            <p className="text-[12px] font-bold text-gray-200">{value}</p>
          </div>
        ))}
      </div>

      {/* District + hostel */}
      <div className="flex items-center gap-3 mt-2.5">
        {college.district && (
          <span className="text-[11px] text-gray-500 flex items-center gap-1">
            📍 {college.district}
          </span>
        )}
        {college.hostelAvailable && (
          <span className="text-[11px] text-emerald-500">🏠 Hostel</span>
        )}
        {college.annualFee && (
          <span className="text-[11px] text-gray-500">
            ₹{(college.annualFee/1000).toFixed(0)}k/yr
          </span>
        )}
      </div>
    </div>
  );
}