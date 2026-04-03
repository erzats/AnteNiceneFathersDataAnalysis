import { getCenturyLabel, getSummary, getTestamentLabel } from "@/lib/data";

export default function HomePage() {
  const summary = getSummary();
  const { total_references, by_testament, unique_authors, unique_books } = summary;

  const testamentRows = [
    { label: "New Testament", count: by_testament.new_testament, color: "bg-blue-500" },
    { label: "Old Testament", count: by_testament.old_testament_or_other, color: "bg-amber-500" },
    { label: "Deuterocanonical", count: by_testament.deuterocanonical, color: "bg-emerald-500" },
  ];

  return (
    <div className="space-y-10">
      <div>
        <h1 className="text-3xl font-bold text-stone-800">Scripture Citation Analysis</h1>
        <p className="mt-2 text-stone-500 max-w-2xl">
          Systematic analysis of every Scripture reference tagged across the nine-volume{" "}
          <em>Ante-Nicene Fathers</em> corpus — Church Fathers writing before the Council of
          Nicaea (325 CE).
        </p>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {[
          { label: "Total Citations", value: total_references.toLocaleString() },
          { label: "Church Fathers", value: unique_authors },
          { label: "Books Cited", value: unique_books },
          { label: "Volumes", value: 9 },
        ].map(({ label, value }) => (
          <div key={label} className="bg-white rounded-xl border border-stone-200 p-5">
            <div className="text-2xl font-bold text-stone-800">{value}</div>
            <div className="text-sm text-stone-500 mt-1">{label}</div>
          </div>
        ))}
      </div>

      {/* Testament breakdown */}
      <div className="bg-white rounded-xl border border-stone-200 p-6">
        <h2 className="font-semibold text-stone-700 mb-4">Citations by Testament</h2>
        <div className="space-y-3">
          {testamentRows.map(({ label, count, color }) => {
            const pct = ((count / total_references) * 100).toFixed(1);
            return (
              <div key={label}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-stone-600">{label}</span>
                  <span className="font-medium text-stone-700">
                    {count.toLocaleString()} <span className="text-stone-400">({pct}%)</span>
                  </span>
                </div>
                <div className="h-2 bg-stone-100 rounded-full overflow-hidden">
                  <div className={`h-full ${color} rounded-full`} style={{ width: `${pct}%` }} />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="grid sm:grid-cols-2 gap-6">
        {/* Top books */}
        <div className="bg-white rounded-xl border border-stone-200 p-6">
          <h2 className="font-semibold text-stone-700 mb-4">Most Cited Books</h2>
          <ol className="space-y-2">
            {summary.top_books.map(({ book, display_name, count }, i) => (
              <li key={book} className="flex items-center gap-3 text-sm">
                <span className="w-5 text-stone-400 text-right shrink-0">{i + 1}.</span>
                <span className="flex-1 text-stone-700">{display_name}</span>
                <span className="font-medium text-stone-600">{count.toLocaleString()}</span>
              </li>
            ))}
          </ol>
        </div>

        {/* Top authors */}
        <div className="bg-white rounded-xl border border-stone-200 p-6">
          <h2 className="font-semibold text-stone-700 mb-4">Most Prolific Church Fathers</h2>
          <ol className="space-y-2">
            {summary.top_authors.map(({ author_id, display_name, count }, i) => (
              <li key={author_id} className="flex items-center gap-3 text-sm">
                <span className="w-5 text-stone-400 text-right shrink-0">{i + 1}.</span>
                <span className="flex-1 text-stone-700">{display_name}</span>
                <span className="font-medium text-stone-600">{count.toLocaleString()}</span>
              </li>
            ))}
          </ol>
        </div>
      </div>

      {/* Unquoted books */}
      {summary.unquoted_books.length > 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-6">
          <h2 className="font-semibold text-amber-800 mb-2">
            Books Never Cited ({summary.unquoted_books.length})
          </h2>
          <p className="text-sm text-amber-700 mb-3">
            These canonical books have no tagged Scripture references anywhere in the corpus.
          </p>
          <div className="flex flex-wrap gap-2">
            {summary.unquoted_books.map(({ book, display_name }) => (
              <span
                key={book}
                className="bg-amber-100 text-amber-800 text-xs px-2 py-1 rounded-md"
              >
                {display_name}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
