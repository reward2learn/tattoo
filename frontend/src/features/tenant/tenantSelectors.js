import { createSelector } from "@reduxjs/toolkit";
import { selectArtistStudios } from "@/features/auth/authSelectors";

export const INDEPENDENT = { key: "independent", name: "Independent", slug: null };

export const selectWorkspaces = createSelector([selectArtistStudios], (studios) => [
  INDEPENDENT,
  ...studios.map((m) => ({ key: m.slug, name: m.name, slug: m.slug, city: m.city })),
]);

// Falls back to Independent when the stored studio is no longer an active membership.
export const selectActiveWorkspace = createSelector(
  [selectWorkspaces, (state) => state.tenant.activeWorkspace],
  (workspaces, key) => workspaces.find((w) => w.key === key) ?? INDEPENDENT,
);
