import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { Toaster, toast } from "@/components/ui/sonner";
import { dismiss } from "@/features/notification/notificationSlice";
import { selectNotifications } from "@/features/notification/notificationSelectors";

export const ToastBridge = () => {
  const items = useSelector(selectNotifications);
  const dispatch = useDispatch();
  useEffect(() => {
    items.forEach((n) => {
      (toast[n.type] || toast)(n.message, { id: n.id });
      dispatch(dismiss(n.id));
    });
  }, [items, dispatch]);
  return <Toaster theme="dark" position="top-right" richColors closeButton />;
};
