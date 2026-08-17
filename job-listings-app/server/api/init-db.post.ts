// Proxies to job-search-automation's POST /init-db. Creates the job_listings
// table if it doesn't exist yet — safe to call repeatedly (no-op if it does).
export default defineEventHandler(async () => {
  const { backendUrl } = useRuntimeConfig();
  try {
    return await $fetch(`${backendUrl}/init-db`, { method: "POST" });
  } catch (err) {
    throw createError({
      statusCode: 502,
      statusMessage: "Could not reach the job-search-automation backend",
      cause: err,
    });
  }
});
