import { Link } from "react-router-dom";
import { useSelector } from "react-redux";
import { Mail } from "lucide-react";
import { selectCurrentUser } from "@/features/auth/authSelectors";
import { Eyebrow } from "@/components/common/States";
import { StudioDirectory } from "@/components/studio/StudioDirectory";

export const PageIntro = ({ eyebrow, title, children }) => (
  <div className="animate-rise">
    <Eyebrow>{eyebrow}</Eyebrow>
    <h1 className="mt-3 font-display text-4xl sm:text-5xl text-zinc-50">{title}</h1>
    {children && <div className="mt-4 text-zinc-400 max-w-2xl">{children}</div>}
  </div>
);

export const InvitationsCallout = () => {
  const user = useSelector(selectCurrentUser);
  if (!user?.pending_invitations) return null;
  return (
    <Link to="/invitations" data-testid="pending-invitations-callout"
      className="mt-8 flex items-center gap-3 rounded-md border border-amber-500/40 bg-amber-500/10 px-4 py-3 text-sm text-amber-200 hover:bg-amber-500/15 transition-colors">
      <Mail className="h-4 w-4" /> You have {user.pending_invitations} pending studio invitation{user.pending_invitations > 1 ? "s" : ""}.
    </Link>
  );
};

export default function ClientHomePage() {
  const user = useSelector(selectCurrentUser);
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16" data-testid="client-home-page">
      <PageIntro eyebrow="Your home" title={`Hello, ${user.name.split(" ")[0]}`}>
        Browse studios, see who works there, and get in touch with the one that fits your idea.
      </PageIntro>
      <InvitationsCallout />
      <h2 className="mt-14 mb-6 font-display text-2xl text-zinc-50">Studios</h2>
      <StudioDirectory testid="client-studio-directory" />
    </div>
  );
}
