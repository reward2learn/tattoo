import { Link, NavLink, useNavigate } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import { LogOut, Menu } from "lucide-react";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { selectCurrentUser } from "@/features/auth/authSelectors";
import { signOut } from "@/features/auth/authSlice";
import { selectMobileNavOpen } from "@/features/ui/uiSelectors";
import { setMobileNavOpen } from "@/features/ui/uiSlice";
import { useNavLinks } from "@/components/layout/useNavLinks";
import { WorkspaceSwitcher } from "@/components/layout/WorkspaceSwitcher";

export const Wordmark = () => (
  <Link to="/" className="flex items-center gap-2 shrink-0" data-testid="nav-logo-link">
    <span className="h-7 w-7 rotate-45 border border-amber-500/80 flex items-center justify-center">
      <span className="h-2 w-2 bg-amber-500 -rotate-45" />
    </span>
    <span className="font-display text-xl tracking-tight text-zinc-50">InkForge</span>
  </Link>
);

const linkCls = ({ isActive }) =>
  `text-sm transition-colors ${isActive ? "text-amber-500" : "text-zinc-400 hover:text-zinc-100"}`;

const useSignOut = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  return async () => {
    dispatch(setMobileNavOpen(false));
    await dispatch(signOut());
    navigate("/", { replace: true });
  };
};

const GuestActions = ({ mobile }) => (
  <div className={mobile ? "flex flex-col gap-3" : "flex items-center gap-3"}>
    <Link to="/login" data-testid={mobile ? "mobile-nav-signin-button" : "nav-signin-button"}
      className="text-sm text-zinc-300 hover:text-zinc-50 px-3 py-2">Sign in</Link>
    <Link to="/signup" data-testid={mobile ? "mobile-nav-signup-button" : "nav-signup-button"}
      className="text-sm font-medium px-4 py-2 rounded-md bg-amber-500 text-zinc-950 hover:bg-amber-400 transition-colors text-center">Sign up</Link>
  </div>
);

const MobileNav = ({ links, user, onSignOut }) => {
  const open = useSelector(selectMobileNavOpen);
  const dispatch = useDispatch();
  const close = () => dispatch(setMobileNavOpen(false));
  return (
    <Sheet open={open} onOpenChange={(v) => dispatch(setMobileNavOpen(v))}>
      <SheetTrigger className="md:hidden p-2 -mr-2 text-zinc-300" data-testid="mobile-nav-toggle" aria-label="Open menu">
        <Menu className="h-6 w-6" />
      </SheetTrigger>
      <SheetContent side="right" className="w-[85vw] max-w-xs bg-zinc-950 border-zinc-800" data-testid="mobile-nav-sheet">
        <SheetHeader><SheetTitle className="font-display text-left text-zinc-50">Menu</SheetTitle></SheetHeader>
        {user && <p className="mt-6 text-sm text-zinc-400" data-testid="mobile-nav-user-name">{user.name}</p>}
        <nav className="mt-6 flex flex-col gap-4">
          {links.map((l) => (
            <NavLink key={l.to} to={l.to} onClick={close} className={linkCls} data-testid={`mobile-${l.testid}`}>{l.label}</NavLink>
          ))}
        </nav>
        <div className="mt-8 border-t border-zinc-800 pt-6">
          {user ? (
            <div className="flex flex-col gap-4">
              <WorkspaceSwitcher className="w-full justify-between" />
              <button onClick={onSignOut} className="flex items-center gap-2 text-sm text-zinc-300 hover:text-zinc-50" data-testid="mobile-nav-signout-button">
                <LogOut className="h-4 w-4" /> Sign out
              </button>
            </div>
          ) : (
            <div onClick={close}><GuestActions mobile /></div>
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
};

export const SiteHeader = () => {
  const user = useSelector(selectCurrentUser);
  const links = useNavLinks();
  const onSignOut = useSignOut();
  return (
    <header className="sticky top-0 z-50 backdrop-blur-xl bg-zinc-950/80 border-b border-zinc-800/80" data-testid="site-header">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-6">
        <Wordmark />
        <nav className="hidden md:flex items-center gap-6 flex-1">
          {links.map((l) => <NavLink key={l.to} to={l.to} className={linkCls} data-testid={l.testid}>{l.label}</NavLink>)}
        </nav>
        <div className="hidden md:flex items-center gap-4">
          {user ? (
            <>
              <WorkspaceSwitcher />
              <span className="text-sm text-zinc-300 max-w-[12rem] truncate" data-testid="nav-user-name">{user.name}</span>
              <button onClick={onSignOut} className="inline-flex items-center gap-1.5 text-sm text-zinc-400 hover:text-zinc-50 transition-colors" data-testid="nav-signout-button">
                <LogOut className="h-4 w-4" /> Sign out
              </button>
            </>
          ) : <GuestActions />}
        </div>
        <MobileNav links={links} user={user} onSignOut={onSignOut} />
      </div>
    </header>
  );
};

export const SiteFooter = () => (
  <footer className="border-t border-zinc-900 mt-24">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 flex flex-col sm:flex-row gap-4 justify-between text-xs text-zinc-500">
      <span className="font-mono uppercase tracking-widest">InkForge · Jakarta — Bali</span>
      <span>Original tattoo art, credited to the artists who draw it.</span>
    </div>
  </footer>
);
