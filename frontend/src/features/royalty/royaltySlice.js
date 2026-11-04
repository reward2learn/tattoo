import { createSlice } from "@reduxjs/toolkit";

const royaltySlice = createSlice({
  name: "royalty",
  initialState: { period: "30d" },
  reducers: {
    setPeriod: (state, { payload }) => {
      state.period = payload;
    },
  },
});

export const { setPeriod } = royaltySlice.actions;
export default royaltySlice.reducer;
