import { useRef, useState } from "react";
import { useDispatch } from "react-redux";
import { Upload } from "lucide-react";
import { useUploadLogoMutation } from "@/features/tenant/tenantApi";
import { notify } from "@/features/notification/notificationSlice";
import { apiErrorMessage, assetUrl } from "@/lib/app";
import { StudioLogo } from "@/components/common/States";
import { GhostButton } from "@/components/common/Form";

const TYPES = ["image/png", "image/jpeg", "image/webp"];
const MAX = 5 * 1024 * 1024;

export const LogoUploader = ({ studio }) => {
  const input = useRef(null);
  const [error, setError] = useState("");
  const [upload, { isLoading }] = useUploadLogoMutation();
  const dispatch = useDispatch();

  const onFile = async (file) => {
    if (!file) return;
    setError("");
    const ext = file.name.split(".").pop().toLowerCase();
    if (!TYPES.includes(file.type) && !["png", "jpg", "jpeg", "webp"].includes(ext)) return setError("Logo must be PNG, JPG or WebP");
    if (file.size > MAX) return setError("Logo must be 5 MB or smaller");
    try {
      await upload({ slug: studio.slug, file }).unwrap();
      dispatch(notify({ message: "Logo updated" }));
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      input.current.value = "";
    }
  };

  return (
    <div className="flex flex-col sm:flex-row gap-5 sm:items-center">
      <StudioLogo src={assetUrl(studio.logo_url)} name={studio.name} className="h-32 w-full sm:w-48 shrink-0 border border-zinc-800" testid="branding-logo-preview" />
      <div className="space-y-2">
        <input ref={input} type="file" accept="image/png,image/jpeg,image/webp" className="hidden"
          data-testid="branding-logo-input" onChange={(e) => onFile(e.target.files?.[0])} />
        <GhostButton type="button" onClick={() => input.current.click()} disabled={isLoading} data-testid="branding-logo-upload-button">
          <Upload className="h-4 w-4" /> {isLoading ? "Uploading…" : studio.logo_url ? "Replace logo" : "Upload logo"}
        </GhostButton>
        <p className="text-xs text-zinc-500">PNG, JPG or WebP · up to 5 MB · shown uncropped</p>
        {error && <p className="text-sm text-red-400" data-testid="branding-logo-error">{error}</p>}
      </div>
    </div>
  );
};
