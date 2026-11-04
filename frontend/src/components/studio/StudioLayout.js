import { NavLink, useParams } from "react-router-dom";
import { ArrowUpRight } from "lucide-react";
import { useGetStudioSettingsQuery } from "@/features/tenant/tenantApi";
import { assetUrl } from "@/lib/app";
import { Eyebrow, FullPageLoader, StudioLogo } from "@/components/common/States";

const tab = ({ isActive }) =>
  `px-4 py-2 text-sm rounded-md transition-colors ${isActive ? "bg-zinc-800 text-zinc-50" : "text-zinc-400 hover:text-zinc-100"}`;

export const StudioLayout = ({ children }) => {
  const { slug } = useParams();
  const { data: studio, isLoading } = useGetStudioSettingsQuery(slug);
  if (isLoading || !studio) return <FullPageLoader />;
  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 sm:py-14" data-testid="studio-dashboard-layout">
      <div className="flex flex-col sm:flex-row sm:items-center gap-5 animate-rise">
        <StudioLogo src={assetUrl(studio.logo_url)} name={studio.name} className="h-20 w-28 shrink-0" testid="dashboard-studio-logo" />
        <div className="min-w-0 flex-1">
          <Eyebrow>Studio dashboard</Eyebrow>
          <h1 className="mt-2 font-display text-3xl sm:text-4xl text-zinc-50 truncate" data-testid="dashboard-studio-name">{studio.name}</h1>
        </div>
      </div>
      <nav className="mt-8 flex flex-wrap gap-2 border-b border-zinc-900 pb-4">
        <NavLink end to={`/studio/${slug}`} className={tab} data-testid="studio-tab-branding">Branding</NavLink>
        <NavLink to={`/studio/${slug}/team`} className={tab} data-testid="studio-tab-team">Team</NavLink>
        <a href={`/t/${slug}`} target="_blank" rel="noreferrer" className="px-4 py-2 text-sm text-zinc-400 hover:text-amber-500 inline-flex items-center gap-1" data-testid="studio-tab-public-page">
          Public page <ArrowUpRight className="h-4 w-4" />
        </a>
      </nav>
      <div className="mt-8">{children(studio)}</div>
    </div>
  );
};
