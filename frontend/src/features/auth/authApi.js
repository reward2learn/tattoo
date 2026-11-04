import { api } from "@/app/api";

const post = (url) => (body) => ({ url, method: "POST", body });

export const authApi = api.injectEndpoints({
  endpoints: (b) => ({
    me: b.query({ query: () => "auth/me", providesTags: ["Me"] }),
    login: b.mutation({ query: post("auth/login") }),
    register: b.mutation({ query: post("auth/register") }),
    googleSession: b.mutation({ query: post("auth/google/session") }),
    chooseAccountType: b.mutation({ query: post("auth/account-type"), invalidatesTags: ["Me"] }),
    logout: b.mutation({ query: () => ({ url: "auth/logout", method: "POST" }) }),
  }),
});

export const {
  useMeQuery,
  useLoginMutation,
  useRegisterMutation,
  useGoogleSessionMutation,
  useChooseAccountTypeMutation,
} = authApi;
