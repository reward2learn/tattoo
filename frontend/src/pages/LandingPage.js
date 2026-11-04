import { Link } from "react-router-dom";
import { useSelector } from "react-redux";
import { selectCurrentUser } from "@/features/auth/authSelectors";
import { homeFor } from "@/lib/app";
import { Eyebrow } from "@/components/common/States";
import { StudioDirectory } from "@/components/studio/StudioDirectory";

const PILLARS = [
  { n: "01", t: "For clients", b: "Describe the tattoo you're imagining and reach studios whose artists actually draw that style." },
  { n: "02", t: "For artists", b: "Keep an independent workspace and join the studios that invite you — every design stays credited to you." },
  { n: "03", t: "For studios", b: "A branded home at your own URL, your colors and logo, and a team you control." },
];

const Hero = () => {
  const user = useSelector(selectCurrentUser);
  return (
    <section className="relative overflow-hidden border-b border-zinc-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 lg:py-28 grid lg:grid-cols-12 gap-12 items-center">
        <div className="lg:col-span-6 animate-rise">
          <Eyebrow>Tattoo design platform · Indonesia</Eyebrow>
          <h1 className="mt-6 font-display text-4xl sm:text-5xl lg:text-6xl leading-[1.05] text-zinc-50" data-testid="landing-headline">
            Ideas become ink.<br /><span className="italic text-amber-500">Artists get the credit.</span>
          </h1>
          <p className="mt-6 max-w-lg text-base text-zinc-400 leading-relaxed">
            InkForge connects people who want a tattoo with the studios and artists who draw it — every studio with its
            own branded page, every design attributed to the hand that made it.
          </p>
          <div className="mt-10 flex flex-wrap gap-3">
            {user ? (
              <Link to={homeFor(user)} className="h-11 px-6 inline-flex items-center rounded-md bg-amber-500 text-zinc-950 text-sm font-semibold hover:bg-amber-400 transition-colors" data-testid="landing-go-home-button">Go to your home</Link>
            ) : (
              <>
                <Link to="/signup" className="h-11 px-6 inline-flex items-center rounded-md bg-amber-500 text-zinc-950 text-sm font-semibold hover:bg-amber-400 transition-colors" data-testid="landing-signup-button">Sign up</Link>
                <Link to="/login" className="h-11 px-6 inline-flex items-center rounded-md border border-zinc-700 text-sm text-zinc-200 hover:border-zinc-500 transition-colors" data-testid="landing-signin-button">Sign in</Link>
              </>
            )}
          </div>
        </div>
        <div className="lg:col-span-6 relative animate-rise" style={{ animationDelay: "150ms" }}>
          <div className="absolute -inset-4 border border-amber-500/20 rounded-lg translate-x-4 translate-y-4" />
          <img src="/img/hero.jpg" alt="Tattoo flash sheets on an artist's workbench" className="relative w-full aspect-[3/2] object-cover rounded-lg border border-zinc-800" data-testid="landing-hero-image" />
        </div>
      </div>
    </section>
  );
};

export default function LandingPage() {
  return (
    <div data-testid="landing-page">
      <Hero />
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 grid md:grid-cols-3 gap-px bg-zinc-900 border border-zinc-900 rounded-lg overflow-hidden">
        {PILLARS.map((p) => (
          <div key={p.n} className="bg-zinc-950 p-8">
            <span className="font-mono text-xs text-amber-500">{p.n}</span>
            <h2 className="mt-4 font-display text-2xl text-zinc-50">{p.t}</h2>
            <p className="mt-3 text-sm text-zinc-400 leading-relaxed">{p.b}</p>
          </div>
        ))}
      </section>
      <section id="studios" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-8">
        <Eyebrow>Studios on InkForge</Eyebrow>
        <h2 className="mt-3 mb-8 font-display text-3xl text-zinc-50">Visit a studio</h2>
        <StudioDirectory testid="landing-studio-directory" />
      </section>
    </div>
  );
}
