import { getBooks, getTestamentLabel } from "@/lib/data";

const TESTAMENT_ORDER = ["new_testament", "old_testament_or_other", "deuterocanonical"] as const;

const TESTAMENT_COLORS: Record<string, string> = {
  new_testament: "bg-blue-100 text-blue-800",
  old_testament_or_other: "bg-amber-100 text-amber-800",
  deuterocanonical: "bg-emerald-100 text-emerald-800",
};

export default function BooksPage() {
  const allBooks = getBooks().filter((b) => b.total_count > 0);
  const maxCount = Math.max(...allBooks.map((b) => b.total_count));

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-stone-800">Biblical Books</h1>
        <p className="mt-2 text-stone-500">
          All {allBooks.length} biblical books cited in the corpus, ranked by total citation count.
        </p>
      </div>

      {TESTAMENT_ORDER.map((group) => {
        const books = allBooks
          .filter((b) => b.testament_group === group)
          .sort((a, b) => b.total_count - a.total_count);
        if (books.length === 0) return null;
        return (
          <section key={group}>
            <h2 className="text-lg font-semibold text-stone-700 mb-3">
              {getTestamentLabel(group)}{" "}
              <span className="text-stone-400 font-normal text-sm">({books.length} books)</span>
            </h2>
            <div className="bg-white rounded-xl border border-stone-200 overflow-hidden">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-stone-100 text-stone-500 text-xs uppercase tracking-wide">
                    <th className="text-left px-4 py-3 font-medium">Book</th>
                    <th className="text-right px-4 py-3 font-medium">Citations</th>
                    <th className="px-4 py-3 w-48 hidden sm:table-cell"></th>
                  </tr>
                </thead>
                <tbody>
                  {books.map((book, i) => (
                    <tr
                      key={book.book}
                      className={`border-b border-stone-50 ${i % 2 === 0 ? "" : "bg-stone-50/50"}`}
                    >
                      <td className="px-4 py-2.5 font-medium text-stone-700">
                        {book.display_name}
                        <span className="ml-2 text-xs text-stone-400">{book.book}</span>
                      </td>
                      <td className="px-4 py-2.5 text-right text-stone-600 tabular-nums">
                        {book.total_count.toLocaleString()}
                      </td>
                      <td className="px-4 py-2.5 hidden sm:table-cell">
                        <div className="h-2 bg-stone-100 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full ${
                              group === "new_testament"
                                ? "bg-blue-400"
                                : group === "deuterocanonical"
                                ? "bg-emerald-400"
                                : "bg-amber-400"
                            }`}
                            style={{ width: `${(book.total_count / maxCount) * 100}%` }}
                          />
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        );
      })}
    </div>
  );
}
