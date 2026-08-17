// Mirrors JobOut from job-search-automation's API (see ../job-search-automation/src/job_search/api.py)
interface Job {
  id: number;
  source: string;
  title: string;
  company: string;
  url: string;
  description: string;
  tags: string[];
  salary: string | null;
  location: string;
  postedDate: string;
  fitScore: number | null;
  incomeScore: number | null;
  score: number | null;
  reasoning: string | null;
  outreachDraft: string | null;
}

// Mirrors AppConfig.to_dict() from job-search-automation (see ../job-search-automation/src/job_search/config.py)
interface AppSettings {
  profile: string;
  ollama: {
    url: string;
    model: string;
    timeout: number;
  };
  keywords: {
    target: string[];
    exclude: string[];
    seniority: string[];
    ai: string[];
    tech: string[];
  };
  providers: {
    remoteok: boolean;
    remotive: boolean;
    weworkremotely: boolean;
    python_jobs: boolean;
    vuejobs: boolean;
    hackernews: boolean;
    arbeitnow: boolean;
  };
  weworkremotely: {
    categories: string[];
  };
  scoring: {
    min_score_to_keep: number;
    fit_weight: number;
    income_weight: number;
  };
  output: {
    dir: string;
    csv_filename: string;
    md_filename: string;
  };
  database: {
    url: string;
  };
}

export type { Job, AppSettings };
