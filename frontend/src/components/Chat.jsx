import { useState, useRef, useEffect } from 'react';
import { counselStudent, followUpQuestion } from '../api';
import CollegeCard from './CollegeCard';
import DocumentList from './DocumentList';
import ExploreColleges from './ExploreColleges';
import ReactMarkdown from 'react-markdown';

const EXAMPLES = [
  { icon: '🎯', text: '87 percentile, OBC, Nashik, CS or IT' },
  { icon: '🏛️', text: '95 percentile, General, Pune, Computer Science' },
  { icon: '📚', text: '92 percentile, SC, Nagpur, AI or Data Science' },
];

function Avatar({ letter = 'C', size = 'w-9 h-9' }) {
  return (
    <div className={`${size} rounded-xl bg-gradient-to-br from-blue-500 to-emerald-500 flex items-center justify-center font-bold text-white text-[13px] flex-shrink-0 shadow-lg shadow-blue-500/30`}>
      {letter}
    </div>
  );
}

function TypingBubble() {
  return (
    <div className="flex items-start gap-3 fade-in">
      <Avatar />
      <div className="glass-card rounded-2xl rounded-tl-sm px-4 py-3.5 border-l-2 border-l-blue-500">
        <div className="flex gap-1.5 items-center">
          <div className="typing-dot bg-blue-400" />
          <div className="typing-dot bg-blue-400" />
          <div className="typing-dot bg-blue-400" />
          <span className="text-[11px] text-blue-300 ml-2 font-medium">Analysing your profile...</span>
        </div>
      </div>
    </div>
  );
}

function ProfileChip({ label, value }) {
  if (!value) return null;
  return (
    <span className="inline-flex items-center gap-1.5 text-[11px] bg-[#0f172a] border border-[#334155] text-[#94a3b8] px-2.5 py-1 rounded-full shadow-inner">
      <span className="text-[#64748b] font-medium">{label}</span>
      <span className="text-white font-semibold">{value}</span>
    </span>
  );
}

