// Proxies to job-search-automation's PUT /config.
import type { FetchError } from "ofetch";
import type { AppSettings } from "@/lib/types";

export default defineEventHandler(async (event) => {
  const { backendUrl } = useRuntimeConfig();
  const body = await readBody<AppSettings>(event);

  try {
    return await $fetch<AppSettings>(`${backendUrl}/config`, {
      method: "PUT",
      body,
    });
  } catch (err) {
    const error = err as FetchError;
    throw createError({
      statusCode: error?.response?.status || 502,
      statusMessage:
        error?.response?._data?.detail || "Could not save settings",
      cause: err,
    });
  }
});
