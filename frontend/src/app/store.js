import { combineReducers, configureStore } from "@reduxjs/toolkit";
import { api } from "@/app/api";
import authReducer, { signedOut } from "@/features/auth/authSlice";
import tenantReducer from "@/features/tenant/tenantSlice";
import chatReducer from "@/features/chat/chatSlice";
import designReducer from "@/features/design/designSlice";
import marketplaceReducer from "@/features/marketplace/marketplaceSlice";
import royaltyReducer from "@/features/royalty/royaltySlice";
import notificationReducer from "@/features/notification/notificationSlice";
import uiReducer from "@/features/ui/uiSlice";

const appReducer = combineReducers({
  [api.reducerPath]: api.reducer,
  auth: authReducer,
  tenant: tenantReducer,
  chat: chatReducer,
  design: designReducer,
  marketplace: marketplaceReducer,
  royalty: royaltyReducer,
  notification: notificationReducer,
  ui: uiReducer,
});

// Sign-out wipes every session/workflow slice; the RTK Query cache is reset by the signOut thunk.
const rootReducer = (state, action) => {
  if (action.type === signedOut.type && state) {
    state = { [api.reducerPath]: state[api.reducerPath], notification: state.notification, ui: state.ui };
  }
  return appReducer(state, action);
};

export const makeStore = () =>
  configureStore({
    reducer: rootReducer,
    middleware: (getDefaultMiddleware) => getDefaultMiddleware().concat(api.middleware),
  });
