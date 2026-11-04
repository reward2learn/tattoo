import { useState } from "react";
import { Provider } from "react-redux";
import { makeStore } from "@/app/store";

export const ReduxProvider = ({ children }) => {
  const [store] = useState(makeStore);
  return <Provider store={store}>{children}</Provider>;
};
