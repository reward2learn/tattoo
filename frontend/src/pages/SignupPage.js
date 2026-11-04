import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { useSelector } from "react-redux";
import { useRegisterMutation } from "@/features/auth/authApi";
import { selectCurrentUser } from "@/features/auth/authSelectors";
import { apiErrorMessage, homeFor } from "@/lib/app";
import { AuthCard, Divider, FormError } from "@/components/auth/AuthCard";
import { GoogleButton } from "@/components/auth/GoogleAuth";
import { AccountTypePicker } from "@/components/auth/AccountTypePicker";
import { PrimaryButton, TextField } from "@/components/common/Form";

const validate = ({ name, email, password, account_type }) => {
  if (!name.trim()) return "Enter your name";
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return "Enter a valid email address";
  if (password.length < 8) return "Password must be at least 8 characters";
  if (!account_type) return "Choose what brings you to InkForge";
  return null;
};

export default function SignupPage() {
  const [form, setForm] = useState({ name: "", email: "", password: "", account_type: "" });
  const [error, setError] = useState("");
  const [register, { isLoading }] = useRegisterMutation();
  const user = useSelector(selectCurrentUser);
  const navigate = useNavigate();

  if (user && !isLoading) return <Navigate to={homeFor(user)} replace />;
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    const problem = validate(form);
    setError(problem || "");
    if (problem) return;
    try {
      const u = await register(form).unwrap();
      navigate(u.pending_invitations > 0 ? "/invitations" : homeFor(u), { replace: true });
    } catch (err) {
      setError(apiErrorMessage(err));
    }
  };

  return (
    <AuthCard eyebrow="Join InkForge" title="Create your account" testid="signup-page">
      <form onSubmit={submit} className="space-y-5" noValidate>
        <AccountTypePicker value={form.account_type} onChange={(v) => setForm({ ...form, account_type: v })} />
        <TextField id="signup-name-input" label="Name" autoComplete="name" value={form.name} onChange={set("name")} />
        <TextField id="signup-email-input" label="Email" type="email" autoComplete="email" value={form.email} onChange={set("email")} />
        <TextField id="signup-password-input" label="Password" type="password" autoComplete="new-password"
          hint="At least 8 characters" value={form.password} onChange={set("password")} />
        <FormError message={error} testid="signup-error" />
        <PrimaryButton type="submit" className="w-full" disabled={isLoading} data-testid="signup-submit-button">
          {isLoading ? "Creating account…" : "Create account"}
        </PrimaryButton>
      </form>
      <Divider />
      <GoogleButton />
      <p className="mt-6 text-sm text-zinc-400">
        Already have an account? <Link to="/login" className="text-amber-500 hover:text-amber-400" data-testid="signup-to-login-link">Sign in</Link>
      </p>
    </AuthCard>
  );
}
