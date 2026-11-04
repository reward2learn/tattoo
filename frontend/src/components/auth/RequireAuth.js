import { useSelector } from "react-redux";
import { Navigate, useLocation, useParams } from "react-router-dom";
import { selectAuthStatus, selectCurrentUser } from "@/features/auth/authSelectors";
import { NoAccess, FullPageLoader } from "@/components/common/States";

export const RequireAuth = ({ roles, children }) => {
  const status = useSelector(selectAuthStatus);
  const user = useSelector(selectCurrentUser);
  const location = useLocation();
  if (status === "checking") return <FullPageLoader />;
  if (status !== "authenticated") {
    return <Navigate to="/login" replace state={{ from: location.pathname + location.search }} />;
  }
  if (user.needs_account_type && location.pathname !== "/auth/choose-type") {
    return <Navigate to="/auth/choose-type" replace />;
  }
  if (roles && !roles.some((r) => user.roles.includes(r))) return <NoAccess />;
  return children;
};

export const RequireStudioOwner = ({ children }) => {
  const { slug } = useParams();
  const user = useSelector(selectCurrentUser);
  return (
    <RequireAuth>
      {user?.memberships.some((m) => m.slug === slug && m.role === "owner") ? children : <NoAccess />}
    </RequireAuth>
  );
};
