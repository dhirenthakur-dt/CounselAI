import { useState, useEffect, useMemo, useRef } from 'react';
import { searchColleges, getCollegeCutoffs, getAllColleges } from '../api';

const NAAC_SCORES = { 'A++': 7, 'A+': 6, 'A': 5, 'B++': 4, 'B+': 3, 'B': 2, 'C': 1 };

const PRESET_BATTLES = [
  { name: 'PCCOE vs VIIT (Pune)', q1: 'Pimpri Chinchwad College of Engineering', q2: 'Vishwakarma Institute of Information Technology' },
  { name: 'COEP vs VJTI (Premier)', q1: 'College of Engineering, Pune', q2: 'Veermata Jijabai Technological Institute' },
  { name: 'PICT vs VIT (CS/IT Hubs)', q1: 'Pune Institute of Computer Technology', q2: 'Vishwakarma Institute of Technology' },
  { name: 'GCE Karad vs GCE Amravati (Govt)', q1: 'Government College of Engineering, Karad', q2: 'Government College of Engineering, Amravati' }
];

const CATEGORIES = [
  { code: 'GOPENS', label: 'General / Open (GOPENS)' },
  { code: 'GOBCS',  label: 'OBC (GOBCS)' },
  { code: 'EWS',    label: 'EWS (Economically Weaker)' },
  { code: 'GSCS',   label: 'SC (GSCS)' },
  { code: 'GSTS',   label: 'ST (GSTS)' },
  { code: 'TFWS',   label: 'TFWS (Tuition Fee Waiver)' },
  { code: 'LOPENS', label: 'Ladies Open (LOPENS)' },
  { code: 'LOBCS',  label: 'Ladies OBC (LOBCS)' },
];

