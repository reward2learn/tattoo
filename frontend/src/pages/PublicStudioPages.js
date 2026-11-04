import { Link, NavLink, useParams } from "react-router-dom";
import { AtSign, Mail, MapPin } from "lucide-react";
import { useGetPublicStudioQuery } from "@/features/tenant/tenantApi";
import { assetUrl, textOn } from "@/lib/app";
import { FullPageLoader, NotFound, StudioLogo } from "@/components/common/States";

const StudioFrame = ({ studio, children }) => {
  const fg = textOn(studio.primary_color);
  const sub = ({ isActive }) => `text-sm pb-1 border-b-2 transition-colors ${isActive ? "border-[var(--studio-accent)]" : "border-transparent opacity-70 hover:opacity-100"}`;
  return (
    <div style={{ "--studio-primary": studio.primary_color, "--studio-accent": studio.accent_color, background: studio.primary_color, color: fg }}
      className="min-h-[calc(100vh-4rem)]" data-testid="public-studio-theme">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between gap-4 py-5 border-b" style={{ borderColor: `${studio.accent_color}33` }}>
          <Link to={`/t/${studio.slug}`} className="flex items-center gap-3 min-w-0" data-testid="public-studio-home-link">
            <StudioLogo src={assetUrl(studio.logo_url)} name={studio.name} className="h-10 w-14 shrink-0" />
            <span className="font-display text-lg truncate">{studio.name}</span>
          </Link>
          <nav className="flex gap-5 shrink-0">
            <NavLink end to={`/t/${studio.slug}`} className={sub} data-testid="public-studio-nav-home">Studio</NavLink>
            <NavLink to={`/t/${studio.slug}/contact`} className={sub} data-testid="public-studio-contact-link">Contact</NavLink>
          </nav>
        </div>
        {children}
      </div>
    </div>
  );
};

const useStudio = () => {
  const { slug } = useParams();
  return useGetPublicStudioQuery(slug);
};

const Gate = ({ children }) => {
  const { data, error, isLoading } = useStudio();
  if (isLoading) return <FullPageLoader />;
  if (error?.status === 404 || !data) return <NotFound title="Studio not found" testid="studio-not-found" />;
  return <StudioFrame studio={data}>{children(data)}</StudioFrame>;
};

const Hero = ({ s }) => (
  <section className="py-14 sm:py-20 grid gap-10 lg:grid-cols-12 items-center animate-rise">
    <div className="lg:col-span-5 flex justify-center lg:justify-start">
      <StudioLogo src={assetUrl(s.logo_url)} name={s.name} className="h-56 w-full max-w-sm" testid="public-studio-logo" />
    </div>
    <div className="lg:col-span-7">
      <p className="inline-flex items-center gap-1.5 font-mono text-xs uppercase tracking-[0.25em]" style={{ color: s.accent_color }} data-testid="public-studio-city">
        <MapPin className="h-3.5 w-3.5" /> {s.city}
      </p>
      <h1 className="mt-4 font-display text-4xl sm:text-5xl lg:text-6xl leading-tight" data-testid="public-studio-name">{s.name}</h1>
      <p className="mt-4 text-lg italic font-display" style={{ color: s.accent_color }} data-testid="public-studio-tagline">{s.tagline}</p>
      <p className="mt-6 leading-relaxed opacity-80 max-w-2xl whitespace-pre-line" data-testid="public-studio-about">{s.about}</p>
    </div>
  </section>
);

const Roster = ({ artists, accent }) => (
  <section className="pb-20">
    <h2 className="font-display text-2xl">Artists</h2>
    {artists.length ? (
      <ul className="mt-6 grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3" data-testid="public-studio-roster">
        {artists.map((a) => (
          <li key={a.id} className="flex items-center gap-4 rounded-lg border p-4" style={{ borderColor: "var(--studio-accent)" }} data-testid={`public-roster-artist-${a.id}`}>
            <span className="h-12 w-12 shrink-0 rounded-full flex items-center justify-center font-display text-lg"
              style={{ background: "var(--studio-accent)", color: textOn(accent) }}>
              {a.name[0]}
            </span>
            <span className="font-medium">{a.name}</span>
          </li>
        ))}
      </ul>
    ) : <p className="mt-4 opacity-60" data-testid="public-studio-roster-empty">No artists listed yet.</p>}
  </section>
);

export const PublicStudioPage = () => (
  <Gate>{(s) => <div data-testid="public-studio-page"><Hero s={s} /><Roster artists={s.artists} accent={s.accent_color} /></div>}</Gate>
);

const ContactRow = ({ icon: Icon, label, value, href, testid }) => (
  <div className="flex items-start gap-4 py-5 border-b" style={{ borderColor: "color-mix(in srgb, var(--studio-accent) 25%, transparent)" }}>
    <Icon className="h-5 w-5 mt-0.5" style={{ color: "var(--studio-accent)" }} />
    <div className="min-w-0">
      <p className="font-mono text-[10px] uppercase tracking-widest opacity-60">{label}</p>
      {href ? <a href={href} className="mt-1 block text-lg break-all hover:underline" data-testid={testid}>{value}</a>
        : <p className="mt-1 text-lg" data-testid={testid}>{value || "—"}</p>}
    </div>
  </div>
);

export const PublicStudioContactPage = () => (
  <Gate>
    {(s) => (
      <section className="py-14 sm:py-20 max-w-2xl animate-rise" data-testid="public-studio-contact-page">
        <h1 className="font-display text-4xl sm:text-5xl">Get in touch</h1>
        <p className="mt-4 opacity-75">Reach {s.name} directly to talk about your tattoo.</p>
        <div className="mt-10">
          <ContactRow icon={Mail} label="Email" value={s.contact_email} href={s.contact_email ? `mailto:${s.contact_email}` : null} testid="public-contact-email" />
          <ContactRow icon={AtSign} label="Instagram" value={s.instagram}
            href={s.instagram ? `https://instagram.com/${s.instagram.replace(/^@/, "")}` : null} testid="public-contact-instagram" />
          <ContactRow icon={MapPin} label="City" value={s.city} testid="public-contact-city" />
        </div>
      </section>
    )}
  </Gate>
);
