import { useState } from "react";
import { useDispatch } from "react-redux";
import { useUpdateBrandingMutation } from "@/features/tenant/tenantApi";
import { notify } from "@/features/notification/notificationSlice";
import { apiErrorMessage, HEX_RE } from "@/lib/app";
import { AreaField, Field, PrimaryButton, TextField } from "@/components/common/Form";
import { Input } from "@/components/ui/input";
import { LogoUploader } from "@/components/studio/LogoUploader";
import { StudioLayout } from "@/components/studio/StudioLayout";

const FIELDS = ["name", "primary_color", "accent_color", "tagline", "about", "city", "contact_email", "instagram"];
const HEX_MSG = "Enter a valid hex color like #1A1A1A";

const ColorField = ({ id, label, value, onChange, error }) => (
  <Field id={id} label={label} error={error}>
    <div className="flex items-center gap-3">
      <input type="color" aria-label={`${label} picker`} value={HEX_RE.test(value) && value.length === 7 ? value : "#000000"}
        onChange={(e) => onChange(e.target.value.toUpperCase())} data-testid={`${id}-picker`}
        className="h-11 w-14 shrink-0 cursor-pointer rounded-md border border-zinc-800 bg-zinc-900 p-1" />
      <Input id={id} data-testid={id} value={value} onChange={(e) => onChange(e.target.value)}
        className="bg-zinc-900/70 border-zinc-800 text-zinc-100 h-11 font-mono uppercase" />
    </div>
  </Field>
);

const BrandingForm = ({ studio }) => {
  const [form, setForm] = useState(() => Object.fromEntries(FIELDS.map((k) => [k, studio[k] ?? ""])));
  const [errors, setErrors] = useState({});
  const [save, { isLoading }] = useUpdateBrandingMutation();
  const dispatch = useDispatch();
  const set = (k) => (v) => setForm({ ...form, [k]: typeof v === "string" ? v : v.target.value });

  const submit = async (e) => {
    e.preventDefault();
    const errs = {};
    ["primary_color", "accent_color"].forEach((k) => { if (!HEX_RE.test(form[k])) errs[k] = HEX_MSG; });
    setErrors(errs);
    if (Object.keys(errs).length) return dispatch(notify({ type: "error", message: HEX_MSG }));
    try {
      await save({ slug: studio.slug, ...form, contact_email: form.contact_email || null }).unwrap();
      dispatch(notify({ message: "Branding saved" }));
    } catch (err) {
      dispatch(notify({ type: "error", message: apiErrorMessage(err) }));
    }
  };

  return (
    <form onSubmit={submit} className="grid gap-6 lg:grid-cols-2" noValidate data-testid="branding-form">
      <div className="lg:col-span-2"><LogoUploader studio={studio} /></div>
      <TextField id="branding-name-input" label="Studio name" value={form.name} onChange={set("name")} />
      <TextField id="branding-city-input" label="City" value={form.city} onChange={set("city")} placeholder="Jakarta" />
      <ColorField id="branding-primary-color-input" label="Primary color" value={form.primary_color} onChange={set("primary_color")} error={errors.primary_color} />
      <ColorField id="branding-accent-color-input" label="Accent color" value={form.accent_color} onChange={set("accent_color")} error={errors.accent_color} />
      <div className="lg:col-span-2"><TextField id="branding-tagline-input" label="Tagline" value={form.tagline} onChange={set("tagline")} maxLength={140} /></div>
      <div className="lg:col-span-2"><AreaField id="branding-about-input" label="About" value={form.about} onChange={set("about")} maxLength={2000} /></div>
      <TextField id="branding-contact-email-input" label="Contact email" type="email" value={form.contact_email} onChange={set("contact_email")} />
      <TextField id="branding-instagram-input" label="Instagram" value={form.instagram} onChange={set("instagram")} placeholder="@yourstudio" />
      <div className="lg:col-span-2 flex justify-end">
        <PrimaryButton type="submit" disabled={isLoading} data-testid="studio-branding-save-button">{isLoading ? "Saving…" : "Save branding"}</PrimaryButton>
      </div>
    </form>
  );
};

export default function StudioBrandingPage() {
  return <StudioLayout>{(studio) => <BrandingForm key={studio.slug} studio={studio} />}</StudioLayout>;
}
