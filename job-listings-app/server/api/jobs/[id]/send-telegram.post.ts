// Proxies to job-search-automation's POST /jobs/{id}/send-telegram.
//
// This is the ONLY path the UI uses to deliver an offer to Telegram. The
// backend looks up the job, reads its owning profile (JobRecord.profile),
// and sends to that profile's own chat_id — so a job for profile "user1"
// always lands in user1's chat, regardless of which profile is currently
// selected in the UI. The caller never supplies a chat_id.
import type { ApiFetchError } from "@/lib/types";

export default defineEventHandler(async (event) => {
  const { backendUrl } = useRuntimeConfig();
  const id = getRouterParam(event, "id");

  try {
    return await $fetch(`${backendUrl}/jobs/${id}/send-telegram`, {
      method: "POST",
    });
  } catch (err) {
    const error = err as ApiFetchError;
    const status = error?.response?.status;

    // 400 from the backend means "reachable, but this offer can't be sent"
    // (Telegram disabled for the profile, no chat_id, no bot token, or the
    // Telegram API itself rejected it) — surface the backend's own reason
    // instead of a generic message.
    if (status === 400 || status === 404) {
      throw createError({
        statusCode: status,
        statusMessage:
          error?.response?._data?.detail ??
          "Could not send this offer to Telegram",
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
