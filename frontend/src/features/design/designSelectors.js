export const selectActiveSessionId = (state) => state.design.activeSessionId;
export const selectSelectedDesignId = (state) => state.design.selectedDesignId;
export const selectGenerationStatus = (state) => state.design.generationStatus;
export const selectGenerationProgress = (state) => state.design.generationProgress;
export const selectDesignError = (state) => state.design.error;
export const selectIsGenerating = (state) => ["queued", "generating"].includes(state.design.generationStatus);
