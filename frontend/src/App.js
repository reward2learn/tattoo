import "@/App.css";
import { BrowserRouter, Navigate, Route, Routes, useLocation } from "react-router-dom";
import { useSelector } from "react-redux";
import { useMeQuery } from "@/features/auth/authApi";
import { selectCurrentUser } from "@/features/auth/authSelectors";
import { ToastBridge } from "@/features/notification/ToastBridge";
import { homeFor } from "@/lib/app";
import { SiteFooter, SiteHeader } from "@/components/layout/SiteHeader";
import { RequireAuth, RequireStudioOwner } from "@/components/auth/RequireAuth";
import { AuthCallback } from "@/components/auth/GoogleAuth";
import { NotFound } from "@/components/common/States";
import LandingPage from "@/pages/LandingPage";
import LoginPage from "@/pages/LoginPage";
import SignupPage from "@/pages/SignupPage";
import ChooseTypePage from "@/pages/ChooseTypePage";
import ClientHomePage from "@/pages/ClientHomePage";
import ArtistHomePage from "@/pages/ArtistHomePage";
import CreateStudioPage from "@/pages/CreateStudioPage";
import StudioBrandingPage from "@/pages/StudioBrandingPage";
import StudioTeamPage from "@/pages/StudioTeamPage";
import InvitationsPage from "@/pages/InvitationsPage";
import PlatformTenantsPage from "@/pages/PlatformTenantsPage";
import { PublicStudioContactPage, PublicStudioPage } from "@/pages/PublicStudioPages";

const HomeRedirect = () => {
  const user = useSelector(selectCurrentUser);
  return <Navigate to={homeFor(user)} replace />;
};

const guard = (el, roles) => <RequireAuth roles={roles}>{el}</RequireAuth>;

const AppRoutes = () => (
  <Routes>
    <Route path="/" element={<LandingPage />} />
    <Route path="/login" element={<LoginPage />} />
    <Route path="/signup" element={<SignupPage />} />
    <Route path="/home" element={guard(<HomeRedirect />)} />
    <Route path="/auth/choose-type" element={guard(<ChooseTypePage />)} />
    <Route path="/client" element={guard(<ClientHomePage />, ["client"])} />
    <Route path="/artist" element={guard(<ArtistHomePage />, ["artist"])} />
    <Route path="/invitations" element={guard(<InvitationsPage />)} />
    <Route path="/studio/new" element={guard(<CreateStudioPage />, ["studio_owner"])} />
    <Route path="/studio/:slug" element={<RequireStudioOwner><StudioBrandingPage /></RequireStudioOwner>} />
    <Route path="/studio/:slug/team" element={<RequireStudioOwner><StudioTeamPage /></RequireStudioOwner>} />
    <Route path="/platform/tenants" element={guard(<PlatformTenantsPage />, ["platform_admin"])} />
    <Route path="/t/:slug" element={<PublicStudioPage />} />
    <Route path="/t/:slug/contact" element={<PublicStudioContactPage />} />
    <Route path="*" element={<NotFound />} />
  </Routes>
);

const AppRouter = () => {
  const location = useLocation();
  const returningFromGoogle = location.hash?.includes("session_id=");
  useMeQuery(undefined, { skip: returningFromGoogle });
  return (
    <div className="min-h-screen flex flex-col overflow-x-hidden">
      <SiteHeader />
      <main className="flex-1">{returningFromGoogle ? <AuthCallback /> : <AppRoutes />}</main>
      <SiteFooter />
      <ToastBridge />
    </div>
  );
};

export default function App() {
  return (
    <BrowserRouter>
      <AppRouter />
    </BrowserRouter>
  );
}
