import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useDispatch } from "react-redux";
import { useCreateStudioMutation, useLazyCheckSlugQuery } from "@/features/tenant/tenantApi";
import { notify } from "@/features/notification/notificationSlice";
import { apiErrorMessage, localSlugProblem, slugify } from "@/lib/app";
import { AuthCard, FormError } from "@/components/auth/AuthCard";
import { Field, PrimaryButton, TextField } from "@/components/common/Form";
import { Input } from "@/components/ui/input";

const useSlugCheck = (slug) => {
  const [check, { data, isFetching }] = useLazyCheckSlugQuery();
  const local = slug ? localSlugProblem(slug) : null;
  useEffect(() => {
    if (!slug || local) return undefined;
    const t = setTimeout(() => check(slug), 350);
    return () => clearTimeout(t);
  }, [slug, local, check]);
  if (!slug) return { message: null };
  if (local) return { message: local };
  if (isFetching || data?.slug !== slug) return { message: null, pending: true };
  return { message: data.message, ok: data.available };
};

export default function CreateStudioPage() {
  const [name, setName] = useState("");
  const [slug, setSlug] = useState("");
  const [slugTouched, setSlugTouched] = useState(false);
  const [error, setError] = useState("");
  const [create, { isLoading }] = useCreateStudioMutation();
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const status = useSlugCheck(slug);

  const onName = (v) => {
    setName(v);
    if (!slugTouched) setSlug(slugify(v));
  };

  const submit = async (e) => {
    e.preventDefault();
    if (name.trim().length < 2) return setError("Enter your studio name");
    const problem = localSlugProblem(slug);
    if (problem) return setError(problem);
    try {
      const studio = await create({ name: name.trim(), slug }).unwrap();
      dispatch(notify({ message: `${studio.name} is live — now add your branding` }));
      navigate(`/studio/${studio.slug}`, { replace: true });
    } catch (err) {
      setError(apiErrorMessage(err));
    }
  };

  return (
    <AuthCard eyebrow="Step 1 of 2" title="Create your studio" testid="create-studio-page">
      <form onSubmit={submit} className="space-y-5" noValidate>
        <TextField id="create-studio-input-name" label="Studio name" placeholder="Rumah Tinta Jakarta"
          value={name} onChange={(e) => onName(e.target.value)} />
        <Field id="create-studio-input-slug" label="Studio URL" error={status.message}
          hint={status.ok ? "Available" : "Lowercase letters, numbers and hyphens"}>
          <div className="flex items-center rounded-md border border-zinc-800 bg-zinc-900/70 focus-within:ring-2 focus-within:ring-amber-500/60">
            <span className="pl-3 text-sm text-zinc-500 font-mono">/t/</span>
            <Input id="create-studio-input-slug" data-testid="create-studio-input-slug" value={slug}
              className="border-0 bg-transparent h-11 font-mono text-zinc-100 focus-visible:ring-0 pl-1"
              onChange={(e) => { setSlugTouched(true); setSlug(e.target.value); }} />
          </div>
        </Field>
        <FormError message={error} testid="create-studio-error" />
        <PrimaryButton type="submit" className="w-full" disabled={isLoading || status.pending} data-testid="create-studio-submit-button">
          {isLoading ? "Creating…" : "Create studio"}
        </PrimaryButton>
      </form>
    </AuthCard>
  );
}
