import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

const rawBaseQuery = fetchBaseQuery({
  baseUrl: `${process.env.REACT_APP_BACKEND_URL}/api`,
  credentials: "include",
});

const NO_REFRESH = ["auth/refresh", "auth/login", "auth/register", "auth/google/session", "auth/logout"];
let refreshing = null;

// Access tokens are short-lived; on 401 try the refresh cookie once, then retry.
export const baseQueryWithReauth = async (args, api, extra) => {
  let result = await rawBaseQuery(args, api, extra);
  const url = typeof args === "string" ? args : args.url;
  if (result.error?.status === 401 && !NO_REFRESH.some((p) => url.startsWith(p))) {
    refreshing =
      refreshing ||
      rawBaseQuery({ url: "auth/refresh", method: "POST" }, api, extra).finally(() => {
        refreshing = null;
      });
    const refreshed = await refreshing;
    if (!refreshed.error) result = await rawBaseQuery(args, api, extra);
  }
  return result;
};

export const api = createApi({
  reducerPath: "api",
  baseQuery: baseQueryWithReauth,
  tagTypes: ["Me", "Studio", "Team", "Invitations", "Tenants", "PublicStudio", "Workspace"],
  endpoints: () => ({}),
});
