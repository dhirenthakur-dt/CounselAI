export default function DocumentList({ documents }) {
  if (!documents || documents.error) return null;

  return (
    <div className="mt-3 bg-[#1a1f2e] border border-[#2d3748] rounded-xl p-4">
      <div className="flex items-center gap-2 mb-3">
        <span className="text-sm font-semibold text-gray-200">📋 Documents Needed</span>
        <span className="text-[11px] bg-blue-500/10 text-blue-400 border border-blue-500/20 px-2 py-0.5 rounded-full">
          {documents.mandatoryCount} required
        </span>
      </div>

      {/* Warnings */}
      {documents.warnings?.length > 0 && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 mb-3">
          {documents.warnings.map((w, i) => (
            <p key={i} className="text-[12px] text-red-400 font-medium">{w}</p>
          ))}
        </div>
      )}

      {/* Document list */}
      <div className="space-y-2">
        {documents.mandatory?.map((doc, i) => (
          <label key={i} className="flex items-start gap-2.5 cursor-pointer group">
            <input
              type="checkbox"
              className="mt-0.5 w-3.5 h-3.5 accent-blue-500 flex-shrink-0"
            />
            <div>
              <p className="text-[12px] text-gray-300 group-hover:text-white transition-colors">
                {doc.documentName}
              </p>
              {doc.notes && (
                <p className="text-[11px] text-gray-500 mt-0.5">{doc.notes}</p>
              )}
            </div>
          </label>
        ))}
      </div>
    </div>
  );
}