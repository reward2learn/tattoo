import { useState } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { useSelector } from "react-redux";
import { useLoginMutation } from "@/features/auth/authApi";
import { selectCurrentUser } from "@/features/auth/authSelectors";
import { apiErrorMessage, homeFor } from "@/lib/app";
import { AuthCard, Divider, FormError } from "@/components/auth/AuthCard";
import { GoogleButton } from "@/components/auth/GoogleAuth";
import { PrimaryButton, TextField } from "@/components/common/Form";

export default function LoginPage() {
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [login, { isLoading }] = useLoginMutation();
  const user = useSelector(selectCurrentUser);
  const navigate = useNavigate();
  const from = useLocation().state?.from;

  if (user && !isLoading) return <Navigate to={from || homeFor(user)} replace />;

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const u = await login(form).unwrap();
      navigate(from || homeFor(u), { replace: true });
    } catch (err) {
      setError(apiErrorMessage(err));
    }
  };

  return (
    <AuthCard eyebrow="Welcome back" title="Sign in" testid="login-page">
      <GoogleButton />
      <Divider />
      <form onSubmit={submit} className="space-y-5" noValidate>
        <TextField id="login-email-input" label="Email" type="email" autoComplete="email" value={form.email}
          onChange={(e) => setForm({ ...form, email: e.target.value })} required />
        <TextField id="login-password-input" label="Password" type="password" autoComplete="current-password"
          value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required />
        <FormError message={error} testid="login-error" />
        <PrimaryButton type="submit" className="w-full" disabled={isLoading} data-testid="login-submit-button">
          {isLoading ? "Signing in…" : "Sign in"}
        </PrimaryButton>
      </form>
      <p className="mt-6 text-sm text-zinc-400">
        New to InkForge? <Link to="/signup" className="text-amber-500 hover:text-amber-400" data-testid="login-to-signup-link">Create an account</Link>
      </p>
    </AuthCard>
  );
}
