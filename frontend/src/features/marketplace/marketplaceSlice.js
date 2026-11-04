import { createSlice } from "@reduxjs/toolkit";

const marketplaceSlice = createSlice({
  name: "marketplace",
  initialState: { filters: {}, sort: "newest" },
  reducers: {
    setFilters: (state, { payload }) => {
      state.filters = payload;
    },
    setSort: (state, { payload }) => {
      state.sort = payload;
    },
  },
});

export const { setFilters, setSort } = marketplaceSlice.actions;
export default marketplaceSlice.reducer;
