export default function DocumentList({ documents }) {
  if (!documents || documents.error) return null;

  return (
    <div className="mt-4 rounded-2xl border border-[#374151] bg-[#111827] overflow-hidden fade-in">
      {/* Header */}
      <div className="px-5 py-4 border-b border-[#374151] flex items-center justify-between">
        <h3 className="text-[13px] font-semibold text-white flex items-center gap-2">
          📋 Documents Required
        </h3>
        <span className="text-[11px] bg-blue-500/10 text-blue-400 border border-blue-500/20 px-2.5 py-1 rounded-full font-medium">
          {documents.mandatoryCount} required
        </span>
      </div>

      {/* Warnings */}
      {documents.warnings?.length > 0 && (
        <div className="mx-4 mt-4 bg-red-500/10 border border-red-500/20 rounded-xl p-3">
          {documents.warnings.map((w, i) => (
            <p key={i} className="text-[12px] text-red-400 font-medium flex items-start gap-2">
              <span className="flex-shrink-0 mt-0.5">⚠️</span>
              <span>{w}</span>
            </p>
          ))}
        </div>
      )}

      {/* Document checklist */}
      <div className="p-4 space-y-2.5">
        {documents.mandatory?.map((doc, i) => (
          <label key={i} className="flex items-start gap-3 cursor-pointer group hover:bg-[#1f2937]/50 px-2 py-1.5 rounded-xl transition-colors">
            <input
              type="checkbox"
              className="mt-0.5 w-4 h-4 accent-blue-500 flex-shrink-0"
            />
            <div>
              <p className="text-[12px] text-[#e5e7eb] group-hover:text-white transition-colors font-medium">
                {doc.documentName}
              </p>
              {doc.notes && (
                <p className="text-[11px] text-[#6b7280] mt-0.5">{doc.notes}</p>
              )}
            </div>
          </label>
        ))}
      </div>

      {/* Optional documents */}
      {documents.optional?.length > 0 && (
        <div className="px-4 pb-4">
          <p className="text-[11px] text-[#6b7280] font-semibold uppercase tracking-wider mb-2 mt-1">
            Optional Documents
          </p>
          <div className="space-y-2">
            {documents.optional.map((doc, i) => (
              <label key={i} className="flex items-start gap-3 cursor-pointer group hover:bg-[#1f2937]/50 px-2 py-1.5 rounded-xl transition-colors">
                <input
                  type="checkbox"
                  className="mt-0.5 w-4 h-4 accent-[#6b7280] flex-shrink-0"
                />
                <div>
                  <p className="text-[12px] text-[#9ca3af] group-hover:text-[#e5e7eb] transition-colors">
                    {doc.documentName}
                  </p>
                  {doc.notes && (
                    <p className="text-[11px] text-[#6b7280] mt-0.5">{doc.notes}</p>
                  )}
                </div>
              </label>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}