export const apiErrorMessage = (error, fallback = "Something went wrong. Please try again.") => {
  const detail = error?.data?.detail;
  if (!detail) return error?.status === "FETCH_ERROR" ? "Network error. Check your connection." : fallback;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) return detail.map((e) => e?.msg || JSON.stringify(e)).join(" ");
  return detail.msg || fallback;
};

export const slugify = (name) =>
  name
    .toLowerCase()
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 40);

export const SLUG_RE = /^[a-z0-9-]{3,40}$/;
export const RESERVED = ["admin", "api", "auth", "marketplace", "dashboard", "artist", "platform", "t", "settings"];

export const localSlugProblem = (slug) => {
  if (!SLUG_RE.test(slug)) return "Use 3–40 lowercase letters, numbers or hyphens";
  if (RESERVED.includes(slug)) return "This studio URL is reserved";
  return null;
};

export const HEX_RE = /^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$/;

export const textOn = (hex) => {
  if (!HEX_RE.test(hex || "")) return "#FAFAFA";
  let h = hex.slice(1);
  if (h.length === 3) h = h.split("").map((c) => c + c).join("");
  const [r, g, b] = [0, 2, 4].map((i) => parseInt(h.slice(i, i + 2), 16));
  return (0.299 * r + 0.587 * g + 0.114 * b) / 255 > 0.6 ? "#0A0A0A" : "#FAFAFA";
};

export const assetUrl = (path) => (path ? `${process.env.REACT_APP_BACKEND_URL}${path}` : null);

export const homeFor = (u) => {
  if (!u) return "/login";
  if (u.needs_account_type) return "/auth/choose-type";
  if (u.is_platform_admin) return "/platform/tenants";
  const owned = u.memberships.find((m) => m.role === "owner");
  if (owned) return `/studio/${owned.slug}`;
  if (u.account_type === "studio_owner") return "/studio/new";
  if (u.roles.includes("artist")) return "/artist";
  return "/client";
};

export const formatDate = (iso) =>
  iso ? new Date(iso.endsWith("Z") || iso.includes("+") ? iso : `${iso}Z`).toLocaleDateString("en-GB", {
    day: "2-digit", month: "short", year: "numeric",
  }) : "—";
