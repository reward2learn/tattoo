import { useDispatch, useSelector } from "react-redux";
import { Check, ChevronDown, Layers } from "lucide-react";
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { selectActiveWorkspace, selectWorkspaces } from "@/features/tenant/tenantSelectors";
import { setActiveWorkspace } from "@/features/tenant/tenantSlice";
import { selectRoles } from "@/features/auth/authSelectors";

export const WorkspaceSwitcher = ({ className = "" }) => {
  const workspaces = useSelector(selectWorkspaces);
  const active = useSelector(selectActiveWorkspace);
  const roles = useSelector(selectRoles);
  const dispatch = useDispatch();
  if (!roles.includes("artist") || workspaces.length < 2) return null;
  return (
    <DropdownMenu>
      <DropdownMenuTrigger
        data-testid="workspace-switcher-dropdown"
        className={`inline-flex items-center gap-2 h-9 px-3 rounded-md border border-zinc-800 bg-zinc-900/70 text-sm text-zinc-200 hover:border-amber-500/60 transition-colors ${className}`}
      >
        <Layers className="h-4 w-4 text-amber-500" />
        <span className="max-w-[10rem] truncate" data-testid="workspace-switcher-current">{active.name}</span>
        <ChevronDown className="h-3.5 w-3.5 text-zinc-500" />
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-60 bg-zinc-950 border-zinc-800">
        <DropdownMenuLabel className="font-mono text-[10px] uppercase tracking-widest text-zinc-500">Workspace</DropdownMenuLabel>
        <DropdownMenuSeparator className="bg-zinc-800" />
        {workspaces.map((w) => (
          <DropdownMenuItem
            key={w.key}
            data-testid={`workspace-option-${w.key}`}
            onSelect={() => dispatch(setActiveWorkspace(w.key))}
            className="flex items-center justify-between cursor-pointer"
          >
            <span className="truncate">{w.name}</span>
            {w.key === active.key && <Check className="h-4 w-4 text-amber-500" />}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
};
