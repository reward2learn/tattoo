import { useEffect, useRef } from "react";
import { useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";
import { useGoogleSessionMutation } from "@/features/auth/authApi";
import { signedOut } from "@/features/auth/authSlice";
import { notify } from "@/features/notification/notificationSlice";
import { homeFor } from "@/lib/app";
import { FullPageLoader } from "@/components/common/States";

export const AuthCallback = () => {
  const processed = useRef(false);
  const [exchange] = useGoogleSessionMutation();
  const navigate = useNavigate();
  const dispatch = useDispatch();

  useEffect(() => {
    if (processed.current) return;
    processed.current = true;
    const sessionId = new URLSearchParams(window.location.hash.slice(1)).get("session_id");
    window.history.replaceState(null, "", window.location.pathname);
    exchange({ session_id: sessionId })
      .unwrap()
      .then((user) => navigate(homeFor(user), { replace: true }))
      .catch(() => {
        dispatch(signedOut());
        dispatch(notify({ type: "error", message: "Google sign-in failed. Please try again." }));
        navigate("/login", { replace: true });
      });
  }, [exchange, navigate, dispatch]);

  return <FullPageLoader />;
};

export const GoogleButton = () => {
  const start = () => {
    // REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
    const redirectUrl = window.location.origin + "/home";
    window.location.href = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
  };
  return (
    <button
      type="button"
      onClick={start}
      data-testid="google-signin-button"
      className="w-full inline-flex items-center justify-center gap-3 h-11 rounded-md border border-zinc-700 bg-zinc-900/60 text-sm font-medium text-zinc-100 hover:bg-zinc-800 transition-colors"
    >
      <svg width="18" height="18" viewBox="0 0 48 48" aria-hidden="true">
        <path fill="#FFC107" d="M43.6 20.5H42V20H24v8h11.3C33.7 32.7 29.2 36 24 36c-6.6 0-12-5.4-12-12s5.4-12 12-12c3 0 5.8 1.1 7.9 3l5.7-5.7C34 6.1 29.3 4 24 4 12.9 4 4 12.9 4 24s8.9 20 20 20 20-8.9 20-20c0-1.3-.1-2.4-.4-3.5z" />
        <path fill="#FF3D00" d="M6.3 14.7l6.6 4.8C14.7 15.1 19 12 24 12c3 0 5.8 1.1 7.9 3l5.7-5.7C34 6.1 29.3 4 24 4 16.3 4 9.7 8.3 6.3 14.7z" />
        <path fill="#4CAF50" d="M24 44c5.2 0 9.9-2 13.4-5.2l-6.2-5.2C29.2 35.1 26.7 36 24 36c-5.2 0-9.6-3.3-11.3-8l-6.5 5C9.5 39.6 16.2 44 24 44z" />
        <path fill="#1976D2" d="M43.6 20.5H42V20H24v8h11.3c-.8 2.2-2.2 4.2-4.1 5.6l6.2 5.2C37 39.2 44 34 44 24c0-1.3-.1-2.4-.4-3.5z" />
      </svg>
      Continue with Google
    </button>
  );
};
