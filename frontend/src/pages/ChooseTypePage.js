import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { useSelector } from "react-redux";
import { useChooseAccountTypeMutation } from "@/features/auth/authApi";
import { selectCurrentUser } from "@/features/auth/authSelectors";
import { apiErrorMessage, homeFor } from "@/lib/app";
import { AuthCard, FormError } from "@/components/auth/AuthCard";
import { AccountTypePicker } from "@/components/auth/AccountTypePicker";
import { PrimaryButton } from "@/components/common/Form";

export default function ChooseTypePage() {
  const user = useSelector(selectCurrentUser);
  const [type, setType] = useState("");
  const [error, setError] = useState("");
  const [choose, { isLoading }] = useChooseAccountTypeMutation();
  const navigate = useNavigate();

  if (!user.needs_account_type) return <Navigate to={homeFor(user)} replace />;

  const submit = async () => {
    if (!type) return setError("Choose what brings you to InkForge");
    try {
      const u = await choose({ account_type: type }).unwrap();
      navigate(u.pending_invitations > 0 ? "/invitations" : homeFor(u), { replace: true });
    } catch (err) {
      setError(apiErrorMessage(err));
    }
  };

  return (
    <AuthCard eyebrow={`Hi ${user.name}`} title="What brings you here?" testid="choose-type-page">
      <AccountTypePicker value={type} onChange={(v) => { setType(v); setError(""); }} />
      <div className="mt-5"><FormError message={error} testid="choose-type-error" /></div>
      <PrimaryButton onClick={submit} disabled={isLoading} className="w-full mt-5" data-testid="choose-type-continue-button">
        Continue
      </PrimaryButton>
    </AuthCard>
  );
}
