"use client";

import { useEffect, useState } from "react";
import { Report } from "@/types";
import { fetchReport } from "@/lib/api";
import Hero from "@/components/Hero";
import IdeaList from "@/components/IdeaList";
import Sidebar from "@/components/Sidebar";
import Footer from "@/components/Footer";

export default function Home() {
  const [report, setReport] = useState<Report | null>(null);

  useEffect(() => {
    fetchReport().then(setReport).catch(() => {});
  }, []);

  return (
    <>
      <div className="max-w-[1200px] mx-auto px-12 pt-10 pb-20 flex gap-8 items-start max-[900px]:flex-col max-[900px]:px-5 max-[900px]:pt-6">
        <div className="flex-1 min-w-0">
          <Hero generatedAt={report?.generated_at ?? null} />

          {report ? (
            <IdeaList
              ideas={report.ideas}
              narratives={report.narratives}
            />
          ) : (
            <div className="text-center py-24">
              <div className="w-[18px] h-[18px] border-2 border-divider border-t-title rounded-full animate-spin mx-auto mb-3" />
              <p className="text-sm text-desc">Loading ideas...</p>
            </div>
          )}
        </div>

        <div className="max-[900px]:w-full">
          <Sidebar narratives={report?.narratives ?? []} />
        </div>
      </div>

      <Footer generatedAt={report?.generated_at ?? null} />
    </>
  );
}
