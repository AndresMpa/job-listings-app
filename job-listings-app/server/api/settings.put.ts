// Proxies to job-search-automation's PUT /config.
import type { AppSettings } from "@/lib/types";

export default defineEventHandler(async (event) => {
  const { backendUrl } = useRuntimeConfig();
  const body = await readBody<AppSettings>(event);

  try {
    return await $fetch<AppSettings>(`${backendUrl}/config`, {
      method: "PUT",
      body,
    });
  } catch (err: any) {
    throw createError({
      statusCode: err?.response?.status || 502,
      statusMessage: err?.response?._data?.detail || "Could not save settings",
      cause: err,
    });
  }
});
