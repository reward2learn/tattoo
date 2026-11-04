import { createSlice } from "@reduxjs/toolkit";

export const DEFAULT_CHAT_MODEL = "Claude Sonnet 5.5";

const chatSlice = createSlice({
  name: "chat",
  initialState: { activeConversationId: null, selectedModel: DEFAULT_CHAT_MODEL, draft: "" },
  reducers: {
    setActiveConversation: (state, { payload }) => {
      state.activeConversationId = payload;
    },
    setSelectedModel: (state, { payload }) => {
      state.selectedModel = payload;
    },
    setDraft: (state, { payload }) => {
      state.draft = payload;
    },
  },
});

export const { setActiveConversation, setSelectedModel, setDraft } = chatSlice.actions;
export default chatSlice.reducer;
