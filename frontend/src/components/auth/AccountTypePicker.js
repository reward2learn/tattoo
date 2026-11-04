import { Brush, Building2, Sparkles } from "lucide-react";

export const ACCOUNT_TYPES = [
  { value: "client", label: "I want a tattoo", body: "Find a studio and bring your idea to the right artist.", icon: Sparkles },
  { value: "artist", label: "I'm a tattoo artist", body: "Work independently and join studios that invite you.", icon: Brush },
  { value: "studio_owner", label: "I run a studio", body: "Create a branded studio page and manage your team.", icon: Building2 },
];

export const AccountTypePicker = ({ value, onChange }) => (
  <div className="grid gap-3" role="radiogroup" data-testid="account-type-picker">
    {ACCOUNT_TYPES.map(({ value: v, label, body, icon: Icon }) => {
      const active = value === v;
      return (
        <button
          type="button"
          key={v}
          role="radio"
          aria-checked={active}
          onClick={() => onChange(v)}
          data-testid={`account-type-${v}`}
          className={`flex items-start gap-4 text-left rounded-md border p-4 transition-colors ${
            active ? "border-amber-500 bg-amber-500/10" : "border-zinc-800 bg-zinc-900/50 hover:border-zinc-600"
          }`}
        >
          <Icon className={`mt-0.5 h-5 w-5 shrink-0 ${active ? "text-amber-500" : "text-zinc-500"}`} />
          <span>
            <span className="block text-sm font-semibold text-zinc-100">{label}</span>
            <span className="block mt-1 text-xs text-zinc-400">{body}</span>
          </span>
        </button>
      );
    })}
  </div>
);
