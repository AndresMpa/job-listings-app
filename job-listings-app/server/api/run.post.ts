// Proxies to job-search-automation's POST /run. Triggers a full fetch +
// score + report cycle on the backend, optionally scoped to one profile.
export default defineEventHandler(async (event) => {
  const { backendUrl } = useRuntimeConfig();
  const query = getQuery(event);
  try {
    return await $fetch(`${backendUrl}/run`, {
      method: "POST",
      query,
    });
  } catch (err) {
    throw createError({
      statusCode: 502,
      statusMessage: "Could not reach the job-search-automation backend",
      cause: err,
    });
  }
});
