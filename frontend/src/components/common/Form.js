import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

export const Field = ({ id, label, error, hint, children }) => (
  <div className="space-y-2">
    <Label htmlFor={id} className="text-xs font-mono uppercase tracking-widest text-zinc-400">{label}</Label>
    {children}
    {hint && !error && <p className="text-xs text-zinc-500">{hint}</p>}
    {error && <p className="text-sm text-red-400" data-testid={`${id}-error`}>{error}</p>}
  </div>
);

const inputCls = "bg-zinc-900/70 border-zinc-800 text-zinc-100 placeholder:text-zinc-600 focus-visible:ring-amber-500/60 h-11";

export const TextField = ({ id, label, error, hint, ...props }) => (
  <Field id={id} label={label} error={error} hint={hint}>
    <Input id={id} data-testid={id} className={inputCls} {...props} />
  </Field>
);

export const AreaField = ({ id, label, error, hint, ...props }) => (
  <Field id={id} label={label} error={error} hint={hint}>
    <Textarea id={id} data-testid={id} className={`${inputCls} h-auto min-h-[120px]`} {...props} />
  </Field>
);

export const PrimaryButton = ({ children, className = "", ...props }) => (
  <button
    className={`inline-flex items-center justify-center gap-2 h-11 px-6 rounded-md bg-amber-500 text-zinc-950 text-sm font-semibold hover:bg-amber-400 active:scale-[0.98] transition-[background-color,transform] disabled:opacity-50 disabled:pointer-events-none ${className}`}
    {...props}
  >
    {children}
  </button>
);

export const GhostButton = ({ children, className = "", ...props }) => (
  <button
    className={`inline-flex items-center justify-center gap-2 h-9 px-4 rounded-md border border-zinc-800 text-sm text-zinc-300 hover:border-zinc-600 hover:text-zinc-50 transition-colors disabled:opacity-50 ${className}`}
    {...props}
  >
    {children}
  </button>
);
