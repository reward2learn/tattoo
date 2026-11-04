import { createSlice, isAnyOf } from "@reduxjs/toolkit";
import { api } from "@/app/api";
import { authApi } from "@/features/auth/authApi";

const initialState = { status: "checking", user: null };

const { endpoints: e } = authApi;
const userLoaded = isAnyOf(
  e.me.matchFulfilled,
  e.login.matchFulfilled,
  e.register.matchFulfilled,
  e.googleSession.matchFulfilled,
  e.chooseAccountType.matchFulfilled,
);

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    signedOut: (state) => {
      state.status = "anonymous";
      state.user = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addMatcher(userLoaded, (state, { payload }) => {
        state.user = payload;
        state.status = "authenticated";
      })
      .addMatcher(e.me.matchRejected, (state, action) => {
        if (action.meta?.condition) return;
        state.user = null;
        state.status = "anonymous";
      });
  },
});

export const { signedOut } = authSlice.actions;

export const signOut = () => async (dispatch) => {
  try {
    await dispatch(authApi.endpoints.logout.initiate()).unwrap();
  } catch (_) {
    // cookies are cleared server-side even when the token is already invalid
  }
  dispatch(signedOut());
  dispatch(api.util.resetApiState());
};

export default authSlice.reducer;
