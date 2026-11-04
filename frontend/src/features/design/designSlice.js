import { createSlice } from "@reduxjs/toolkit";

const initialState = {
  activeSessionId: null,
  selectedDesignId: null,
  generationStatus: "idle", // idle | queued | generating | completed | failed
  generationProgress: 0,
  error: null,
};

const designSlice = createSlice({
  name: "design",
  initialState,
  reducers: {
    setActiveSession: (state, { payload }) => {
      state.activeSessionId = payload;
    },
    setSelectedDesign: (state, { payload }) => {
      state.selectedDesignId = payload;
    },
    setGenerationStatus: (state, { payload }) => {
      state.generationStatus = payload;
      if (payload !== "failed") state.error = null;
    },
    setGenerationProgress: (state, { payload }) => {
      state.generationProgress = Math.max(0, Math.min(100, payload));
    },
    setDesignError: (state, { payload }) => {
      state.error = payload;
      state.generationStatus = "failed";
    },
    resetDesignState: () => initialState,
  },
});

export const {
  setActiveSession,
  setSelectedDesign,
  setGenerationStatus,
  setGenerationProgress,
  setDesignError,
  resetDesignState,
} = designSlice.actions;
export default designSlice.reducer;
