import { useSelector } from "react-redux";
import { selectCurrentUser, selectOwnedStudios, selectRoles } from "@/features/auth/authSelectors";

// Only pages that exist in the current build.
export const useNavLinks = () => {
  const user = useSelector(selectCurrentUser);
  const roles = useSelector(selectRoles);
  const owned = useSelector(selectOwnedStudios);
  if (!user) return [{ to: "/#studios", label: "Studios", testid: "nav-studios-link" }];
  const links = [];
  if (roles.includes("platform_admin")) links.push({ to: "/platform/tenants", label: "Tenants", testid: "nav-platform-tenants-link" });
  owned.forEach((s, i) => {
    const sfx = owned.length > 1 ? ` · ${s.name}` : "";
    links.push({ to: `/studio/${s.slug}`, label: `Studio${sfx}`, testid: `nav-studio-dashboard-link-${i}` });
    links.push({ to: `/studio/${s.slug}/team`, label: `Team${sfx}`, testid: `nav-studio-team-link-${i}` });
  });
  if (roles.includes("studio_owner") && owned.length === 0) {
    links.push({ to: "/studio/new", label: "Create studio", testid: "nav-create-studio-link" });
  }
  if (roles.includes("artist")) links.push({ to: "/artist", label: "Artist home", testid: "nav-artist-home-link" });
  if (roles.includes("client")) links.push({ to: "/client", label: "Home", testid: "nav-client-home-link" });
  if (!user.is_platform_admin) {
    const n = user.pending_invitations;
    links.push({ to: "/invitations", label: n ? `Invitations (${n})` : "Invitations", testid: "nav-invitations-link" });
  }
  return links;
};
