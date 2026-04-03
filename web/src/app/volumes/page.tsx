import { getVolumeComparison } from "@/lib/data";

const VOLUME_LABELS: Record<string, string> = {
  volume_1: "Vol. 1",
  volume_2: "Vol. 2",
  volume_3: "Vol. 3",
  volume_4: "Vol. 4",
  volume_5: "Vol. 5",
  volume_6: "Vol. 6",
  volume_7: "Vol. 7",
  volume_8: "Vol. 8",
  volume_9: "Vol. 9",
};

const TESTAMENT_HEADER_COLORS: Record<string, string> = {
  new_testament: "bg-blue-50 text-blue-700",
  old_testament_or_other: "bg-amber-50 text-amber-700",
  deuterocanonical: "bg-emerald-50 text-emerald-700",
};

export default function VolumesPage() {
  const rows = getVolumeComparison();
  const volumes = rows.length > 0 ? Object.keys(rows[0].by_volume) : [];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-stone-800">Volume Comparison</h1>
        <p className="mt-2 text-stone-500">
          Citation counts per biblical book broken down across all nine ANF volumes. Only books with
          at least one citation are shown.
        </p>
      </div>

      <div className="bg-white rounded-xl border border-stone-200 overflow-x-auto">
        <table className="text-sm w-full">
          <thead>
            <tr className="border-b border-stone-100 text-stone-500 text-xs uppercase tracking-wide">
              <th className="text-left px-4 py-3 font-medium sticky left-0 bg-white">Book</th>
              <th className="text-right px-4 py-3 font-medium">Total</th>
              {volumes.map((v) => (
                <th key={v} className="text-right px-3 py-3 font-medium">
                  {VOLUME_LABELS[v] ?? v}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr
                key={row.book}
                className={`border-b border-stone-50 ${i % 2 === 0 ? "" : "bg-stone-50/50"}`}
              >
                <td
                  className={`px-4 py-2 font-medium sticky left-0 ${
                    i % 2 === 0 ? "bg-white" : "bg-stone-50"
                  }`}
                >
                  <span className="text-stone-700">{row.display_name}</span>
                  <span
                    className={`ml-2 text-xs px-1.5 py-0.5 rounded ${
                      TESTAMENT_HEADER_COLORS[row.testament_group] ?? ""
                    }`}
                  >
                    {row.testament_group === "new_testament"
                      ? "NT"
                      : row.testament_group === "deuterocanonical"
                      ? "Deut"
                      : "OT"}
                  </span>
                </td>
                <td className="px-4 py-2 text-right tabular-nums font-medium text-stone-700">
                  {row.total_count.toLocaleString()}
                </td>
                {volumes.map((v) => {
                  const count = row.by_volume[v] ?? 0;
                  return (
                    <td
                      key={v}
                      className={`px-3 py-2 text-right tabular-nums ${
                        count > 0 ? "text-stone-600" : "text-stone-200"
                      }`}
                    >
                      {count > 0 ? count : "—"}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
