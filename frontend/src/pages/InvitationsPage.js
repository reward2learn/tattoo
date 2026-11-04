import { useDispatch } from "react-redux";
import { Link } from "react-router-dom";
import { MapPin } from "lucide-react";
import { useAcceptInvitationMutation, useDeclineInvitationMutation, useGetMyInvitationsQuery } from "@/features/tenant/tenantApi";
import { notify } from "@/features/notification/notificationSlice";
import { apiErrorMessage } from "@/lib/app";
import { GhostButton, PrimaryButton } from "@/components/common/Form";
import { FullPageLoader } from "@/components/common/States";
import { PageIntro } from "@/pages/ClientHomePage";

export default function InvitationsPage() {
  const { data, isLoading } = useGetMyInvitationsQuery();
  const [accept, { isLoading: accepting }] = useAcceptInvitationMutation();
  const [decline, { isLoading: declining }] = useDeclineInvitationMutation();
  const dispatch = useDispatch();

  const act = async (fn, msg) => {
    try {
      await fn.unwrap();
      dispatch(notify({ message: msg }));
    } catch (err) {
      dispatch(notify({ type: "error", message: apiErrorMessage(err) }));
    }
  };

  if (isLoading) return <FullPageLoader />;
  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16" data-testid="invitations-page">
      <PageIntro eyebrow="Invitations" title="Studio invitations" />
      {data?.length ? (
        <ul className="mt-10 space-y-4" data-testid="invitations-list">
          {data.map((inv) => (
            <li key={inv.id} className="rounded-lg border border-zinc-800 bg-zinc-950 p-5 flex flex-col sm:flex-row sm:items-center gap-4" data-testid={`invitation-card-${inv.studio.slug}`}>
              <div className="flex-1 min-w-0">
                <Link to={`/t/${inv.studio.slug}`} className="font-display text-xl text-zinc-50 hover:text-amber-500">{inv.studio.name}</Link>
                <p className="mt-1 text-sm text-zinc-400 flex items-center gap-1"><MapPin className="h-3.5 w-3.5" /> {inv.studio.city} · invited as {inv.role}</p>
              </div>
              <div className="flex gap-2">
                <PrimaryButton disabled={accepting} onClick={() => act(accept(inv.id), `You joined ${inv.studio.name}`)} data-testid={`invitation-accept-button-${inv.studio.slug}`}>Accept</PrimaryButton>
                <GhostButton className="h-11" disabled={declining} onClick={() => act(decline(inv.id), "Invitation declined")} data-testid={`invitation-decline-button-${inv.studio.slug}`}>Decline</GhostButton>
              </div>
            </li>
          ))}
        </ul>
      ) : (
        <p className="mt-10 text-zinc-500" data-testid="invitations-empty">You have no pending invitations.</p>
      )}
    </div>
  );
}
