import { useState, useRef, useEffect } from 'react';
import { counselStudent } from '../api';
import CollegeCard from './CollegeCard';
import DocumentList from './DocumentList';
import ReactMarkdown from 'react-markdown';

const EXAMPLES = [
  { icon: '🎯', text: '87 percentile, OBC, Nashik, CS or IT' },
  { icon: '🏛️', text: '95 percentile, General, Pune, Computer Science' },
  { icon: '📚', text: '92 percentile, SC, Nagpur, AI or Data Science' },
];

function Avatar({ letter = 'C', size = 'w-9 h-9' }) {
  return (
    <div className={`${size} rounded-xl bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center font-bold text-white text-[13px] flex-shrink-0 shadow-lg shadow-blue-500/20`}>
      {letter}
    </div>
  );
}

function TypingBubble() {
  return (
    <div className="flex items-start gap-3 fade-in">
      <Avatar />
      <div className="bg-[#111827] border border-[#374151] rounded-2xl rounded-tl-sm px-4 py-3.5">
        <div className="flex gap-1.5 items-center">
          <div className="typing-dot" />
          <div className="typing-dot" />
          <div className="typing-dot" />
          <span className="text-[11px] text-[#6b7280] ml-2 font-medium">Analysing your profile...</span>
        </div>
      </div>
    </div>
  );
}

function ProfileChip({ label, value }) {
  if (!value) return null;
  return (
    <span className="inline-flex items-center gap-1.5 text-[11px] bg-[#1f2937] border border-[#374151] text-[#9ca3af] px-2.5 py-1 rounded-full">
      <span className="text-[#6b7280]">{label}</span>
      <span className="text-white font-medium">{value}</span>
    </span>
  );
}

