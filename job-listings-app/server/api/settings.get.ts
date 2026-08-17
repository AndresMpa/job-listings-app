// Proxies to job-search-automation's GET /config.
import type { AppSettings } from "@/lib/types";

export default defineEventHandler(async () => {
  const { backendUrl } = useRuntimeConfig();
  try {
    return await $fetch<AppSettings>(`${backendUrl}/config`);
  } catch (err) {
    throw createError({
      statusCode: 502,
      statusMessage: "Could not reach the job-search-automation backend",
      cause: err,
    });
  }
});
