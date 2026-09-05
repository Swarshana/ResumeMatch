"use client";

import React, { useState } from "react";
import { analyzeResume } from "@/lib/api";
import { AnalyzeResponse } from "@/lib/types/api";
import { StatusBadge, SectionHeading } from "@/components/ui/components";

export default function Home() {
  const [resume, setResume] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);

  const handleAnalyze = async () => {
    if (!resume.trim() || !jobDescription.trim()) return;
    setLoading(true);
    setError(null);
    try {
      setResult(await analyzeResume(resume, jobDescription));
    } catch (err: any) {
      setError(err.message || "Analysis failed");
    } finally {
      setLoading(false);
    }
  };

  if (result) {
    return (
      <main className="min-h-screen bg-neutral-50 py-12 px-4 md:px-8">
        <div className="max-w-4xl mx-auto space-y-12">
          <div className="flex justify-between items-center">
            <h1 className="text-xl font-black tracking-tight text-neutral-900 uppercase tracking-widest">ResumeMatch AI</h1>
            <button onClick={() => setResult(null)} className="text-xs font-bold text-neutral-500 hover:text-black transition-colors underline uppercase tracking-widest">Start Over</button>
          </div>
          <header className="bg-white p-8 rounded-3xl border border-neutral-200 shadow-sm flex flex-col md:flex-row gap-8 items-center">
            <div className="flex items-center gap-6">
              <div className="w-24 h-24 rounded-full border-4 border-neutral-100 flex items-center justify-center relative shrink-0">
                <span className="text-2xl font-black text-neutral-900">{result.overall_score.toFixed(0)}%</span>
              </div>
              <div className="space-y-2">
                <StatusBadge status={result.overall_status} className="px-3 py-1" />
                <p className="text-[10px] font-black text-neutral-400 uppercase tracking-widest">Overall Score</p>
              </div>
            </div>
            <p className="text-neutral-600 leading-relaxed border-t md:border-t-0 md:border-l border-neutral-100 pt-6 md:pt-0 md:pl-8 text-sm">{result.summary}</p>
          </header>
          <section>
            <SectionHeading>Skill Clusters</SectionHeading>
            <div className="grid md:grid-cols-2 gap-4">
              {result.skill_clusters.map(cluster => (
                <div key={cluster.id} className="bg-white p-6 rounded-2xl border border-neutral-200 shadow-sm space-y-4">
                  <div className="flex justify-between items-center">
                    <h3 className="font-bold text-neutral-900 text-sm">{cluster.name}</h3>
                    <StatusBadge status={cluster.status} />
                  </div>
                  <div className="w-full bg-neutral-100 h-2 rounded-full overflow-hidden">
                    <div className={`h-full ${cluster.score >= 60 ? "bg-emerald-500" : cluster.score >= 30 ? "bg-amber-500" : "bg-rose-500"}`} style={{ width: `${Math.max(cluster.score, 5)}%` }} />
                  </div>
                  <p className="text-[10px] font-bold text-neutral-400 uppercase tracking-widest">
                    {cluster.requirement_count === 1 ? "1 REQUIREMENT" : `${cluster.requirement_count} REQUIREMENTS`}
                  </p>
                </div>
              ))}
            </div>
          </section>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-white py-24 px-6 flex flex-col justify-center">
      <div className="max-w-3xl mx-auto w-full space-y-16">
        <header className="text-center space-y-6">
          <div className="inline-block px-4 py-1.5 bg-neutral-900 text-white text-[10px] font-black tracking-[0.2em] uppercase rounded-full">ResumeMatch AI v1.0</div>
          <h1 className="text-5xl md:text-6xl font-black tracking-tighter text-neutral-900 text-balance">Evaluate your resume match intelligently.</h1>
          <p className="text-lg text-neutral-500 max-w-xl mx-auto leading-relaxed font-medium">Advanced semantic analysis identifying strengths and gaps with precise, evidence-based feedback.</p>
        </header>
        <div className="grid md:grid-cols-2 gap-6">
          <div className="space-y-3">
            <label className="text-[10px] font-black uppercase tracking-widest text-neutral-400">Your Resume</label>
            <textarea rows={12} className="w-full p-6 bg-neutral-50 border border-neutral-200 rounded-3xl focus:border-neutral-900 focus:bg-white outline-none transition-all text-sm font-medium leading-relaxed shadow-sm resize-none" placeholder="Paste your full resume here..." value={resume} onChange={e => setResume(e.target.value)} />
            <div className="text-[10px] font-bold text-neutral-300 font-mono tracking-wider">{resume.length} CHARS</div>
          </div>
          <div className="space-y-3">
            <label className="text-[10px] font-black uppercase tracking-widest text-neutral-400">Job Description</label>
            <textarea rows={12} className="w-full p-6 bg-neutral-50 border border-neutral-200 rounded-3xl focus:border-neutral-900 focus:bg-white outline-none transition-all text-sm font-medium leading-relaxed shadow-sm resize-none" placeholder="Paste the job requirements here..." value={jobDescription} onChange={e => setJobDescription(e.target.value)} />
            <div className="text-[10px] font-bold text-neutral-300 font-mono tracking-wider">{jobDescription.length} CHARS</div>
          </div>
        </div>
        <div className="flex flex-col items-center gap-6">
          <button onClick={handleAnalyze} disabled={loading || !resume.trim() || !jobDescription.trim()} className="px-12 py-5 bg-neutral-900 text-white text-base font-black rounded-full hover:bg-neutral-800 disabled:opacity-30 transition-all shadow-xl active:scale-95 flex items-center gap-3">
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>Analyzing Context...</span>
              </>
            ) : "Analyze Match"}
          </button>
          {error && <p className="text-xs font-bold text-rose-600 uppercase tracking-widest bg-rose-50 px-4 py-2 rounded-full">{error}</p>}
        </div>
      </div>
    </main>
  );
}