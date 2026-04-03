import { getAuthors, getCenturyLabel } from "@/lib/data";

export default function AuthorsPage() {
  const authors = getAuthors().filter((a) => !a.is_editor);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-stone-800">Church Fathers</h1>
        <p className="mt-2 text-stone-500">
          {authors.length} Church Fathers with tagged Scripture citations, ranked by total citation
          count.
        </p>
      </div>

      <div className="bg-white rounded-xl border border-stone-200 overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-stone-100 text-stone-500 text-xs uppercase tracking-wide">
              <th className="text-left px-4 py-3 font-medium">#</th>
              <th className="text-left px-4 py-3 font-medium">Father</th>
              <th className="text-left px-4 py-3 font-medium hidden sm:table-cell">Era</th>
              <th className="text-right px-4 py-3 font-medium">Citations</th>
              <th className="text-right px-4 py-3 font-medium">Books</th>
              <th className="text-right px-4 py-3 font-medium hidden md:table-cell">Deut.</th>
              <th className="px-4 py-3 hidden lg:table-cell w-36">Top books</th>
            </tr>
          </thead>
          <tbody>
            {authors.map((author, i) => (
              <tr
                key={author.author_id}
                className={`border-b border-stone-50 ${i % 2 === 0 ? "" : "bg-stone-50/50"}`}
              >
                <td className="px-4 py-2.5 text-stone-400 tabular-nums">{i + 1}</td>
                <td className="px-4 py-2.5">
                  <div className="font-medium text-stone-700">{author.display_name}</div>
                  {author.floruit && (
                    <div className="text-xs text-stone-400">fl. {author.floruit} CE</div>
                  )}
                </td>
                <td className="px-4 py-2.5 text-stone-500 hidden sm:table-cell">
                  {getCenturyLabel(author.century)}
                </td>
                <td className="px-4 py-2.5 text-right tabular-nums font-medium text-stone-600">
                  {author.total_citations.toLocaleString()}
                </td>
                <td className="px-4 py-2.5 text-right tabular-nums text-stone-500">
                  {author.unique_books}
                </td>
                <td className="px-4 py-2.5 text-right hidden md:table-cell">
                  {author.quoted_deuterocanonical ? (
                    <span className="text-emerald-600 font-medium">
                      {author.deuterocanonical_books_cited}
                    </span>
                  ) : (
                    <span className="text-stone-300">—</span>
                  )}
                </td>
                <td className="px-4 py-2.5 hidden lg:table-cell">
                  <div className="flex flex-wrap gap-1">
                    {author.top_books.slice(0, 3).map(({ book, display_name }) => (
                      <span
                        key={book}
                        className="bg-stone-100 text-stone-600 text-xs px-1.5 py-0.5 rounded"
                        title={display_name}
                      >
                        {book}
                      </span>
                    ))}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
