import { ResponsiveContainer, AreaChart, Area, Tooltip } from "recharts";
import type { DataPoint } from "../types";

interface Props {
  data: DataPoint[];
  positive?: boolean;
}

const CustomTooltip = ({ active, payload }: any) => {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload as DataPoint;
  return (
    <div className="bg-[#222] border border-subtle rounded-md px-2 py-1 text-[10px] text-secondary shadow-xl pointer-events-none">
      <span className="text-muted">{d.date}  </span>
      <span className="text-primary font-semibold tabular">{d.value?.toFixed(2)}</span>
    </div>
  );
};

export default function MiniChart({ data, positive = true }: Props) {
  const color = positive ? "#22c55e" : "#ef4444";
  const gradId = `g${positive ? "p" : "n"}`;
  return (
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart data={data} margin={{ top: 2, right: 0, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id={gradId} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%"   stopColor={color} stopOpacity={0.3} />
            <stop offset="100%" stopColor={color} stopOpacity={0}   />
          </linearGradient>
        </defs>
        <Area
          type="monotone"
          dataKey="value"
          stroke={color}
          strokeWidth={1.5}
          fill={`url(#${gradId})`}
          dot={false}
          activeDot={{ r: 2, fill: color, strokeWidth: 0 }}
          connectNulls
        />
        <Tooltip content={<CustomTooltip />} cursor={{ stroke: "rgba(255,255,255,0.1)", strokeWidth: 1 }} />
      </AreaChart>
    </ResponsiveContainer>
  );
}
