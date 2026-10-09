import { useState, useEffect } from 'react';
import { searchColleges, getDistricts, getCollegesByDistrict, getCollegeCutoffs, getLiveCollegeDetails } from '../api';

const NAAC_SCORES = { 'A++': 7, 'A+': 6, 'A': 5, 'B++': 4, 'B+': 3, 'B': 2, 'C': 1 };

const CollegeCutoffViewer = ({ data }) => {
  const branches = [...new Set(data.map(c => c.branch?.branchName || 'General'))].sort();
  const [activeBranch, setActiveBranch] = useState(branches[0]);

  const branchData = data.filter(c => (c.branch?.branchName || 'General') === activeBranch);

  const years = [...new Set(branchData.map(c => c.year))].sort((a,b) => b - a);
  const [activeYear, setActiveYear] = useState(years[0] || 2024);
  
  useEffect(() => {
    const newYears = [...new Set(data.filter(c => (c.branch?.branchName || 'General') === activeBranch).map(c => c.year))].sort((a,b) => b - a);
    if (!newYears.includes(activeYear)) {
      setActiveYear(newYears[0]);
    }
  }, [activeBranch, data, activeYear]);

  const yearData = branchData.filter(c => c.year === activeYear);

  const rounds = [...new Set(yearData.map(c => c.capRound))].sort((a,b) => a - b);
  const [activeRound, setActiveRound] = useState(rounds[0] || 1);

  useEffect(() => {
    const newRounds = [...new Set(data.filter(c => (c.branch?.branchName || 'General') === activeBranch && c.year === activeYear).map(c => c.capRound))].sort((a,b) => a - b);
    if (!newRounds.includes(activeRound)) {
      setActiveRound(newRounds[0]);
    }
  }, [activeYear, activeBranch, data, activeRound]);

  const finalData = yearData.filter(c => c.capRound === activeRound);

  return (
    <div className="bg-[#111827] rounded-xl border border-[#374151] overflow-hidden flex flex-col">
      <div className="p-3 border-b border-[#374151] bg-[#1a2235]">
        <select 
          value={activeBranch} 
          onChange={e => setActiveBranch(e.target.value)}
          className="w-full bg-[#0a0e1a] border border-[#374151] rounded-lg py-2 px-3 text-sm text-white focus:outline-none focus:border-blue-500/50 appearance-none cursor-pointer"
        >
          {branches.map(b => <option key={b} value={b}>{b}</option>)}
        </select>
      </div>

      <div className="flex gap-2 p-3 overflow-x-auto border-b border-[#374151] custom-scrollbar">
        {years.map(y => (
          <button
            key={y}
            onClick={() => setActiveYear(y)}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors shrink-0 ${activeYear === y ? 'bg-blue-500 text-white' : 'bg-[#1f2937] text-[#9ca3af] hover:text-white hover:bg-[#374151]'}`}
          >
            {y}
          </button>
        ))}
      </div>

      <div className="flex gap-2 p-3 overflow-x-auto border-b border-[#374151] bg-[#111827] custom-scrollbar">
        {rounds.map(r => (
          <button
            key={r}
            onClick={() => setActiveRound(r)}
            className={`px-3 py-1 rounded-full text-[11px] font-bold tracking-wide transition-colors shrink-0 ${activeRound === r ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/50' : 'bg-[#1f2937] text-[#9ca3af] border border-transparent hover:text-white'}`}
          >
            Round {r}
          </button>
        ))}
      </div>

      <div className="p-3 grid grid-cols-2 sm:grid-cols-3 gap-3 max-h-[300px] overflow-y-auto custom-scrollbar">
        {finalData.map((c, i) => (
          <div key={i} className="flex justify-between items-center bg-[#0a0e1a] p-3 rounded-xl border border-[#1f2937] hover:border-[#374151] transition-colors">
            <span className="text-xs font-bold text-[#9ca3af]">{c.category}</span>
            <span className="text-sm font-bold text-white">{c.closingPercentile}</span>
          </div>
        ))}
        {finalData.length === 0 && (
          <div className="col-span-full text-center text-[#6b7280] py-4 text-xs">No cutoffs found.</div>
        )}
      </div>
    </div>
  );
};
export default function ExploreColleges() {
  const [query, setQuery] = useState('');
  const [districts, setDistricts] = useState([]);
  const [selectedDistrict, setSelectedDistrict] = useState('');
  
  const [colleges, setColleges] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // Expanded college state
  const [expandedId, setExpandedId] = useState(null);
  const [cutoffs, setCutoffs] = useState({});
  const [liveData, setLiveData] = useState({});
  const [loadingExtras, setLoadingExtras] = useState(false);

  useEffect(() => {
    getDistricts().then(setDistricts).catch(console.error);
    // Initial fetch of some colleges (e.g., Pune by default to populate)
    handleDistrictChange('Pune');
  }, []);

  const sortColleges = (list) => {
    return list.sort((a, b) => {
      const scoreA = NAAC_SCORES[a.naacGrade] || 0;
      const scoreB = NAAC_SCORES[b.naacGrade] || 0;
      return scoreB - scoreA;
    });
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setSelectedDistrict('');
    try {
      const res = await searchColleges(query);
      setColleges(sortColleges(res));
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDistrictChange = async (dist) => {
    setSelectedDistrict(dist);
    setQuery('');
    if (!dist) return;
    setLoading(true);
    try {
      const res = await getCollegesByDistrict(dist);
      setColleges(sortColleges(res));
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const toggleExpand = async (college) => {
    if (expandedId === college.id) {
      setExpandedId(null);
      return;
    }
    setExpandedId(college.id);
    
    // Only fetch if not already fetched
    if (!cutoffs[college.id] || !liveData[college.id]) {
      setLoadingExtras(true);
      try {
        const [cutoffRes, liveRes] = await Promise.all([
          getCollegeCutoffs(college.id).catch(() => []),
          getLiveCollegeDetails(college.name, college.id).catch(() => null)
        ]);
        
        setCutoffs(prev => ({ ...prev, [college.id]: cutoffRes }));
        setLiveData(prev => ({ ...prev, [college.id]: liveRes }));
      } catch (err) {
        console.error(err);
      } finally {
        setLoadingExtras(false);
      }
    }
  };

  return (
    <div className="flex flex-col h-full bg-[#030712] relative z-10 p-6 md:p-8 fade-in overflow-y-auto">
      {/* Decorative Orbs */}
      <div className="bg-orb-1" />
      <div className="bg-orb-2" />

      <div className="max-w-5xl w-full mx-auto space-y-8">
        
        {/* Header & Search */}
        <div className="glass-panel rounded-3xl p-6 md:p-8 flex flex-col md:flex-row gap-4 items-center justify-between border-t border-l border-white/5">
          <div className="flex-1 w-full">
            <h1 className="text-3xl font-bold text-white mb-2 tracking-tight">Explore Colleges</h1>
            <p className="text-[#9ca3af] text-sm">Discover top MHT-CET colleges, check past cutoffs, and view real-time data.</p>
          </div>

          <div className="flex-1 w-full flex flex-col sm:flex-row gap-3">
            <form onSubmit={handleSearch} className="flex-1 relative">
              <input 
                type="text" 
                value={query}
                onChange={e => setQuery(e.target.value)}
                placeholder="Search college by name..."
                className="w-full bg-[#0a0e1a] border border-[#374151] rounded-xl py-3 px-4 pl-10 text-sm text-white focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50 transition-all placeholder:text-[#6b7280]"
              />
              <svg className="w-4 h-4 absolute left-4 top-3.5 text-[#6b7280]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
              <button type="submit" className="hidden" />
            </form>
            
            <select 
              value={selectedDistrict}
              onChange={e => handleDistrictChange(e.target.value)}
              className="bg-[#0a0e1a] border border-[#374151] rounded-xl py-3 px-4 text-sm text-white focus:outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/50 transition-all appearance-none sm:w-[180px] cursor-pointer"
            >
              <option value="" disabled>Filter District</option>
              {districts.map(d => <option key={d} value={d}>{d}</option>)}
            </select>
          </div>
        </div>

        {/* Results */}
        <div className="space-y-4">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-20">
              <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mb-4" />
              <p className="text-[#6b7280] text-sm animate-pulse">Hunting down colleges...</p>
            </div>
          ) : colleges.length === 0 ? (
            <div className="text-center py-20 text-[#6b7280] glass-panel rounded-3xl">
              No colleges found. Try a different search term or district.
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-4">
              {colleges.map((college, idx) => (
                <div key={college.id} className="glass-card rounded-2xl overflow-hidden group">
                  {/* Collapsed Header */}
                  <div 
                    onClick={() => toggleExpand(college)}
                    className="p-5 cursor-pointer flex flex-col md:flex-row md:items-center justify-between gap-4 relative"
                  >
                    <div className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-blue-500 to-emerald-500 opacity-0 group-hover:opacity-100 transition-opacity" />
                    
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-[10px] font-bold text-[#6b7280] tracking-widest bg-[#0a0e1a] px-2 py-0.5 rounded border border-[#1f2937]">RANK #{idx + 1}</span>
                        {college.naacGrade && (
                          <span className="text-[10px] font-bold text-blue-400 bg-blue-400/10 border border-blue-400/20 px-2 py-0.5 rounded-full">
                            NAAC {college.naacGrade}
                          </span>
                        )}
                        {college.collegeType && (
                          <span className="text-[10px] font-medium text-emerald-400 bg-emerald-400/10 border border-emerald-400/20 px-2 py-0.5 rounded-full">
                            {college.collegeType}
                          </span>
                        )}
                      </div>
                      <h3 className="text-[16px] font-semibold text-white leading-snug group-hover:text-blue-200 transition-colors">
                        {college.name}
                      </h3>
                      <p className="text-[13px] text-[#9ca3af] mt-1 flex items-center gap-1.5">
                        📍 {college.city}, {college.district} 
                        {college.establishedYear && <span className="opacity-50">• Est. {college.establishedYear}</span>}
                      </p>
                    </div>

                    <div className="flex items-center justify-end gap-3 shrink-0">
                       <button className="text-[12px] font-medium text-blue-400 bg-blue-500/10 hover:bg-blue-500/20 px-4 py-2 rounded-xl transition-colors flex items-center gap-2">
                         {expandedId === college.id ? 'Close Details' : 'View Cutoffs & Data'}
                         <svg className={`w-4 h-4 transition-transform duration-300 ${expandedId === college.id ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path></svg>
                       </button>
                    </div>
                  </div>

                  {/* Expanded Content */}
                  {expandedId === college.id && (
                    <div className="border-t border-[#374151] bg-[#0a0e1a]/50 p-6 slide-down">
                      {loadingExtras ? (
                        <div className="flex items-center gap-3 text-sm text-[#9ca3af] justify-center py-10">
                          <span className="w-5 h-5 border-2 border-emerald-400 border-t-transparent rounded-full animate-spin" />
                          Fetching live AI data & past cutoffs...
                        </div>
                      ) : (
                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                          
                          {/* Left Column: Live Details */}
                          <div className="lg:col-span-1 space-y-4">
                            <h4 className="text-xs font-bold text-[#6b7280] tracking-widest uppercase flex items-center gap-2">
                              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" /> Live Web Data
                            </h4>
                            
                            {liveData[college.id] ? (
                              <div className="space-y-3">
                                {liveData[college.id].quick_facts?.length > 0 && (
                                  <div className="flex flex-wrap gap-2 mb-2">
                                    {liveData[college.id].quick_facts.map((fact, i) => (
                                      <span key={i} className="text-[11px] bg-[#1f2937] border border-[#374151] text-[#9ca3af] px-2.5 py-1 rounded-full">
                                        {fact}
                                      </span>
                                    ))}
                                  </div>
                                )}
                                
                                <div className="space-y-2">
                                  {liveData[college.id].official_website && (
                                    <a href={liveData[college.id].official_website} target="_blank" rel="noopener noreferrer" className="flex items-center gap-3 w-full p-3 rounded-xl border border-[#374151] bg-[#111827] text-[#e5e7eb] hover:border-blue-500/50 hover:bg-[#1e293b] transition-all text-sm group/link">
                                      <div className="bg-blue-500/10 p-2 rounded-lg text-blue-400 group-hover/link:bg-blue-500 group-hover/link:text-white transition-colors">🌐</div>
                                      <div className="flex-1">Official Website</div>
                                      <div className="text-[#6b7280]">↗</div>
                                    </a>
                                  )}
                                  {liveData[college.id].fee_link && (
                                    <a href={liveData[college.id].fee_link} target="_blank" rel="noopener noreferrer" className="flex items-center gap-3 w-full p-3 rounded-xl border border-[#374151] bg-[#111827] text-[#e5e7eb] hover:border-emerald-500/50 hover:bg-[#1e293b] transition-all text-sm group/link">
                                      <div className="bg-emerald-500/10 p-2 rounded-lg text-emerald-400 group-hover/link:bg-emerald-500 group-hover/link:text-white transition-colors">💰</div>
                                      <div className="flex-1">Fee Structure</div>
                                      <div className="text-[#6b7280]">↗</div>
                                    </a>
                                  )}
                                  {liveData[college.id].hostel_link && (
                                    <a href={liveData[college.id].hostel_link} target="_blank" rel="noopener noreferrer" className="flex items-center gap-3 w-full p-3 rounded-xl border border-[#374151] bg-[#111827] text-[#e5e7eb] hover:border-amber-500/50 hover:bg-[#1e293b] transition-all text-sm group/link">
                                      <div className="bg-amber-500/10 p-2 rounded-lg text-amber-400 group-hover/link:bg-amber-500 group-hover/link:text-white transition-colors">🏠</div>
                                      <div className="flex-1">Hostel Info</div>
                                      <div className="text-[#6b7280]">↗</div>
                                    </a>
                                  )}
                                  {liveData[college.id].placement_link && (
                                    <a href={liveData[college.id].placement_link} target="_blank" rel="noopener noreferrer" className="flex items-center gap-3 w-full p-3 rounded-xl border border-[#374151] bg-[#111827] text-[#e5e7eb] hover:border-purple-500/50 hover:bg-[#1e293b] transition-all text-sm group/link">
                                      <div className="bg-purple-500/10 p-2 rounded-lg text-purple-400 group-hover/link:bg-purple-500 group-hover/link:text-white transition-colors">📊</div>
                                      <div className="flex-1">Placements</div>
                                      <div className="text-[#6b7280]">↗</div>
                                    </a>
                                  )}
                                </div>
                              </div>
                            ) : (
                              <p className="text-sm text-[#6b7280]">Live data not available.</p>
                            )}
                          </div>

                          {/* Right Column: Cutoffs */}
                          <div className="lg:col-span-2 space-y-4">
                            <h4 className="text-xs font-bold text-[#6b7280] tracking-widest uppercase">Past Branch-Wise Cutoffs</h4>
                            
                            {cutoffs[college.id]?.length > 0 ? (
                              <CollegeCutoffViewer data={cutoffs[college.id]} />
                            ) : (
                              <div className="p-8 text-center text-[#6b7280] bg-[#111827] rounded-xl border border-[#374151] border-dashed">
                                No cutoff data available for this college.
                              </div>
                            )}
                          </div>
                          
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
