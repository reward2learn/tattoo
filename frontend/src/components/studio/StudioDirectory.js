import { Link } from "react-router-dom";
import { ArrowUpRight, MapPin } from "lucide-react";
import { useGetPublicStudiosQuery } from "@/features/tenant/tenantApi";
import { assetUrl } from "@/lib/app";
import { StudioLogo } from "@/components/common/States";

export const StudioDirectory = ({ testid = "studio-directory" }) => {
  const { data = [], isLoading } = useGetPublicStudiosQuery();
  if (isLoading) return <div className="h-40 rounded-md bg-zinc-900/40 animate-pulse" />;
  if (!data.length) return <p className="text-zinc-500">No studios yet.</p>;
  return (
    <div className="grid gap-5 sm:grid-cols-2" data-testid={testid}>
      {data.map((s, i) => (
        <Link
          key={s.slug}
          to={`/t/${s.slug}`}
          data-testid={`studio-card-${s.slug}`}
          className="group relative flex gap-5 items-center rounded-lg border border-zinc-800 bg-zinc-950 p-5 hover:border-zinc-600 transition-colors animate-rise"
          style={{ animationDelay: `${i * 80}ms` }}
        >
          <span className="absolute left-0 top-0 h-full w-1 rounded-l-lg" style={{ background: s.accent_color }} />
          <StudioLogo src={assetUrl(s.logo_url)} name={s.name} className="h-20 w-24 shrink-0" />
          <div className="min-w-0">
            <p className="font-display text-xl text-zinc-50 truncate">{s.name}</p>
            <p className="mt-1 text-sm text-zinc-400 line-clamp-2">{s.tagline}</p>
            <p className="mt-2 inline-flex items-center gap-1 text-xs font-mono uppercase tracking-widest text-zinc-500">
              <MapPin className="h-3 w-3" /> {s.city}
            </p>
          </div>
          <ArrowUpRight className="ml-auto h-5 w-5 shrink-0 text-zinc-600 group-hover:text-amber-500 transition-colors" />
        </Link>
      ))}
    </div>
  );
};
