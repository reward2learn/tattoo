import { Link } from "react-router-dom";
import { useSelector } from "react-redux";
import { ArrowUpRight, Feather, Store } from "lucide-react";
import { selectCurrentUser } from "@/features/auth/authSelectors";
import { selectActiveWorkspace, selectWorkspaces } from "@/features/tenant/tenantSelectors";
import { useGetWorkspaceQuery } from "@/features/tenant/tenantApi";
import { apiErrorMessage, assetUrl } from "@/lib/app";
import { StudioLogo } from "@/components/common/States";
import { WorkspaceSwitcher } from "@/components/layout/WorkspaceSwitcher";
import { InvitationsCallout, PageIntro } from "@/pages/ClientHomePage";

const StudioWorkspace = ({ slug }) => {
  const { data, error, isLoading } = useGetWorkspaceQuery(slug);
  if (isLoading) return <div className="h-32 rounded-lg bg-zinc-900/40 animate-pulse" />;
  if (error) return <p className="text-red-400" data-testid="workspace-error">{apiErrorMessage(error)}</p>;
  const s = data.studio;
  return (
    <div className="flex flex-col sm:flex-row gap-6 sm:items-center" data-testid="studio-workspace-card">
      <StudioLogo src={assetUrl(s.logo_url)} name={s.name} className="h-24 w-32 shrink-0" />
      <div className="min-w-0">
        <p className="font-display text-2xl text-zinc-50">{s.name}</p>
        <p className="mt-1 text-sm text-zinc-400">{s.city} · your role: <span className="text-zinc-200" data-testid="workspace-role">{data.role}</span></p>
        <Link to={`/t/${s.slug}`} className="mt-3 inline-flex items-center gap-1 text-sm text-amber-500 hover:text-amber-400" data-testid="workspace-public-page-link">
          View studio page <ArrowUpRight className="h-4 w-4" />
        </Link>
      </div>
    </div>
  );
};

const IndependentWorkspace = ({ name }) => (
  <div className="flex gap-5 items-start" data-testid="independent-workspace-card">
    <Feather className="h-8 w-8 text-amber-500 shrink-0" />
    <div>
      <p className="font-display text-2xl text-zinc-50">Independent</p>
      <p className="mt-2 text-sm text-zinc-400 max-w-lg">
        Work under your own name, {name}. Designs you create here belong to you; studio work stays in each studio's workspace.
      </p>
    </div>
  </div>
);

export default function ArtistHomePage() {
  const user = useSelector(selectCurrentUser);
  const active = useSelector(selectActiveWorkspace);
  const workspaces = useSelector(selectWorkspaces);
  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16" data-testid="artist-home-page">
      <PageIntro eyebrow="Artist home" title={user.name} />
      <InvitationsCallout />
      <section className="mt-12 rounded-lg border border-zinc-800 bg-zinc-950 p-6 sm:p-8">
        <div className="flex flex-wrap items-center justify-between gap-4 mb-8">
          <p className="font-mono text-[11px] uppercase tracking-[0.25em] text-zinc-500">
            Current workspace · <span className="text-amber-500" data-testid="active-workspace-name">{active.name}</span>
          </p>
          <WorkspaceSwitcher />
        </div>
        {active.slug ? <StudioWorkspace slug={active.slug} /> : <IndependentWorkspace name={user.name.split(" ")[0]} />}
      </section>
      <section className="mt-10">
        <h2 className="font-display text-xl text-zinc-50 mb-4">Your workspaces</h2>
        <ul className="divide-y divide-zinc-900 border border-zinc-900 rounded-lg" data-testid="workspace-list">
          {workspaces.map((w) => (
            <li key={w.key} className="flex items-center gap-3 px-5 py-4 text-sm text-zinc-300" data-testid={`workspace-list-item-${w.key}`}>
              {w.slug ? <Store className="h-4 w-4 text-zinc-500" /> : <Feather className="h-4 w-4 text-zinc-500" />}
              <span className="flex-1">{w.name}</span>
              {w.city && <span className="font-mono text-xs uppercase tracking-widest text-zinc-600">{w.city}</span>}
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
