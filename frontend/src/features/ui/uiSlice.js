import { createSlice } from "@reduxjs/toolkit";

const uiSlice = createSlice({
  name: "ui",
  initialState: { mobileNavOpen: false },
  reducers: {
    setMobileNavOpen: (state, { payload }) => {
      state.mobileNavOpen = payload;
    },
  },
});

export const { setMobileNavOpen } = uiSlice.actions;
export default uiSlice.reducer;