export default function Chat() {
  const [messages, setMessages]       = useState([]);
  const [input, setInput]             = useState('');
  const [loading, setLoading]         = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const bottomRef                     = useRef(null);
  const inputRef                      = useRef(null);

  useEffect(() => {
    setMessages([{
      role: 'bot',
      text: `## Welcome to CounselAI 👋\n\nI'm your personal **MHT-CET admission counsellor** — powered by AI and real DTE Maharashtra data.\n\nTell me your **percentile**, **category**, **district**, and **branch preference** and I'll give you:\n- Personalised college shortlist with chance level\n- CAP Round strategy (which round to lock seat)\n- Live fee and hostel data on demand\n- Category-specific document checklist`,
    }]);
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const send = async (text) => {
    const msg = (text || input).trim();
    if (!msg || loading) return;
    setMessages(prev => [...prev, { role: 'user', text: msg }]);
    setInput('');
    setLoading(true);
    setSidebarOpen(false);
    try {
      const data = await counselStudent(msg);
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
    <div className="flex h-screen bg-[#0a0e1a]">

      {/* ── Mobile sidebar overlay ── */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/60 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* ── Sidebar ── */}
      <div className={`
        fixed lg:relative z-50 lg:z-auto
        flex flex-col w-72 border-r border-[#374151] bg-[#0d1117] p-5
        transition-transform duration-300 h-full
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        lg:flex
      `}>
        {/* Logo */}
        <div className="flex items-center gap-3 mb-8">
          <Avatar size="w-10 h-10" />
          <div>
            <h1 className="font-bold text-white text-[15px]">CounselAI</h1>
            <p className="text-[11px] text-[#6b7280]">MHT-CET Counsellor</p>
          </div>
        </div>

        {/* Status */}
        <div className="flex items-center gap-2 mb-6">
          <div className="w-2 h-2 rounded-full bg-emerald-400 pulse-ring" />
          <span className="text-[12px] text-emerald-400 font-medium">All systems online</span>
        </div>

        {/* Capabilities */}
        <div className="mb-6">
          <p className="text-[11px] text-[#6b7280] font-semibold uppercase tracking-wider mb-3">
            What I can help with
          </p>
          {[
            { icon: '🎓', text: 'College shortlist from real DTE data' },
            { icon: '📊', text: '157,206 cutoff records (2022-2024)' },
            { icon: '🗺️', text: 'District-wise college priority' },
            { icon: '📋', text: 'Document checklist with warnings' },
            { icon: '🔍', text: 'Live fee & hostel search' },
            { icon: '⚡', text: 'CAP Round strategy guidance' },
          ].map(({ icon, text }) => (
            <div key={text} className="flex items-center gap-2.5 py-2 group">
              <span className="text-[14px] group-hover:scale-110 transition-transform">{icon}</span>
              <span className="text-[12px] text-[#9ca3af] group-hover:text-white transition-colors">{text}</span>
            </div>
          ))}
        </div>

        {/* Example queries */}
        <div className="mt-auto">
          <p className="text-[11px] text-[#6b7280] font-semibold uppercase tracking-wider mb-2">
            Try these
          </p>
          {EXAMPLES.map((e, i) => (
            <button
              key={i}
              onClick={() => send(e.text)}
              className="w-full text-left flex items-center gap-2 text-[12px] text-[#9ca3af] hover:text-white hover:bg-[#1f2937] px-3 py-2.5 rounded-xl transition-all duration-200 mb-1"
            >
              <span>{e.icon}</span>
              <span className="line-clamp-1">{e.text}</span>
            </button>
          ))}
        </div>

        {/* Close button (mobile) */}
        <button
          onClick={() => setSidebarOpen(false)}
          className="lg:hidden absolute top-4 right-4 text-[#6b7280] hover:text-white p-1"
        >
          ✕
        </button>
      </div>

      {/* ── Main chat area ── */}
      <div className="flex flex-col flex-1 min-w-0">

        {/* Header */}
        <div className="flex items-center gap-3 px-5 py-4 border-b border-[#374151] bg-[#0d1117]">
          {/* Hamburger for mobile */}
          <button
            onClick={() => setSidebarOpen(true)}
            className="lg:hidden text-[#9ca3af] hover:text-white p-1 -ml-1 mr-1"
          >
            <svg width="20" height="20" fill="none" viewBox="0 0 24 24">
              <path d="M3 6h18M3 12h18M3 18h18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            </svg>
          </button>
          <Avatar size="w-8 h-8" />
          <div className="flex-1">
            <h2 className="text-[14px] font-semibold text-white">CounselAI</h2>
            <p className="text-[11px] text-[#6b7280]">Powered by real DTE Maharashtra data</p>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-emerald-400 pulse-ring" />
            <span className="text-[11px] text-[#6b7280]">Online</span>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-4 lg:px-8 py-6 space-y-6">
          {messages.map((msg, i) => (
            <div key={i}>
              {msg.role === 'user' ? (
                <div className="flex justify-end fade-in">
                  <div className="max-w-lg bg-gradient-to-r from-blue-600 to-blue-500 text-white rounded-2xl rounded-tr-sm px-4 py-3 text-[13px] leading-relaxed shadow-lg shadow-blue-500/10">
                    {msg.text}
                  </div>
                </div>
              ) : (
                <div className="flex items-start gap-3 fade-in">
                  <Avatar />
                  <div className="flex-1 min-w-0">
                    {/* Main response bubble */}
                    <div className="bg-[#111827] border border-[#374151] rounded-2xl rounded-tl-sm px-5 py-4 shadow-sm">
                      <div className="prose text-[13px] text-[#d1d5db]">
                        <ReactMarkdown>{msg.text}</ReactMarkdown>
                      </div>
                    </div>

                    {/* Profile chips */}
                    {msg.profile && msg.profile.percentile && (
                      <div className="flex flex-wrap gap-2 mt-3 ml-1">
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
                      <div className="mt-4">
                        <p className="text-[11px] text-[#6b7280] font-semibold uppercase tracking-wider mb-3 ml-1">
                          🎓 {msg.colleges.length} College Matches
                        </p>
                        <div className="grid grid-cols-1 xl:grid-cols-2 gap-3">
                          {msg.colleges.map((c, j) => (
                            <CollegeCard key={j} college={c} rank={j + 1} />
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Document checklist */}
                    {msg.documents && <DocumentList documents={msg.documents} />}
                  </div>
                </div>
              )}
            </div>
          ))}
          {loading && <TypingBubble />}
          <div ref={bottomRef} />
        </div>

        {/* Input area */}
        <div className="border-t border-[#374151] bg-[#0d1117] px-4 lg:px-8 py-4">
          <div className="max-w-4xl mx-auto">
            <div className="flex gap-3 items-end">
              <div className="flex-1 bg-[#111827] border border-[#374151] rounded-2xl overflow-hidden focus-within:border-blue-500/50 focus-within:shadow-lg focus-within:shadow-blue-500/5 transition-all duration-200">
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
                  className="w-full bg-transparent px-4 py-3.5 text-[13px] text-[#e5e7eb] placeholder-[#6b7280] resize-none focus:outline-none disabled:opacity-50"
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
                className="bg-blue-600 hover:bg-blue-500 disabled:bg-[#1f2937] disabled:text-[#6b7280] text-white w-12 h-12 rounded-2xl font-bold transition-all duration-200 disabled:cursor-not-allowed flex items-center justify-center shadow-lg shadow-blue-500/20 flex-shrink-0 hover:glow-blue active:scale-95"
              >
                {loading ? (
                  <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  <svg width="18" height="18" fill="none" viewBox="0 0 24 24">
                    <path d="M22 2L11 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                    <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                )}
              </button>
            </div>
            <div className="flex items-center justify-between mt-2.5 px-1">
              <p className="text-[11px] text-[#6b7280]">
                Enter to send · Shift+Enter for new line
              </p>
              <p className="text-[11px] text-[#6b7280]">
                157k+ DTE cutoff records · 692 colleges
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}