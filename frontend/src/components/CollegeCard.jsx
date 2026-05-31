import { useState } from 'react';
import { getLiveCollegeDetails } from '../api';

const CHANCE = {
  HIGH:   { color: 'text-emerald-400', bg: 'bg-emerald-400/10', border: 'border-emerald-400/20', label: 'High Chance' },
  MEDIUM: { color: 'text-amber-400',   bg: 'bg-amber-400/10',   border: 'border-amber-400/20',   label: 'Medium Chance' },
  LOW:    { color: 'text-red-400',     bg: 'bg-red-400/10',     border: 'border-red-400/20',     label: 'Low Chance' },
};

export default function CollegeCard({ college, rank }) {
  const [live, setLive]         = useState(null);
  const [loading, setLoading]   = useState(false);
  const [open, setOpen]         = useState(false);
  const c = CHANCE[college.chance] || CHANCE.LOW;

  const fetchLive = async () => {
    if (live) { setOpen(o => !o); return; }
    setLoading(true); setOpen(true);
    try {
      const data = await getLiveCollegeDetails(college.collegeName, college.collegeId);
      setLive(data);
    } catch { setLive({ error: 'Search failed. Try again.' }); }
    finally { setLoading(false); }
  };

  return (
    <div className="glass-card rounded-2xl overflow-hidden group">
      <div className="p-5 relative">
        <div className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-blue-500 to-emerald-500 opacity-0 group-hover:opacity-100 transition-opacity" />
        
        {/* Rank + Chance badge */}
        <div className="flex items-start justify-between mb-3">
          <span className="text-[11px] font-bold text-[#6b7280] tracking-widest bg-[#0f172a] px-2 py-0.5 rounded border border-[#1e293b]">RANK #{rank}</span>
          <span className={`text-[11px] font-semibold px-2.5 py-1 rounded-full border ${c.bg} ${c.color} ${c.border} shadow-inner`}>
            {c.label}
          </span>
        </div>

        {/* College name */}
        <h3 className="text-[15px] font-semibold text-white leading-snug mb-1.5 line-clamp-2 group-hover:text-blue-300 transition-colors">
          {college.collegeName}
        </h3>

        {/* Branch */}
        <p className="text-[13px] text-blue-400 font-medium mb-4">{college.branchName}</p>

        {/* Stats grid */}
        <div className="grid grid-cols-3 gap-2 mb-4">
          {[
            { label: 'Match Score', value: college.totalScore },
            { label: 'Cutoff', value: `${college.closingPercentile}%` },
            { label: 'Safety', value: `+${college.safetyMargin}%` },
          ].map(({ label, value }) => (
            <div key={label} className="bg-[#0f172a] rounded-xl p-2.5 text-center border border-[#1e293b] shadow-inner">
              <p className="text-[10px] text-[#64748b] mb-1 font-medium tracking-wide">{label}</p>
              <p className="text-[13px] font-bold text-white">{value}</p>
            </div>
          ))}
        </div>

        {/* Tags: district, NAAC, hostel, fee */}
        <div className="flex flex-wrap items-center gap-2 mb-5">
          {college.district && (
            <span className="flex items-center gap-1 text-[11px] text-[#94a3b8] bg-[#0f172a] border border-[#1e293b] px-2.5 py-1 rounded-full shadow-inner">
              📍 {college.district}
            </span>
          )}
          {college.naacGrade && (
            <span className="text-[11px] text-blue-400 bg-blue-500/10 border border-blue-500/20 px-2.5 py-1 rounded-full font-medium shadow-inner shadow-blue-500/5">
              NAAC {college.naacGrade}
            </span>
          )}
          {college.hostelAvailable && (
            <span className="text-[11px] text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-1 rounded-full font-medium shadow-inner shadow-emerald-500/5">
              🏠 Hostel
            </span>
          )}
          {college.annualFee && (
            <span className="text-[11px] text-[#94a3b8] bg-[#0f172a] border border-[#1e293b] px-2.5 py-1 rounded-full shadow-inner">
              ₹{(college.annualFee / 1000).toFixed(0)}k/yr
            </span>
          )}
        </div>

        {/* Live search button */}
        <button
          onClick={fetchLive}
          disabled={loading}
          className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl border border-blue-500/30 text-blue-400 hover:bg-blue-500 hover:text-white text-[12px] font-semibold transition-all duration-300 disabled:opacity-50 cursor-pointer shadow-lg shadow-blue-500/5 hover:shadow-blue-500/25"
        >
          {loading ? (
            <>
              <span className="w-3.5 h-3.5 border-2 border-current border-t-transparent rounded-full animate-spin" />
              Searching web...
            </>
          ) : live ? (
            open ? '▲ Hide live details' : '▼ Show live details'
          ) : (
            '🔍 Get live fee & hostel'
          )}
        </button>
      </div>

      {/* Live details panel */}
      {open && (
        <div className="border-t border-[#1e293b] bg-[#030712]/50 p-5 slide-down">
          {loading && (
            <div className="flex items-center justify-center gap-2 text-[12px] text-blue-400">
              <span className="w-4 h-4 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
              Hunting down latest official links...
            </div>
          )}
          {live?.error && <p className="text-[12px] text-red-400 font-medium text-center">{live.error}</p>}
          {live && !live.error && !loading && (
            <div>
              <p className="text-[10px] text-[#64748b] font-bold uppercase tracking-widest mb-3 flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                Live Data from Web
              </p>
              
              {/* Quick Facts */}
              {live.quick_facts?.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-4">
                  {live.quick_facts.map((fact, i) => (
                    <span key={i} className="text-[11px] bg-[#0f172a] border border-[#1e293b] text-[#94a3b8] px-2.5 py-1 rounded-full shadow-inner">
                      {fact}
                    </span>
                  ))}
                </div>
              )}

              {/* Direct Links */}
              <div className="space-y-2 mb-4">
                {live.official_website && (
                  <a href={live.official_website} target="_blank" rel="noopener noreferrer"
                     className="flex items-center gap-3 w-full p-2.5 rounded-xl border border-[#1e293b] bg-[#0f172a] text-[#e2e8f0] hover:border-blue-500/50 hover:bg-blue-500/5 transition-all text-sm group/link shadow-inner">
                    <div className="bg-blue-500/10 p-1.5 rounded-lg text-blue-400 group-hover/link:bg-blue-500 group-hover/link:text-white transition-colors">🌐</div>
                    <div className="flex-1 text-[13px] font-medium">Official Website</div>
                    <div className="text-[#64748b]">↗</div>
                  </a>
                )}
                {live.fee_link && (
                  <a href={live.fee_link} target="_blank" rel="noopener noreferrer"
                     className="flex items-center gap-3 w-full p-2.5 rounded-xl border border-[#1e293b] bg-[#0f172a] text-[#e2e8f0] hover:border-emerald-500/50 hover:bg-emerald-500/5 transition-all text-sm group/link shadow-inner">
                    <div className="bg-emerald-500/10 p-1.5 rounded-lg text-emerald-400 group-hover/link:bg-emerald-500 group-hover/link:text-white transition-colors">💰</div>
                    <div className="flex-1 text-[13px] font-medium">Fee Structure</div>
                    <div className="text-[#64748b]">↗</div>
                  </a>
                )}
                {live.hostel_link && (
                  <a href={live.hostel_link} target="_blank" rel="noopener noreferrer"
                     className="flex items-center gap-3 w-full p-2.5 rounded-xl border border-[#1e293b] bg-[#0f172a] text-[#e2e8f0] hover:border-amber-500/50 hover:bg-amber-500/5 transition-all text-sm group/link shadow-inner">
                    <div className="bg-amber-500/10 p-1.5 rounded-lg text-amber-400 group-hover/link:bg-amber-500 group-hover/link:text-white transition-colors">🏠</div>
                    <div className="flex-1 text-[13px] font-medium">Hostel Info</div>
                    <div className="text-[#64748b]">↗</div>
                  </a>
                )}
                {live.placement_link && (
                  <a href={live.placement_link} target="_blank" rel="noopener noreferrer"
                     className="flex items-center gap-3 w-full p-2.5 rounded-xl border border-[#1e293b] bg-[#0f172a] text-[#e2e8f0] hover:border-purple-500/50 hover:bg-purple-500/5 transition-all text-sm group/link shadow-inner">
                    <div className="bg-purple-500/10 p-1.5 rounded-lg text-purple-400 group-hover/link:bg-purple-500 group-hover/link:text-white transition-colors">📊</div>
                    <div className="flex-1 text-[13px] font-medium">Placements</div>
                    <div className="text-[#64748b]">↗</div>
                  </a>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}