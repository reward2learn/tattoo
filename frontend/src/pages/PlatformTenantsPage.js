import { Link } from "react-router-dom";
import { useGetPlatformTenantsQuery } from "@/features/tenant/teamApi";
import { formatDate } from "@/lib/app";
import { FullPageLoader } from "@/components/common/States";
import { PageIntro } from "@/pages/ClientHomePage";

export default function PlatformTenantsPage() {
  const { data = [], isLoading } = useGetPlatformTenantsQuery();
  if (isLoading) return <FullPageLoader />;
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16" data-testid="platform-tenants-page">
      <PageIntro eyebrow="Platform admin" title="Tenants">{data.length} studios on InkForge.</PageIntro>
      <div className="mt-10 overflow-x-auto rounded-lg border border-zinc-800">
        <table className="w-full min-w-[640px] text-sm" data-testid="admin-tenants-table">
          <thead className="bg-zinc-900/60 text-left font-mono text-[10px] uppercase tracking-widest text-zinc-500">
            <tr>{["Studio", "Slug", "Owner", "Active artists", "Created"].map((h) => <th key={h} className="px-4 py-3 font-normal">{h}</th>)}</tr>
          </thead>
          <tbody className="divide-y divide-zinc-900">
            {data.map((t, i) => (
              <tr key={t.id} className="hover:bg-zinc-900/40" data-testid={`admin-tenants-table-row-${i}`}>
                <td className="px-4 py-3 text-zinc-100">{t.name}</td>
                <td className="px-4 py-3 font-mono"><Link to={`/t/${t.slug}`} className="text-amber-500 hover:text-amber-400" data-testid={`admin-tenant-link-${t.slug}`}>{t.slug}</Link></td>
                <td className="px-4 py-3 text-zinc-300">{t.owner.name}<span className="block text-xs text-zinc-500">{t.owner.email}</span></td>
                <td className="px-4 py-3 text-zinc-100" data-testid={`admin-tenant-artist-count-${t.slug}`}>{t.active_artist_count}</td>
                <td className="px-4 py-3 text-zinc-400">{formatDate(t.created_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
