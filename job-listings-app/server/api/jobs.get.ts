// Proxies to job-search-automation's GET /jobs and maps its snake_case
// fields to the camelCase Job type the frontend uses.
import type { Job } from "@/lib/types";

interface BackendJob {
  id: number;
  source: string;
  title: string;
  company: string;
  url: string;
  description: string;
  tags: string[];
  salary: string | null;
  location: string;
  posted_date: string;
  fit_score: number | null;
  income_score: number | null;
  score: number | null;
  reasoning: string | null;
  outreach_draft: string | null;
}

function toJob(j: BackendJob): Job {
  return {
    id: j.id,
    source: j.source,
    title: j.title,
    company: j.company,
    url: j.url,
    description: j.description,
    tags: j.tags,
    salary: j.salary,
    location: j.location,
    postedDate: j.posted_date,
    fitScore: j.fit_score,
    incomeScore: j.income_score,
    score: j.score,
    reasoning: j.reasoning,
    outreachDraft: j.outreach_draft,
  };
}

export default defineEventHandler(async (event) => {
  const { backendUrl } = useRuntimeConfig();
  const query = getQuery(event);
  try {
    const data = await $fetch<BackendJob[]>(`${backendUrl}/jobs`, { query });
    return data.map(toJob);
  } catch (err: any) {
    // 503 from the backend means "reachable, but schema isn't initialized" —
    // pass that through as-is so the frontend can show the right empty state,
    // instead of collapsing every failure into "couldn't reach the backend".
    if (err?.response?.status === 503) {
      throw createError({
        statusCode: 503,
        statusMessage: "Database schema not initialized",
        cause: err,
      });
    }
    throw createError({
      statusCode: 502,
      statusMessage: "Could not reach the job-search-automation backend",
      cause: err,
    });
  }
});
