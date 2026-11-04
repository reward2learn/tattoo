import { api } from "@/app/api";

// Phase 2 fills in consultation chat endpoints.
export const chatApi = api.injectEndpoints({
  endpoints: (b) => ({
    getChatModels: b.query({ query: () => "poc/chat/models" }),
  }),
});

export const { useGetChatModelsQuery } = chatApi;