export default function CompareColleges() {
  const [college1, setCollege1] = useState(null);
  const [college2, setCollege2] = useState(null);

  const [search1, setSearch1] = useState('');
  const [search2, setSearch2] = useState('');

  const [results1, setResults1] = useState([]);
  const [results2, setResults2] = useState([]);

  const [openDropdown1, setOpenDropdown1] = useState(false);
  const [openDropdown2, setOpenDropdown2] = useState(false);

  const [cutoffs1, setCutoffs1] = useState([]);
  const [cutoffs2, setCutoffs2] = useState([]);

  const [loading1, setLoading1] = useState(false);
  const [loading2, setLoading2] = useState(false);

  // Controls
  const [syncBranches, setSyncBranches] = useState(true);
  const [selectedBranch1, setSelectedBranch1] = useState('');
  const [selectedBranch2, setSelectedBranch2] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('GOPENS');
  const [selectedYear, setSelectedYear] = useState(2024);
  const [selectedRound, setSelectedRound] = useState(1);

  const dropRef1 = useRef(null);
  const dropRef2 = useRef(null);

  // Close dropdowns on click outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (dropRef1.current && !dropRef1.current.contains(event.target)) {
        setOpenDropdown1(false);
      }
      if (dropRef2.current && !dropRef2.current.contains(event.target)) {
        setOpenDropdown2(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Search debouncing for College 1
  useEffect(() => {
    if (!search1.trim()) {
      setResults1([]);
      return;
    }
    const timer = setTimeout(async () => {
      try {
        const data = await searchColleges(search1.trim());
        setResults1(data.slice(0, 8));
      } catch {
        setResults1([]);
      }
    }, 250);
    return () => clearTimeout(timer);
  }, [search1]);

  // Search debouncing for College 2
  useEffect(() => {
    if (!search2.trim()) {
      setResults2([]);
      return;
    }
    const timer = setTimeout(async () => {
      try {
        const data = await searchColleges(search2.trim());
        setResults2(data.slice(0, 8));
      } catch {
        setResults2([]);
      }
    }, 250);
    return () => clearTimeout(timer);
  }, [search2]);

  // Load cutoffs for College 1
  useEffect(() => {
    if (!college1) {
      setCutoffs1([]);
      return;
    }
    setLoading1(true);
    getCollegeCutoffs(college1.id)
      .then(data => {
        setCutoffs1(data);
      })
      .catch(() => setCutoffs1([]))
      .finally(() => setLoading1(false));
  }, [college1]);

  // Load cutoffs for College 2
  useEffect(() => {
    if (!college2) {
      setCutoffs2([]);
      return;
    }
    setLoading2(true);
    getCollegeCutoffs(college2.id)
      .then(data => {
        setCutoffs2(data);
      })
      .catch(() => setCutoffs2([]))
      .finally(() => setLoading2(false));
  }, [college2]);

  // Extract unique branches for both
  const branches1 = useMemo(() => {
    return [...new Set(cutoffs1.map(c => c.branch?.branchName || 'General'))].sort();
  }, [cutoffs1]);

  const branches2 = useMemo(() => {
    return [...new Set(cutoffs2.map(c => c.branch?.branchName || 'General'))].sort();
  }, [cutoffs2]);

  // Common and all unique branches
  const commonBranches = useMemo(() => {
    return branches1.filter(b => branches2.includes(b));
  }, [branches1, branches2]);

  const allAvailableBranches = useMemo(() => {
    return [...new Set([...branches1, ...branches2])].sort();
  }, [branches1, branches2]);

  // Initialize selected branches when colleges load
  useEffect(() => {
    if (branches1.length > 0 && !selectedBranch1) {
      const defaultB = branches1.find(b => b.toLowerCase().includes('computer')) || branches1[0];
      setSelectedBranch1(defaultB);
    }
  }, [branches1, selectedBranch1]);

  useEffect(() => {
    if (branches2.length > 0 && !selectedBranch2) {
      const defaultB = branches2.find(b => b.toLowerCase().includes('computer')) || branches2[0];
      setSelectedBranch2(defaultB);
    }
  }, [branches2, selectedBranch2]);

  // If in sync mode, keep branch2 synced to branch1
  useEffect(() => {
    if (syncBranches && selectedBranch1) {
      setSelectedBranch2(selectedBranch1);
    }
  }, [syncBranches, selectedBranch1]);

  // Load preset battle
  const loadPreset = async (p) => {
    try {
      const res1 = await searchColleges(p.q1);
      const res2 = await searchColleges(p.q2);
      if (res1.length > 0) setCollege1(res1[0]);
      if (res2.length > 0) setCollege2(res2[0]);
    } catch (e) {
      console.error("Failed to load preset:", e);
    }
  };

  // Swap colleges
  const swapColleges = () => {
    const c1 = college1;
    const c2 = college2;
    setCollege1(c2);
    setCollege2(c1);

    const b1 = selectedBranch1;
    const b2 = selectedBranch2;
    setSelectedBranch1(b2);
    setSelectedBranch2(b1);
  };

  // Get active cutoffs for chosen parameters
  const activeCutoff1 = useMemo(() => {
    return cutoffs1.find(c => 
      (c.branch?.branchName || 'General') === selectedBranch1 &&
      c.category === selectedCategory &&
      c.year === selectedYear &&
      c.capRound === selectedRound
    );
  }, [cutoffs1, selectedBranch1, selectedCategory, selectedYear, selectedRound]);

  const activeCutoff2 = useMemo(() => {
    return cutoffs2.find(c => 
      (c.branch?.branchName || 'General') === selectedBranch2 &&
      c.category === selectedCategory &&
      c.year === selectedYear &&
      c.capRound === selectedRound
    );
  }, [cutoffs2, selectedBranch2, selectedCategory, selectedYear, selectedRound]);

  // Historical trend data for 2024, 2023, 2022
  const historicalTrend = useMemo(() => {
    const rows = [];
    const years = [2024, 2023, 2022];
    const rounds = [1, 2];

    for (const yr of years) {
      for (const rnd of rounds) {
        const item1 = cutoffs1.find(c => 
          (c.branch?.branchName || 'General') === selectedBranch1 &&
          c.category === selectedCategory &&
          c.year === yr &&
          c.capRound === rnd
        );
        const item2 = cutoffs2.find(c => 
          (c.branch?.branchName || 'General') === selectedBranch2 &&
          c.category === selectedCategory &&
          c.year === yr &&
          c.capRound === rnd
        );

        if (item1 || item2) {
          const p1 = item1 ? item1.closingPercentile : null;
          const p2 = item2 ? item2.closingPercentile : null;
          const diff = (p1 !== null && p2 !== null) ? (p1 - p2).toFixed(2) : null;
          rows.push({ year: yr, round: rnd, p1, p2, diff });
        }
      }
    }
    return rows;
  }, [cutoffs1, cutoffs2, selectedBranch1, selectedBranch2, selectedCategory]);

  // Calculation helpers
  const cutoffDiff = useMemo(() => {
    if (activeCutoff1 && activeCutoff2) {
      return (activeCutoff1.closingPercentile - activeCutoff2.closingPercentile).toFixed(2);
    }
    return null;
  }, [activeCutoff1, activeCutoff2]);

  const feeDiff = useMemo(() => {
    if (college1?.annualFee && college2?.annualFee) {
      return college1.annualFee - college2.annualFee;
    }
    return null;
  }, [college1, college2]);

  const naacScore1 = college1?.naacGrade ? NAAC_SCORES[college1.naacGrade] || 0 : 0;
  const naacScore2 = college2?.naacGrade ? NAAC_SCORES[college2.naacGrade] || 0 : 0;

  return (
    <div className="flex-1 overflow-y-auto px-4 md:px-8 py-8 space-y-8 scroll-smooth custom-scrollbar">
      
      {/* Header Banner */}
      <div className="glass-card rounded-2xl p-6 md:p-8 relative overflow-hidden border border-[#334155]/60">
        <div className="absolute top-0 right-0 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold mb-3">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse" />
              100% Data-Driven Comparison
            </div>
            <h1 className="text-2xl md:text-3xl font-bold text-white tracking-tight">
              Compare <span className="neon-text">Engineering Colleges</span>
            </h1>
            <p className="text-sm text-[#94a3b8] mt-1 max-w-2xl">
              Compare two Maharashtra colleges side-by-side using official DTE cutoffs, fee structures, NAAC accreditation, and branch seat matrices.
            </p>
          </div>

          {/* Quick Presets */}
          <div className="flex flex-col gap-2">
            <span className="text-[11px] font-bold text-[#64748b] uppercase tracking-wider">Quick Battles:</span>
            <div className="flex flex-wrap gap-2">
              {PRESET_BATTLES.map((p, idx) => (
                <button
                  key={idx}
                  onClick={() => loadPreset(p)}
                  className="text-xs bg-[#0f172a] hover:bg-[#1e293b] text-[#cbd5e1] hover:text-white border border-[#334155] px-3 py-1.5 rounded-xl transition-all duration-200 active:scale-95 shadow-sm"
                >
                  {p.name}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* College Pickers Bar */}
      <div className="grid grid-cols-1 lg:grid-cols-11 gap-4 items-center">
        
        {/* College 1 Selector */}
        <div className="lg:col-span-5 relative" ref={dropRef1}>
          <label className="block text-xs font-bold text-[#94a3b8] uppercase tracking-wider mb-2 flex items-center justify-between">
            <span>🏛️ College 1</span>
            {college1 && (
              <button 
                onClick={() => setCollege1(null)}
                className="text-red-400 hover:text-red-300 text-[11px] font-medium"
              >
                Clear
              </button>
            )}
          </label>
          <div className="bg-[#0f172a] border border-[#334155] rounded-2xl p-2.5 focus-within:border-blue-500/60 transition-colors shadow-inner">
            <input
              type="text"
              value={college1 ? college1.name : search1}
              onChange={e => {
                if (college1) setCollege1(null);
                setSearch1(e.target.value);
                setOpenDropdown1(true);
              }}
              onFocus={() => setOpenDropdown1(true)}
              placeholder="Search e.g. PCCOE, COEP, VIIT..."
              className="w-full bg-transparent px-3 py-1.5 text-sm text-white placeholder-[#64748b] focus:outline-none font-medium"
            />
          </div>

          {/* Dropdown Results 1 */}
          {openDropdown1 && results1.length > 0 && (
            <div className="absolute left-0 right-0 top-full mt-2 bg-[#0f172a] border border-[#334155] rounded-2xl overflow-hidden shadow-2xl z-50 max-h-72 overflow-y-auto custom-scrollbar">
              {results1.map(c => (
                <button
                  key={c.id}
                  onClick={() => {
                    setCollege1(c);
                    setSearch1('');
                    setOpenDropdown1(false);
                  }}
                  className="w-full text-left px-4 py-3 hover:bg-[#1e293b] border-b border-[#1e293b] last:border-0 transition-colors flex flex-col"
                >
                  <span className="text-sm font-semibold text-white leading-snug">{c.name}</span>
                  <div className="flex gap-2 text-[11px] text-[#94a3b8] mt-1">
                    <span>📍 {c.district || c.city || 'Maharashtra'}</span>
                    <span>•</span>
                    <span className="text-emerald-400">{c.collegeType || 'Engineering'}</span>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Swap Button */}
        <div className="lg:col-span-1 flex justify-center py-1">
          <button
            onClick={swapColleges}
            disabled={!college1 && !college2}
            title="Swap colleges"
            className="w-12 h-12 rounded-2xl bg-[#0f172a] border border-[#334155] hover:border-blue-500/50 text-[#94a3b8] hover:text-white flex items-center justify-center transition-all duration-300 disabled:opacity-30 disabled:cursor-not-allowed shadow-lg hover:rotate-180"
          >
            <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
            </svg>
          </button>
        </div>

        {/* College 2 Selector */}
        <div className="lg:col-span-5 relative" ref={dropRef2}>
          <label className="block text-xs font-bold text-[#94a3b8] uppercase tracking-wider mb-2 flex items-center justify-between">
            <span>🏛️ College 2</span>
            {college2 && (
              <button 
                onClick={() => setCollege2(null)}
                className="text-red-400 hover:text-red-300 text-[11px] font-medium"
              >
                Clear
              </button>
            )}
          </label>
          <div className="bg-[#0f172a] border border-[#334155] rounded-2xl p-2.5 focus-within:border-blue-500/60 transition-colors shadow-inner">
            <input
              type="text"
              value={college2 ? college2.name : search2}
              onChange={e => {
                if (college2) setCollege2(null);
                setSearch2(e.target.value);
                setOpenDropdown2(true);
              }}
              onFocus={() => setOpenDropdown2(true)}
              placeholder="Search e.g. VIT, VJTI, SPIT..."
              className="w-full bg-transparent px-3 py-1.5 text-sm text-white placeholder-[#64748b] focus:outline-none font-medium"
            />
          </div>

          {/* Dropdown Results 2 */}
          {openDropdown2 && results2.length > 0 && (
            <div className="absolute left-0 right-0 top-full mt-2 bg-[#0f172a] border border-[#334155] rounded-2xl overflow-hidden shadow-2xl z-50 max-h-72 overflow-y-auto custom-scrollbar">
              {results2.map(c => (
                <button
                  key={c.id}
                  onClick={() => {
                    setCollege2(c);
                    setSearch2('');
                    setOpenDropdown2(false);
                  }}
                  className="w-full text-left px-4 py-3 hover:bg-[#1e293b] border-b border-[#1e293b] last:border-0 transition-colors flex flex-col"
                >
                  <span className="text-sm font-semibold text-white leading-snug">{c.name}</span>
                  <div className="flex gap-2 text-[11px] text-[#94a3b8] mt-1">
                    <span>📍 {c.district || c.city || 'Maharashtra'}</span>
                    <span>•</span>
                    <span className="text-emerald-400">{c.collegeType || 'Engineering'}</span>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* When Both Colleges Are Selected: Controls & Comparison Dashboard */}
      {college1 && college2 ? (
        <div className="space-y-8 fade-in">
          
          {/* Controls Bar: Category, Branch Mode, Year, Round */}
          <div className="glass-card rounded-2xl p-5 border border-[#334155]/60 space-y-4">
            <div className="flex items-center justify-between border-b border-[#334155] pb-3">
              <span className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-blue-500" />
                Comparison Parameters
              </span>
              <button
                onClick={() => setSyncBranches(s => !s)}
                className={`text-xs px-3 py-1.5 rounded-xl font-semibold border transition-all ${
                  syncBranches 
                    ? 'bg-blue-500/10 text-blue-400 border-blue-500/30' 
                    : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                }`}
              >
                {syncBranches ? '🔒 Same Branch Comparison' : '🔀 Independent Branches (Custom)'}
              </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              
              {/* Category */}
              <div>
                <label className="block text-[11px] font-bold text-[#94a3b8] uppercase mb-1.5">Category</label>
                <select
                  value={selectedCategory}
                  onChange={e => setSelectedCategory(e.target.value)}
                  className="w-full bg-[#0f172a] border border-[#334155] rounded-xl px-3 py-2 text-xs font-semibold text-white focus:outline-none focus:border-blue-500"
                >
                  {CATEGORIES.map(cat => (
                    <option key={cat.code} value={cat.code}>{cat.label}</option>
                  ))}
                </select>
              </div>

              {/* Year */}
              <div>
                <label className="block text-[11px] font-bold text-[#94a3b8] uppercase mb-1.5">Cutoff Year</label>
                <div className="flex rounded-xl bg-[#0f172a] border border-[#334155] p-1 gap-1">
                  {[2024, 2023, 2022].map(yr => (
                    <button
                      key={yr}
                      onClick={() => setSelectedYear(yr)}
                      className={`flex-1 py-1.5 rounded-lg text-xs font-bold transition-all ${
                        selectedYear === yr 
                          ? 'bg-blue-500 text-white shadow-md' 
                          : 'text-[#94a3b8] hover:text-white'
                      }`}
                    >
                      {yr}
                    </button>
                  ))}
                </div>
              </div>

              {/* CAP Round */}
              <div>
                <label className="block text-[11px] font-bold text-[#94a3b8] uppercase mb-1.5">CAP Round</label>
                <div className="flex rounded-xl bg-[#0f172a] border border-[#334155] p-1 gap-1">
                  {[1, 2, 3].map(rnd => (
                    <button
                      key={rnd}
                      onClick={() => setSelectedRound(rnd)}
                      className={`flex-1 py-1.5 rounded-lg text-xs font-bold transition-all ${
                        selectedRound === rnd 
                          ? 'bg-emerald-500 text-white shadow-md' 
                          : 'text-[#94a3b8] hover:text-white'
                      }`}
                    >
                      Round {rnd}
                    </button>
                  ))}
                </div>
              </div>

              {/* Branch Selector (Single if Synced) */}
              {syncBranches ? (
                <div>
                  <label className="block text-[11px] font-bold text-[#94a3b8] uppercase mb-1.5">Branch (Both Colleges)</label>
                  <select
                    value={selectedBranch1}
                    onChange={e => {
                      setSelectedBranch1(e.target.value);
                      setSelectedBranch2(e.target.value);
                    }}
                    className="w-full bg-[#0f172a] border border-[#334155] rounded-xl px-3 py-2 text-xs font-semibold text-white focus:outline-none focus:border-blue-500 truncate"
                  >
                    {allAvailableBranches.map(b => (
                      <option key={b} value={b}>
                        {b} {commonBranches.includes(b) ? '✓ (Both)' : ''}
                      </option>
                    ))}
                  </select>
                </div>
              ) : (
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="block text-[10px] font-bold text-[#94a3b8] uppercase mb-1 truncate">Branch (Col 1)</label>
                    <select
                      value={selectedBranch1}
                      onChange={e => setSelectedBranch1(e.target.value)}
                      className="w-full bg-[#0f172a] border border-[#334155] rounded-xl px-2 py-2 text-[11px] font-semibold text-white focus:outline-none focus:border-blue-500 truncate"
                    >
                      {branches1.map(b => <option key={b} value={b}>{b}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="block text-[10px] font-bold text-[#94a3b8] uppercase mb-1 truncate">Branch (Col 2)</label>
                    <select
                      value={selectedBranch2}
                      onChange={e => setSelectedBranch2(e.target.value)}
                      className="w-full bg-[#0f172a] border border-[#334155] rounded-xl px-2 py-2 text-[11px] font-semibold text-white focus:outline-none focus:border-blue-500 truncate"
                    >
                      {branches2.map(b => <option key={b} value={b}>{b}</option>)}
                    </select>
                  </div>
                </div>
              )}

            </div>
          </div>

          {/* Section 1: Head-to-Head Cutoff Battle Card */}
          <div className="glass-card rounded-2xl p-6 border border-[#334155]/60 relative overflow-hidden">
            <div className="flex items-center justify-between mb-6">
              <div>
                <span className="text-xs font-bold text-blue-400 uppercase tracking-widest">Head-to-Head Cutoffs</span>
                <h3 className="text-lg font-bold text-white mt-0.5">
                  Closing Percentile for {selectedCategory} ({selectedYear} - Round {selectedRound})
                </h3>
              </div>
              {cutoffDiff !== null && (
                <div className={`px-3 py-1.5 rounded-full border text-xs font-bold ${
                  cutoffDiff > 0 
                    ? 'bg-blue-500/10 text-blue-400 border-blue-500/30' 
                    : cutoffDiff < 0 
                    ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' 
                    : 'bg-gray-500/10 text-gray-400 border-gray-500/30'
                }`}>
                  {cutoffDiff > 0 
                    ? `College 1 is +${cutoffDiff}% tougher` 
                    : cutoffDiff < 0 
                    ? `College 2 is +${Math.abs(cutoffDiff)}% tougher` 
                    : 'Identical Cutoffs'}
                </div>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 relative">
              
              {/* College 1 Cutoff Bar */}
              <div className="bg-[#0f172a] p-5 rounded-2xl border border-[#1e293b] space-y-3">
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="text-sm font-bold text-white line-clamp-1">{college1.name}</h4>
                    <p className="text-xs text-blue-400 font-semibold mt-0.5">{selectedBranch1}</p>
                  </div>
                  <span className="text-2xl font-black text-white">
                    {activeCutoff1 ? `${activeCutoff1.closingPercentile}%` : 'N/A'}
                  </span>
                </div>

                {/* Progress bar */}
                <div className="w-full bg-[#1e293b] h-3 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full transition-all duration-500"
                    style={{ width: `${activeCutoff1 ? Math.min(100, activeCutoff1.closingPercentile) : 0}%` }}
                  />
                </div>

                <div className="flex justify-between text-[11px] text-[#94a3b8] font-medium pt-1">
                  <span>Category: {selectedCategory}</span>
                  <span>{activeCutoff1 ? `Rank: #${activeCutoff1.closingRank || 'DTE'}` : 'No seat in this round'}</span>
                </div>
              </div>

              {/* College 2 Cutoff Bar */}
              <div className="bg-[#0f172a] p-5 rounded-2xl border border-[#1e293b] space-y-3">
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="text-sm font-bold text-white line-clamp-1">{college2.name}</h4>
                    <p className="text-xs text-emerald-400 font-semibold mt-0.5">{selectedBranch2}</p>
                  </div>
                  <span className="text-2xl font-black text-white">
                    {activeCutoff2 ? `${activeCutoff2.closingPercentile}%` : 'N/A'}
                  </span>
                </div>

                {/* Progress bar */}
                <div className="w-full bg-[#1e293b] h-3 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-emerald-500 to-teal-500 rounded-full transition-all duration-500"
                    style={{ width: `${activeCutoff2 ? Math.min(100, activeCutoff2.closingPercentile) : 0}%` }}
                  />
                </div>

                <div className="flex justify-between text-[11px] text-[#94a3b8] font-medium pt-1">
                  <span>Category: {selectedCategory}</span>
                  <span>{activeCutoff2 ? `Rank: #${activeCutoff2.closingRank || 'DTE'}` : 'No seat in this round'}</span>
                </div>
              </div>

            </div>
          </div>

          {/* Section 2: Detailed Side-by-Side Fact Sheet Table */}
          <div className="glass-card rounded-2xl overflow-hidden border border-[#334155]/60">
            <div className="p-5 border-b border-[#334155] bg-[#0f172a]/50">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <span>📋</span> Side-by-Side Factual Specifications
              </h3>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-[#334155] bg-[#0f172a]">
                    <th className="p-4 text-xs font-bold text-[#94a3b8] uppercase tracking-wider w-1/4">Specification</th>
                    <th className="p-4 text-sm font-bold text-blue-400 w-3/8 truncate">{college1.name}</th>
                    <th className="p-4 text-sm font-bold text-emerald-400 w-3/8 truncate">{college2.name}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#1e293b]">
                  
                  {/* Location */}
                  <tr className="hover:bg-white/[0.02] transition-colors">
                    <td className="p-4 text-xs font-semibold text-[#94a3b8]">District & City</td>
                    <td className="p-4 font-medium text-white">{college1.district || college1.city || 'Maharashtra'}</td>
                    <td className="p-4 font-medium text-white">{college2.district || college2.city || 'Maharashtra'}</td>
                  </tr>

                  {/* College Type */}
                  <tr className="hover:bg-white/[0.02] transition-colors">
                    <td className="p-4 text-xs font-semibold text-[#94a3b8]">College Type</td>
                    <td className="p-4 font-medium text-white">
                      <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-500/10 text-blue-300 border border-blue-500/20">
                        {college1.collegeType || 'Private'}
                      </span>
                    </td>
                    <td className="p-4 font-medium text-white">
                      <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
                        {college2.collegeType || 'Private'}
                      </span>
                    </td>
                  </tr>

                  {/* Annual Fee */}
                  <tr className="hover:bg-white/[0.02] transition-colors">
                    <td className="p-4 text-xs font-semibold text-[#94a3b8]">Annual Tuition Fee</td>
                    <td className="p-4 font-medium text-white">
                      {college1.annualFee ? `₹${college1.annualFee.toLocaleString()}` : 'Contact College'}
                      {feeDiff !== null && feeDiff < 0 && (
                        <span className="ml-2 text-xs text-emerald-400 font-bold bg-emerald-400/10 px-2 py-0.5 rounded border border-emerald-400/20">
                          Save ₹{Math.abs(feeDiff).toLocaleString()} / yr 🏆
                        </span>
                      )}
                    </td>
                    <td className="p-4 font-medium text-white">
                      {college2.annualFee ? `₹${college2.annualFee.toLocaleString()}` : 'Contact College'}
                      {feeDiff !== null && feeDiff > 0 && (
                        <span className="ml-2 text-xs text-emerald-400 font-bold bg-emerald-400/10 px-2 py-0.5 rounded border border-emerald-400/20">
                          Save ₹{Math.abs(feeDiff).toLocaleString()} / yr 🏆
                        </span>
                      )}
                    </td>
                  </tr>

                  {/* 4-Year Total Estimated Cost */}
                  <tr className="hover:bg-white/[0.02] transition-colors">
                    <td className="p-4 text-xs font-semibold text-[#94a3b8]">4-Year Estimated Cost</td>
                    <td className="p-4 font-semibold text-white">
                      {college1.annualFee ? `₹${(college1.annualFee * 4).toLocaleString()}` : 'N/A'}
                    </td>
                    <td className="p-4 font-semibold text-white">
                      {college2.annualFee ? `₹${(college2.annualFee * 4).toLocaleString()}` : 'N/A'}
                    </td>
                  </tr>

                  {/* NAAC Grade */}
                  <tr className="hover:bg-white/[0.02] transition-colors">
                    <td className="p-4 text-xs font-semibold text-[#94a3b8]">NAAC Accreditation</td>
                    <td className="p-4 font-medium text-white">
                      <span className="font-bold text-amber-400">{college1.naacGrade || 'Not Available'}</span>
                      {naacScore1 > naacScore2 && (
                        <span className="ml-2 text-[11px] font-bold text-amber-300 bg-amber-400/10 px-2 py-0.5 rounded border border-amber-400/20">
                          Higher Grade 🏆
                        </span>
                      )}
                    </td>
                    <td className="p-4 font-medium text-white">
                      <span className="font-bold text-amber-400">{college2.naacGrade || 'Not Available'}</span>
                      {naacScore2 > naacScore1 && (
                        <span className="ml-2 text-[11px] font-bold text-amber-300 bg-amber-400/10 px-2 py-0.5 rounded border border-amber-400/20">
                          Higher Grade 🏆
                        </span>
                      )}
                    </td>
                  </tr>

                  {/* Hostel Available */}
                  <tr className="hover:bg-white/[0.02] transition-colors">
                    <td className="p-4 text-xs font-semibold text-[#94a3b8]">Hostel on Campus</td>
                    <td className="p-4 font-medium">
                      {college1.hostelAvailable ? (
                        <span className="text-emerald-400 font-semibold flex items-center gap-1.5">
                          <span>✓</span> Available (Boys & Girls)
                        </span>
                      ) : (
                        <span className="text-[#64748b]">Private PGs outside</span>
                      )}
                    </td>
                    <td className="p-4 font-medium">
                      {college2.hostelAvailable ? (
                        <span className="text-emerald-400 font-semibold flex items-center gap-1.5">
                          <span>✓</span> Available (Boys & Girls)
                        </span>
                      ) : (
                        <span className="text-[#64748b]">Private PGs outside</span>
                      )}
                    </td>
                  </tr>

                  {/* Total Branches Offered */}
                  <tr className="hover:bg-white/[0.02] transition-colors">
                    <td className="p-4 text-xs font-semibold text-[#94a3b8]">Engineering Branches</td>
                    <td className="p-4 font-medium text-white">{branches1.length} branches offered</td>
                    <td className="p-4 font-medium text-white">{branches2.length} branches offered</td>
                  </tr>

                  {/* Established Year */}
                  <tr className="hover:bg-white/[0.02] transition-colors">
                    <td className="p-4 text-xs font-semibold text-[#94a3b8]">Established Year</td>
                    <td className="p-4 font-medium text-white">
                      {college1.establishedYear ? `${college1.establishedYear} (${new Date().getFullYear() - college1.establishedYear} yrs legacy)` : 'N/A'}
                    </td>
                    <td className="p-4 font-medium text-white">
                      {college2.establishedYear ? `${college2.establishedYear} (${new Date().getFullYear() - college2.establishedYear} yrs legacy)` : 'N/A'}
                    </td>
                  </tr>

                  {/* Official Website */}
                  <tr className="hover:bg-white/[0.02] transition-colors">
                    <td className="p-4 text-xs font-semibold text-[#94a3b8]">Official Portal</td>
                    <td className="p-4">
                      {college1.website ? (
                        <a href={college1.website.startsWith('http') ? college1.website : `https://${college1.website}`} target="_blank" rel="noreferrer" className="text-blue-400 hover:underline text-xs flex items-center gap-1">
                          Visit College Website ↗
                        </a>
                      ) : 'N/A'}
                    </td>
                    <td className="p-4">
                      {college2.website ? (
                        <a href={college2.website.startsWith('http') ? college2.website : `https://${college2.website}`} target="_blank" rel="noreferrer" className="text-emerald-400 hover:underline text-xs flex items-center gap-1">
                          Visit College Website ↗
                        </a>
                      ) : 'N/A'}
                    </td>
                  </tr>

                </tbody>
              </table>
            </div>
          </div>

          {/* Section 3: Multi-Year Cutoff History Trend */}
          <div className="glass-card rounded-2xl p-6 border border-[#334155]/60">
            <h3 className="text-base font-bold text-white mb-2 flex items-center gap-2">
              <span>📈</span> 3-Year Historical Cutoff Trend for {selectedCategory}
            </h3>
            <p className="text-xs text-[#94a3b8] mb-4">
              Comparing cutoff consistency between {selectedBranch1} ({college1.name}) and {selectedBranch2} ({college2.name}).
            </p>

            {historicalTrend.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-sm text-left">
                  <thead>
                    <tr className="border-b border-[#334155] text-xs font-bold text-[#94a3b8] uppercase">
                      <th className="py-2.5 px-3">Year & Round</th>
                      <th className="py-2.5 px-3 text-blue-400">College 1 ({college1.name.slice(0, 20)}...)</th>
                      <th className="py-2.5 px-3 text-emerald-400">College 2 ({college2.name.slice(0, 20)}...)</th>
                      <th className="py-2.5 px-3 text-right">Cutoff Gap</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#1e293b]">
                    {historicalTrend.map((row, idx) => (
                      <tr key={idx} className="hover:bg-white/[0.02]">
                        <td className="py-2.5 px-3 font-semibold text-white">
                          {row.year} — Round {row.round}
                        </td>
                        <td className="py-2.5 px-3 font-bold text-blue-300">
                          {row.p1 !== null ? `${row.p1}%` : '—'}
                        </td>
                        <td className="py-2.5 px-3 font-bold text-emerald-300">
                          {row.p2 !== null ? `${row.p2}%` : '—'}
                        </td>
                        <td className="py-2.5 px-3 text-right font-bold">
                          {row.diff !== null ? (
                            <span className={row.diff > 0 ? 'text-blue-400' : row.diff < 0 ? 'text-emerald-400' : 'text-gray-400'}>
                              {row.diff > 0 ? `+${row.diff}% Col 1` : `${row.diff}% Col 2`}
                            </span>
                          ) : '—'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center py-6 text-xs text-[#64748b]">
                No historical cutoff trend records found for this combination of branch & category.
              </div>
            )}
          </div>

          {/* Section 4: Branch Offerings Breakdown */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="glass-card rounded-2xl p-5 border border-[#334155]/60 space-y-3">
              <h4 className="text-sm font-bold text-white flex items-center justify-between">
                <span>All Branches in {college1.name.slice(0, 25)}...</span>
                <span className="text-xs text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded-full font-bold">
                  {branches1.length}
                </span>
              </h4>
              <div className="flex flex-wrap gap-1.5 max-h-48 overflow-y-auto custom-scrollbar p-1">
                {branches1.map((b, i) => (
                  <span 
                    key={i} 
                    className={`text-xs px-2.5 py-1 rounded-lg border font-medium ${
                      branches2.includes(b)
                        ? 'bg-[#0f172a] text-[#cbd5e1] border-[#334155]'
                        : 'bg-blue-500/10 text-blue-300 border-blue-500/30'
                    }`}
                  >
                    {b} {!branches2.includes(b) && '★ (Unique)'}
                  </span>
                ))}
              </div>
            </div>

            <div className="glass-card rounded-2xl p-5 border border-[#334155]/60 space-y-3">
              <h4 className="text-sm font-bold text-white flex items-center justify-between">
                <span>All Branches in {college2.name.slice(0, 25)}...</span>
                <span className="text-xs text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full font-bold">
                  {branches2.length}
                </span>
              </h4>
              <div className="flex flex-wrap gap-1.5 max-h-48 overflow-y-auto custom-scrollbar p-1">
                {branches2.map((b, i) => (
                  <span 
                    key={i} 
                    className={`text-xs px-2.5 py-1 rounded-lg border font-medium ${
                      branches1.includes(b)
                        ? 'bg-[#0f172a] text-[#cbd5e1] border-[#334155]'
                        : 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30'
                    }`}
                  >
                    {b} {!branches1.includes(b) && '★ (Unique)'}
                  </span>
                ))}
              </div>
            </div>
          </div>

        </div>
      ) : (
        /* Empty State: Prompt Student to Pick Colleges */
        <div className="glass-card rounded-2xl p-12 text-center border border-[#334155]/40 space-y-4">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500/20 to-emerald-500/20 border border-[#334155] mx-auto flex items-center justify-center text-3xl shadow-lg shadow-blue-500/10">
            ⚖️
          </div>
          <h2 className="text-lg font-bold text-white">Select Two Colleges to Begin Comparison</h2>
          <p className="text-sm text-[#94a3b8] max-w-md mx-auto">
            Choose College 1 and College 2 using the search boxes above, or tap one of the quick battles (e.g., <button onClick={() => loadPreset(PRESET_BATTLES[0])} className="text-blue-400 hover:underline font-semibold">PCCOE vs VIIT</button>).
          </p>
        </div>
      )}

    </div>
  );
}
