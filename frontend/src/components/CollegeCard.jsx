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
    <div className="rounded-2xl border border-[#374151] bg-[#111827] overflow-hidden hover:border-blue-500/40 transition-all duration-300 fade-in group hover:shadow-lg hover:shadow-blue-500/5">
      <div className="p-5">
        {/* Rank + Chance badge */}
        <div className="flex items-start justify-between mb-3">
          <span className="text-[11px] font-bold text-[#6b7280] tracking-widest">RANK #{rank}</span>
          <span className={`text-[11px] font-semibold px-2.5 py-1 rounded-full border ${c.bg} ${c.color} ${c.border}`}>
            {c.label}
          </span>
        </div>

        {/* College name */}
        <h3 className="text-[14px] font-semibold text-white leading-snug mb-1.5 line-clamp-2 group-hover:text-blue-200 transition-colors">
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
            <div key={label} className="bg-[#0a0e1a] rounded-xl p-2.5 text-center border border-[#1f2937]">
              <p className="text-[10px] text-[#6b7280] mb-1 font-medium">{label}</p>
              <p className="text-[13px] font-bold text-white">{value}</p>
            </div>
          ))}
        </div>

        {/* Tags: district, NAAC, hostel, fee */}
        <div className="flex flex-wrap items-center gap-2 mb-4">
          {college.district && (
            <span className="flex items-center gap-1 text-[11px] text-[#9ca3af] bg-[#1f2937] px-2.5 py-1 rounded-full">
              📍 {college.district}
            </span>
          )}
          {college.naacGrade && (
            <span className="text-[11px] text-blue-400 bg-blue-400/10 border border-blue-400/20 px-2.5 py-1 rounded-full font-medium">
              NAAC {college.naacGrade}
            </span>
          )}
          {college.hostelAvailable && (
            <span className="text-[11px] text-emerald-400 bg-emerald-400/10 border border-emerald-400/20 px-2.5 py-1 rounded-full">
              🏠 Hostel
            </span>
          )}
          {college.annualFee && (
            <span className="text-[11px] text-[#9ca3af] bg-[#1f2937] px-2.5 py-1 rounded-full">
              ₹{(college.annualFee / 1000).toFixed(0)}k/yr
            </span>
          )}
        </div>

        {/* Live search button */}
        <button
          onClick={fetchLive}
          disabled={loading}
          className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl border border-blue-500/30 text-blue-400 hover:bg-blue-500/10 text-[12px] font-medium transition-all duration-200 disabled:opacity-50 cursor-pointer hover:border-blue-500/60"
        >
          {loading ? (
            <>
              <span className="w-3.5 h-3.5 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
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
        <div className="border-t border-[#374151] bg-[#0a0e1a] p-5 slide-down">
          {loading && (
            <div className="flex items-center gap-2 text-[12px] text-[#9ca3af]">
              <span className="w-3 h-3 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
              Searching official website...
            </div>
          )}
          {live?.error && <p className="text-[12px] text-red-400">{live.error}</p>}
          {live && !live.error && !loading && (
            <div>
              <p className="text-[11px] text-[#6b7280] font-semibold uppercase tracking-wider mb-3">
                Live Data from Web
              </p>
              
              {/* Quick Facts */}
              {live.quick_facts?.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-4">
                  {live.quick_facts.map((fact, i) => (
                    <span key={i} className="text-[11px] bg-[#1f2937] border border-[#374151] text-[#9ca3af] px-2.5 py-1 rounded-full">
                      {fact}
                    </span>
                  ))}
                </div>
              )}

              {/* Direct Links */}
              <div className="space-y-2 mb-4">
                {live.official_website && (
                  <a href={live.official_website} target="_blank" rel="noopener noreferrer"
                     className="flex items-center gap-2 w-full py-2.5 px-3 rounded-xl border border-[#374151] text-[#9ca3af] hover:text-white hover:border-blue-500/40 hover:bg-[#1f2937] text-[12px] transition-all">
                    🌐 Official Website
                    <span className="ml-auto text-[10px] text-[#6b7280]">↗</span>
                  </a>
                )}
                {live.fee_link && (
                  <a href={live.fee_link} target="_blank" rel="noopener noreferrer"
                     className="flex items-center gap-2 w-full py-2.5 px-3 rounded-xl border border-[#374151] text-[#9ca3af] hover:text-white hover:border-blue-500/40 hover:bg-[#1f2937] text-[12px] transition-all">
                    💰 Fee Structure
                    <span className="ml-auto text-[10px] text-[#6b7280]">↗</span>
                  </a>
                )}
                {live.hostel_link && (
                  <a href={live.hostel_link} target="_blank" rel="noopener noreferrer"
                     className="flex items-center gap-2 w-full py-2.5 px-3 rounded-xl border border-[#374151] text-[#9ca3af] hover:text-white hover:border-blue-500/40 hover:bg-[#1f2937] text-[12px] transition-all">
                    🏠 Hostel Info
                    <span className="ml-auto text-[10px] text-[#6b7280]">↗</span>
                  </a>
                )}
                {live.placement_link && (
                  <a href={live.placement_link} target="_blank" rel="noopener noreferrer"
                     className="flex items-center gap-2 w-full py-2.5 px-3 rounded-xl border border-[#374151] text-[#9ca3af] hover:text-white hover:border-blue-500/40 hover:bg-[#1f2937] text-[12px] transition-all">
                    📊 Placements
                    <span className="ml-auto text-[10px] text-[#6b7280]">↗</span>
                  </a>
                )}
              </div>

              <p className="text-[10px] text-[#6b7280] mt-3 text-center">
                Links open official college websites. Verify fees directly with the institution.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}