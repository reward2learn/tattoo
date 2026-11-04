import { useState } from "react";
import { useDispatch } from "react-redux";
import { UserPlus } from "lucide-react";
import { useGetTeamQuery, useInviteArtistMutation, useRemoveMemberMutation, useRevokeInvitationMutation } from "@/features/tenant/teamApi";
import { notify } from "@/features/notification/notificationSlice";
import { apiErrorMessage, formatDate } from "@/lib/app";
import { GhostButton, PrimaryButton } from "@/components/common/Form";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { StudioLayout } from "@/components/studio/StudioLayout";

const InviteForm = ({ slug }) => {
  const [email, setEmail] = useState("");
  const [invite, { isLoading }] = useInviteArtistMutation();
  const dispatch = useDispatch();
  const submit = async (e) => {
    e.preventDefault();
    try {
      const res = await invite({ slug, email }).unwrap();
      dispatch(notify({ type: res.email_sent ? "success" : "warning", message: res.message }));
      setEmail("");
    } catch (err) {
      dispatch(notify({ type: "error", message: apiErrorMessage(err) }));
    }
  };
  return (
    <form onSubmit={submit} className="flex flex-col sm:flex-row gap-3" data-testid="team-invite-form">
      <Input type="email" required placeholder="artist@email.com" value={email} onChange={(e) => setEmail(e.target.value)}
        data-testid="team-invite-email-input" className="bg-zinc-900/70 border-zinc-800 h-11 text-zinc-100 sm:max-w-sm" />
      <PrimaryButton type="submit" disabled={isLoading} data-testid="team-invite-submit-button"><UserPlus className="h-4 w-4" /> Invite artist</PrimaryButton>
    </form>
  );
};

const Row = ({ m, action, testid }) => (
  <li className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4 px-5 py-4" data-testid={testid}>
    <div className="min-w-0 flex-1">
      <p className="text-sm text-zinc-100 truncate">{m.name || m.email}</p>
      {m.name && <p className="text-xs text-zinc-500 truncate">{m.email}</p>}
    </div>
    <Badge variant="outline" className="w-fit border-zinc-700 text-zinc-300 font-mono uppercase text-[10px] tracking-widest">{m.role}</Badge>
    <span className="text-xs text-zinc-500 sm:w-32">
      {m.status === "former" ? `Left ${formatDate(m.left_at)}` : m.status === "invited" ? `Invited ${formatDate(m.created_at)}` : `Joined ${formatDate(m.joined_at)}`}
    </span>
    {action}
  </li>
);

const Section = ({ title, items, empty, children, testid }) => (
  <section className="mt-10">
    <h2 className="font-display text-xl text-zinc-50">{title} <span className="text-zinc-600 text-base">({items.length})</span></h2>
    {items.length ? <ul className="mt-4 divide-y divide-zinc-900 border border-zinc-900 rounded-lg" data-testid={testid}>{children}</ul>
      : <p className="mt-3 text-sm text-zinc-500" data-testid={`${testid}-empty`}>{empty}</p>}
  </section>
);

const Team = ({ slug }) => {
  const { data } = useGetTeamQuery(slug);
  const [revoke] = useRevokeInvitationMutation();
  const [remove] = useRemoveMemberMutation();
  const dispatch = useDispatch();
  const run = async (fn, ok) => {
    try { await fn.unwrap(); dispatch(notify({ message: ok })); } catch (err) { dispatch(notify({ type: "error", message: apiErrorMessage(err) })); }
  };
  if (!data) return null;
  return (
    <>
      <Section title="Active members" items={data.active} empty="No members." testid="team-active-list">
        {data.active.map((m) => (
          <Row key={m.id} m={m} testid={`team-active-row-${m.email}`} action={
            <GhostButton onClick={() => run(remove({ slug, id: m.id }), "Member removed")} data-testid={`team-remove-button-${m.email}`}>Remove</GhostButton>} />
        ))}
      </Section>
      <Section title="Pending invitations" items={data.invited} empty="No pending invitations." testid="team-pending-list">
        {data.invited.map((m) => (
          <Row key={m.id} m={m} testid={`team-pending-row-${m.email}`} action={
            <GhostButton onClick={() => run(revoke({ slug, id: m.id }), "Invitation revoked")} data-testid={`team-revoke-button-${m.email}`}>Revoke</GhostButton>} />
        ))}
      </Section>
      <Section title="Former members" items={data.former} empty="No former members." testid="team-former-list">
        {data.former.map((m) => <Row key={m.id} m={m} testid={`team-former-row-${m.email}`} />)}
      </Section>
    </>
  );
};

export default function StudioTeamPage() {
  return (
    <StudioLayout>
      {(studio) => (
        <div data-testid="studio-team-page">
          <p className="text-sm text-zinc-400 mb-4">Invite artists by email. They see the invitation when they sign in with that address.</p>
          <InviteForm slug={studio.slug} />
          <Team slug={studio.slug} />
        </div>
      )}
    </StudioLayout>
  );
}
