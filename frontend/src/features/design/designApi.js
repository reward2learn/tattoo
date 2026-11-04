import { api } from "@/app/api";

// Phase 2/3 fill in concept generation and design endpoints.
export const designApi = api.injectEndpoints({
  endpoints: (b) => ({
    getImageEngines: b.query({ query: () => "poc/images/engines" }),
  }),
});

export const { useGetImageEnginesQuery } = designApi;
