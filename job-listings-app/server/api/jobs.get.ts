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
