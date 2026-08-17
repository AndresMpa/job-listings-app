// Proxies to job-search-automation's GET /profiles.
import type { ProfileSettings } from "@/lib/types";

export default defineEventHandler(async () => {
  const { backendUrl } = useRuntimeConfig();
  try {
    return await $fetch<ProfileSettings[]>(`${backendUrl}/profiles`);
  } catch (err) {
    throw createError({
      statusCode: 502,
      statusMessage: "Could not reach the job-search-automation backend",
      cause: err,
    });
  }
});
