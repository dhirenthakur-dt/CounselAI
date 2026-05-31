import { useState, useRef, useEffect } from 'react';
import { counselStudent } from '../api';
import CollegeCard from './CollegeCard';
import DocumentList from './DocumentList';
import ReactMarkdown from 'react-markdown';

const EXAMPLES = [
  "87 percentile, OBC, Nashik, want CS or IT",
  "95 percentile, General, Pune, Computer Science",
  "92 percentile, SC category, Nagpur, any branch",
];

function TypingIndicator() {
  return (
    <div className="flex items-start gap-3">
      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center flex-shrink-0 text-xs font-bold text-white">
        C
      </div>
      <div className="bg-[#1a1f2e] border border-[#2d3748] rounded-2xl rounded-tl-sm px-4 py-3">
        <div className="flex gap-1.5 items-center h-4">
          <div className="typing-dot"/>
          <div className="typing-dot"/>
          <div className="typing-dot"/>
          <span className="text-[11px] text-gray-500 ml-1">Analysing your profile...</span>
        </div>
      </div>
    </div>
  );
}

function UserMessage({ text }) {
  return (
    <div className="flex justify-end msg-enter">
      <div className="max-w-sm bg-blue-600 text-white rounded-2xl rounded-tr-sm px-4 py-2.5 text-sm leading-relaxed">
        {text}
      </div>
    </div>
  );
}

function BotMessage({ msg }) {
  return (
    <div className="flex items-start gap-3 msg-enter">
      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center flex-shrink-0 text-xs font-bold text-white mt-0.5">
        C
      </div>
      <div className="flex-1 min-w-0">
        {/* Main response */}
        <div className="bg-[#1a1f2e] border border-[#2d3748] rounded-2xl rounded-tl-sm px-4 py-3">
          <div className="prose text-sm text-gray-300">
            <ReactMarkdown>{msg.text}</ReactMarkdown>
          </div>
        </div>

        {/* College cards */}
        {msg.colleges?.length > 0 && (
          <div className="mt-3">
            <p className="text-[11px] text-gray-500 font-semibold uppercase tracking-wider mb-2 ml-1">
              🎓 College Matches
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {msg.colleges.map((c, i) => (
                <CollegeCard key={i} college={c} rank={i + 1} />
              ))}
            </div>
          </div>
        )}

        {/* Document checklist */}
        {msg.documents && <DocumentList documents={msg.documents} />}
      </div>
    </div>
  );
}

export default function Chat() {
  const [messages, setMessages]   = useState([]);
  const [input, setInput]         = useState('');
  const [loading, setLoading]     = useState(false);
  const bottomRef                 = useRef(null);
  const inputRef                  = useRef(null);

  useEffect(() => {
    setMessages([{
      role: 'bot',
      text: `👋 Hi! I'm **CounselAI** — your free MHT-CET admission counsellor.

Tell me your **percentile**, **category**, **district**, and **branch preference** and I'll give you a personalised college shortlist with CAP Round strategy.`,
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

    try {
      const data = await counselStudent(msg);
      setMessages(prev => [...prev, {
        role:      'bot',
        text:      data.response || 'Sorry, something went wrong.',
        colleges:  data.colleges,
        documents: data.documents,
      }]);
    } catch {
      setMessages(prev => [...prev, {
        role: 'bot',
        text: '❌ Could not connect to the server. Make sure both services are running on ports 8080 and 8001.',
      }]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-3xl mx-auto">

      {/* ── Header ── */}
      <div className="flex items-center gap-3 px-5 py-4 border-b border-[#2d3748] bg-[#0f1117]">
        <div className="w-9 h-9 rounded-full bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center font-bold text-white">
          C
        </div>
        <div>
          <h1 className="font-bold text-gray-100 text-sm">CounselAI</h1>
          <p className="text-[11px] text-gray-500">MHT-CET Admission Counsellor</p>
        </div>
        <div className="ml-auto flex items-center gap-1.5">
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"/>
          <span className="text-[11px] text-gray-500">Online</span>
        </div>
      </div>

      {/* ── Messages ── */}
      <div className="flex-1 overflow-y-auto px-4 py-5 space-y-5">
        {messages.map((msg, i) =>
          msg.role === 'user'
            ? <UserMessage key={i} text={msg.text} />
            : <BotMessage key={i} msg={msg} />
        )}
        {loading && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>

      {/* ── Examples ── */}
      {messages.length <= 1 && !loading && (
        <div className="px-4 pb-2">
          <p className="text-[11px] text-gray-600 mb-2">Try an example:</p>
          <div className="flex flex-wrap gap-2">
            {EXAMPLES.map((e, i) => (
              <button
                key={i}
                onClick={() => send(e)}
                className="text-[12px] border border-[#2d3748] text-gray-400 hover:text-blue-400 hover:border-blue-500/40 px-3 py-1.5 rounded-full transition-all"
              >
                {e}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* ── Input ── */}
      <div className="px-4 py-3 border-t border-[#2d3748] bg-[#0f1117]">
        <div className="flex gap-2 items-end">
          <textarea
            ref={inputRef}
            rows={1}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKey}
            placeholder="Type your percentile, category, district, branch..."
            disabled={loading}
            className="flex-1 bg-[#1a1f2e] border border-[#2d3748] rounded-xl px-4 py-2.5 text-sm text-gray-200 placeholder-gray-600 resize-none focus:outline-none focus:border-blue-500/50 transition-colors disabled:opacity-50"
            style={{ maxHeight: '120px' }}
            onInput={e => {
              e.target.style.height = 'auto';
              e.target.style.height = e.target.scrollHeight + 'px';
            }}
          />
          <button
            onClick={() => send()}
            disabled={loading || !input.trim()}
            className="bg-blue-600 hover:bg-blue-500 disabled:bg-[#1a1f2e] disabled:text-gray-600 text-white px-4 py-2.5 rounded-xl text-sm font-medium transition-all disabled:cursor-not-allowed flex-shrink-0"
          >
            {loading ? '...' : 'Send'}
          </button>
        </div>
        <p className="text-[11px] text-gray-600 mt-1.5 ml-1">
          Press Enter to send · Shift+Enter for new line
        </p>
      </div>
    </div>
  );
}