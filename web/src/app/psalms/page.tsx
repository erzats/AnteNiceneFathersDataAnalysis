import { getPsalms } from "@/lib/data";

export default function PsalmsPage() {
  const psalms = getPsalms();
  const maxCount = psalms[0]?.count ?? 1;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-stone-800">Psalm Citations</h1>
        <p className="mt-2 text-stone-500">
          {psalms.length} individual Psalms cited across the corpus, ranked by frequency.
        </p>
      </div>

      <div className="bg-white rounded-xl border border-stone-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-stone-100 text-stone-500 text-xs uppercase tracking-wide">
              <th className="text-left px-4 py-3 font-medium">#</th>
              <th className="text-left px-4 py-3 font-medium">Psalm</th>
              <th className="text-right px-4 py-3 font-medium">Citations</th>
              <th className="px-4 py-3 w-64 hidden sm:table-cell"></th>
            </tr>
          </thead>
          <tbody>
            {psalms.map(({ psalm, count }, i) => (
              <tr
                key={psalm}
                className={`border-b border-stone-50 ${i % 2 === 0 ? "" : "bg-stone-50/50"}`}
              >
                <td className="px-4 py-2.5 text-stone-400 tabular-nums">{i + 1}</td>
                <td className="px-4 py-2.5 font-medium text-stone-700">Psalm {psalm}</td>
                <td className="px-4 py-2.5 text-right tabular-nums font-medium text-stone-600">
                  {count}
                </td>
                <td className="px-4 py-2.5 hidden sm:table-cell">
                  <div className="h-2 bg-stone-100 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-amber-400 rounded-full"
                      style={{ width: `${(count / maxCount) * 100}%` }}
                    />
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
