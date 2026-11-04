import { createSlice, nanoid } from "@reduxjs/toolkit";

const notificationSlice = createSlice({
  name: "notification",
  initialState: { items: [] },
  reducers: {
    notify: {
      reducer: (state, { payload }) => {
        state.items.push(payload);
      },
      prepare: ({ type = "success", message }) => ({ payload: { id: nanoid(), type, message } }),
    },
    dismiss: (state, { payload }) => {
      state.items = state.items.filter((n) => n.id !== payload);
    },
  },
});

export const { notify, dismiss } = notificationSlice.actions;
export default notificationSlice.reducer;
