export const AuthCard = ({ eyebrow, title, children, testid }) => (
  <div className="relative min-h-[calc(100vh-4rem)] flex items-center justify-center px-4 py-16 overflow-hidden" data-testid={testid}>
    <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(245,158,11,0.08),transparent_60%)] pointer-events-none" />
    <div className="relative w-full max-w-md rounded-lg border border-zinc-800 bg-zinc-950/80 backdrop-blur-xl p-6 sm:p-8 animate-rise">
      <p className="font-mono text-[11px] uppercase tracking-[0.25em] text-amber-500">{eyebrow}</p>
      <h1 className="mt-3 font-display text-3xl sm:text-4xl text-zinc-50">{title}</h1>
      <div className="mt-8">{children}</div>
    </div>
  </div>
);

export const Divider = () => (
  <div className="my-6 flex items-center gap-3 text-[11px] font-mono uppercase tracking-widest text-zinc-600">
    <span className="h-px flex-1 bg-zinc-800" /> or <span className="h-px flex-1 bg-zinc-800" />
  </div>
);

export const FormError = ({ message, testid }) =>
  message ? (
    <div className="rounded-md border border-red-500/30 bg-red-500/10 px-3 py-2 text-sm text-red-300" role="alert" data-testid={testid}>
      {message}
    </div>
  ) : null;
