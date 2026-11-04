import { createSlice } from "@reduxjs/toolkit";

const tenantSlice = createSlice({
  name: "tenant",
  initialState: { activeWorkspace: "independent" },
  reducers: {
    setActiveWorkspace: (state, { payload }) => {
      state.activeWorkspace = payload;
    },
  },
});

export const { setActiveWorkspace } = tenantSlice.actions;
export default tenantSlice.reducer;