export default function Chat() {
  const [activeTab, setActiveTab]     = useState('chat');
  const [messages, setMessages]       = useState([]);
  const [input, setInput]             = useState('');
  const [loading, setLoading]         = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [lastResult, setLastResult]   = useState(null);
  const bottomRef                     = useRef(null);
  const inputRef                      = useRef(null);

  // Helper to check if message contains percentile/profile data
  const hasProfileData = (text) => {
    return /\b\d{1,2}(\.\d+)?\s*(percentile|%)\b/i.test(text) || /\b(obc|sc|st|ews|open|general)\b/i.test(text);
  };

  useEffect(() => {
    setMessages([{
      role: 'bot',
      text: `## Welcome to CounselAI 👋\n\nI'm your personal **MHT-CET admission counsellor** — powered by AI and real DTE Maharashtra data.\n\nTell me your **percentile**, **category**, **district**, and **branch preference** and I'll give you:\n- Personalised college shortlist with chance level\n- CAP Round strategy (which round to lock seat)\n- Live fee and hostel data on demand\n- Category-specific document checklist`,
    }]);
  }, []);

  useEffect(() => {
    if (activeTab === 'chat') {
      bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, loading, activeTab]);

  const send = async (text) => {
    const msg = (text || input).trim();
    if (!msg || loading) return;
    setActiveTab('chat');
    setMessages(prev => [...prev, { role: 'user', text: msg }]);
    setInput('');
    setLoading(true);
    setSidebarOpen(false);
    try {
      let data;
      // If no new profile data is detected and we have a previous result, treat as follow-up
      if (!hasProfileData(msg) && lastResult) {
        data = await followUpQuestion(msg, lastResult.profile, lastResult.colleges);
      } else {
        // Fresh counseling query
        data = await counselStudent(msg);
        if (data.profile && data.colleges?.length > 0) {
          setLastResult({ profile: data.profile, colleges: data.colleges });
        }
      }

      setMessages(prev => [...prev, {
        role: 'bot',
        text: data.response || 'Sorry, something went wrong.',
        colleges: data.colleges,
        documents: data.documents,
        profile: data.profile,
      }]);
    } catch {
      setMessages(prev => [...prev, {
        role: 'bot',
        text: '❌ Connection failed. Make sure services are running on ports 8080 and 8001.',
      }]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  return (
    <div className="flex h-screen bg-[#030712] relative z-10 overflow-hidden font-sans">
      
      {/* ── Dynamic Background Orbs ── */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="bg-orb-1" />
        <div className="bg-orb-2" />
      </div>

      {/* ── Mobile sidebar overlay ── */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/80 backdrop-blur-sm z-40 lg:hidden transition-opacity"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* ── Sidebar ── */}
      <div className={`
        fixed lg:relative z-50 lg:z-10
        flex flex-col w-72 border-r border-white/5 bg-[#0a0e1a]/80 backdrop-blur-2xl p-5
        transition-transform duration-300 h-full shadow-2xl
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        lg:flex
      `}>
        {/* Logo */}
        <div className="flex items-center gap-3 mb-8">
          <Avatar size="w-10 h-10" />
          <div>
            <h1 className="font-bold text-white text-[16px] tracking-tight neon-text">CounselAI</h1>
            <p className="text-[11px] text-[#94a3b8] font-medium tracking-wide">MHT-CET ADVISOR</p>
          </div>
        </div>

        {/* Status */}
        <div className="flex items-center gap-2 mb-6 px-1">
          <div className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_8px_#10b981] animate-pulse-slow" />
          <span className="text-[11px] text-emerald-400 font-semibold uppercase tracking-wider">System Online</span>
        </div>

        {/* Navigation Tabs */}
        <div className="flex flex-col gap-2 mb-8">
          <button
            onClick={() => setActiveTab('chat')}
            className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 ${
              activeTab === 'chat' 
                ? 'bg-blue-500/10 text-blue-400 shadow-[0_0_20px_rgba(59,130,246,0.15)] border border-blue-500/20' 
                : 'text-[#94a3b8] hover:bg-white/5 hover:text-white border border-transparent'
            }`}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path></svg>
            <span className="font-semibold text-sm tracking-wide">AI Counselor</span>
          </button>

          <button
            onClick={() => setActiveTab('explore')}
            className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 ${
              activeTab === 'explore' 
                ? 'bg-emerald-500/10 text-emerald-400 shadow-[0_0_20px_rgba(16,185,129,0.15)] border border-emerald-500/20' 
                : 'text-[#94a3b8] hover:bg-white/5 hover:text-white border border-transparent'
            }`}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
            <span className="font-semibold text-sm tracking-wide">Explore Colleges</span>
          </button>
        </div>

        {/* Example queries (only relevant for chat) */}
        <div className="mt-auto">
          <p className="text-[10px] text-[#64748b] font-bold uppercase tracking-widest mb-3 px-1">
            Try AI Prompts
          </p>
          {EXAMPLES.map((e, i) => (
            <button
              key={i}
              onClick={() => send(e.text)}
              className="w-full text-left flex items-center gap-3 text-[12px] text-[#94a3b8] hover:text-white hover:bg-white/5 px-3 py-3 rounded-xl transition-all duration-200 mb-1.5 border border-transparent hover:border-white/10"
            >
              <span className="text-[14px] opacity-80">{e.icon}</span>
              <span className="line-clamp-1 font-medium">{e.text}</span>
            </button>
          ))}
        </div>

        {/* Close button (mobile) */}
        <button
          onClick={() => setSidebarOpen(false)}
          className="lg:hidden absolute top-4 right-4 text-[#64748b] hover:text-white p-2 rounded-lg bg-white/5"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>
      </div>

      {/* ── Main content area ── */}
      <div className="flex flex-col flex-1 min-w-0 z-10">
        
        {/* Top bar for mobile */}
        <div className="lg:hidden flex items-center gap-3 px-5 py-4 border-b border-white/5 bg-[#0a0e1a]/80 backdrop-blur-md">
          <button onClick={() => setSidebarOpen(true)} className="text-[#94a3b8] hover:text-white p-1 -ml-1 mr-1">
            <svg width="20" height="20" fill="none" viewBox="0 0 24 24"><path d="M4 6h16M4 12h16M4 18h16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" /></svg>
          </button>
          <h2 className="text-[15px] font-bold text-white tracking-tight">{activeTab === 'chat' ? 'AI Counselor' : 'Explore Colleges'}</h2>
        </div>

        {activeTab === 'explore' ? (
          <ExploreColleges />
        ) : (
          <>
            {/* Messages */}
            <div className="flex-1 overflow-y-auto px-4 md:px-8 py-8 space-y-8 scroll-smooth">
              {messages.map((msg, i) => (
                <div key={i}>
                  {msg.role === 'user' ? (
                    <div className="flex justify-end fade-in">
                      <div className="max-w-[85%] md:max-w-xl bg-gradient-to-br from-blue-600 to-blue-500 text-white rounded-2xl rounded-tr-sm px-5 py-3.5 text-[14px] leading-relaxed shadow-lg shadow-blue-500/20 font-medium">
                        {msg.text}
                      </div>
                    </div>
                  ) : (
                    <div className="flex items-start gap-4 fade-in">
                      <Avatar />
                      <div className="flex-1 min-w-0">
                        {/* Main response bubble */}
                        <div className="glass-card rounded-2xl rounded-tl-sm px-6 py-5">
                          <div className="prose prose-invert prose-p:text-[#cbd5e1] prose-h2:text-blue-400 prose-strong:text-white prose-li:text-[#cbd5e1] max-w-none text-[14px]">
                            <ReactMarkdown>{msg.text}</ReactMarkdown>
                          </div>
                        </div>

                        {/* Profile chips */}
                        {msg.profile && msg.profile.percentile && (
                          <div className="flex flex-wrap gap-2 mt-4 ml-1">
                            <ProfileChip label="Percentile" value={msg.profile.percentile} />
                            <ProfileChip label="Category" value={msg.profile.category} />
                            <ProfileChip label="District" value={msg.profile.district} />
                            {msg.profile.branches?.length > 0 && (
                              <ProfileChip label="Branch" value={msg.profile.branches.join(', ')} />
                            )}
                          </div>
                        )}

                        {/* College cards grid */}
                        {msg.colleges?.length > 0 && (
                          <div className="mt-6">
                            <div className="flex items-center gap-3 mb-4 ml-1">
                              <span className="w-8 h-[1px] bg-emerald-500/30" />
                              <p className="text-[10px] text-emerald-400 font-bold uppercase tracking-widest">
                                {msg.colleges.length} Recommended Colleges
                              </p>
                              <span className="flex-1 h-[1px] bg-emerald-500/10" />
                            </div>
                            <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
                              {msg.colleges.map((c, j) => (
                                <CollegeCard key={j} college={c} rank={j + 1} />
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Document checklist */}
                        {msg.documents && (
                          <div className="mt-6">
                            <DocumentList documents={msg.documents} />
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              ))}
              {loading && <TypingBubble />}
              <div ref={bottomRef} className="h-4" />
            </div>

            {/* Input area */}
            <div className="border-t border-white/5 bg-[#0a0e1a]/80 backdrop-blur-xl px-4 md:px-8 py-5">
              <div className="max-w-4xl mx-auto">
                <div className="flex gap-3 items-end neon-border p-1 rounded-3xl">
                  <div className="flex-1 bg-[#0f172a] border border-[#1e293b] rounded-2xl overflow-hidden focus-within:border-blue-500/50 focus-within:shadow-[0_0_15px_rgba(59,130,246,0.1)] transition-all duration-300">
                    <textarea
                      ref={inputRef}
                      rows={1}
                      value={input}
                      onChange={e => setInput(e.target.value)}
                      onKeyDown={e => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                          e.preventDefault();
                          send();
                        }
                      }}
                      placeholder="Type your percentile, category, district, branch..."
                      disabled={loading}
                      className="w-full bg-transparent px-5 py-4 text-[14px] text-white placeholder-[#475569] resize-none focus:outline-none disabled:opacity-50 font-medium leading-relaxed"
                      style={{ maxHeight: '120px' }}
                      onInput={e => {
                        e.target.style.height = 'auto';
                        e.target.style.height = e.target.scrollHeight + 'px';
                      }}
                    />
                  </div>
                  <button
                    onClick={() => send()}
                    disabled={loading || !input.trim()}
                    className="bg-gradient-to-r from-blue-600 to-emerald-600 hover:from-blue-500 hover:to-emerald-500 disabled:from-[#1e293b] disabled:to-[#1e293b] disabled:text-[#475569] text-white w-14 h-14 rounded-2xl font-bold transition-all duration-300 disabled:cursor-not-allowed flex items-center justify-center shadow-lg shadow-blue-500/20 flex-shrink-0 active:scale-95 group"
                  >
                    {loading ? (
                      <span className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    ) : (
                      <svg width="20" height="20" fill="none" viewBox="0 0 24 24" className="group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform duration-300">
                        <path d="M22 2L11 13" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" />
                        <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                    )}
                  </button>
                </div>
                <div className="flex items-center justify-between mt-3 px-2">
                  <p className="text-[11px] text-[#475569] font-medium">
                    Press <kbd className="bg-[#1e293b] px-1.5 py-0.5 rounded text-[#94a3b8]">Enter</kbd> to send, <kbd className="bg-[#1e293b] px-1.5 py-0.5 rounded text-[#94a3b8]">Shift+Enter</kbd> for line break
                  </p>
                  <p className="text-[11px] text-[#475569] font-medium hidden sm:block">
                    Powered by 157k+ DTE cutoff records
                  </p>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}