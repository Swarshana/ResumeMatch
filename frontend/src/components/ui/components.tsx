import React from "react";
import { MatchStatus } from "@/lib/types/api";

const statusColors = {
  strong: "bg-emerald-50 border-emerald-200 text-emerald-800",
  partial: "bg-amber-50 border-amber-200 text-amber-800",
  weak: "bg-rose-50 border-rose-200 text-rose-800",
};

export const StatusBadge = ({ status, className = "" }: { status: MatchStatus; className?: string }) => (
  <span className={`px-2 py-0.5 rounded-full text-[10px] font-black uppercase tracking-widest border ${statusColors[status]} ${className}`}>
    {status}
  </span>
);

export const SectionHeading = ({ children }: { children: React.ReactNode }) => (
  <h2 className="text-xs font-black text-neutral-400 uppercase tracking-widest mb-4">
    {children}
  </h2>
);
