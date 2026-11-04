import { Link } from "react-router-dom";
import { Loader2, Lock, MapPinOff } from "lucide-react";

export const FullPageLoader = () => (
  <div className="min-h-[60vh] flex items-center justify-center" data-testid="page-loader">
    <Loader2 className="h-6 w-6 animate-spin text-amber-500" />
  </div>
);

const Message = ({ icon: Icon, title, body, testid }) => (
  <div className="max-w-xl mx-auto px-6 py-24 text-center" data-testid={testid}>
    <Icon className="mx-auto h-8 w-8 text-amber-500" />
    <h1 className="mt-6 font-display text-3xl sm:text-4xl text-zinc-50">{title}</h1>
    <p className="mt-4 text-zinc-400">{body}</p>
    <Link to="/" className="mt-8 inline-block text-sm font-mono uppercase tracking-widest text-amber-500 hover:text-amber-400" data-testid="back-home-link">
      Back to home
    </Link>
  </div>
);

export const NoAccess = () => (
  <Message icon={Lock} testid="no-access-page" title="You don't have access to this page"
    body="Your account doesn't have the role this area needs." />
);

export const NotFound = ({ title = "Page not found", testid = "not-found-page" }) => (
  <Message icon={MapPinOff} testid={testid} title={title} body="The link may be wrong or the page was moved." />
);

export const Eyebrow = ({ children, className = "" }) => (
  <p className={`font-mono text-[11px] uppercase tracking-[0.25em] text-amber-500 ${className}`}>{children}</p>
);

export const StudioLogo = ({ src, name, className = "h-16 w-16", testid }) =>
  src ? (
    <div className={`flex items-center justify-center overflow-hidden rounded-md bg-zinc-900/60 ${className}`}>
      <img src={src} alt={`${name} logo`} className="max-h-full max-w-full object-contain" data-testid={testid} />
    </div>
  ) : (
    <div className={`flex items-center justify-center rounded-md border border-zinc-800 bg-zinc-900 font-display text-xl text-amber-500 ${className}`} data-testid={testid}>
      {name?.[0] ?? "?"}
    </div>
  );
