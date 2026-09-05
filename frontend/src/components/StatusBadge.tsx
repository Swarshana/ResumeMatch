import React from "react";
import { MatchStatus } from "@/lib/types/api";

const statusColors = {
  strong: "bg-emerald-100 text-emerald-800 border-emerald-200",
  partial: "bg-amber-100 text-amber-800 border-amber-200",
  weak: "bg-rose-100 text-rose-800 border-rose-200",
};

export const StatusBadge = ({ status }: { status: MatchStatus }) => (
  <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-black border uppercase tracking-widest ${statusColors[status]}`}>
    {status}
  </span>
);
