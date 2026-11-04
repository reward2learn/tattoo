import { createSelector } from "@reduxjs/toolkit";

const EMPTY = [];

export const selectAuthStatus = (state) => state.auth.status;
export const selectCurrentUser = (state) => state.auth.user;
export const selectIsAuthenticated = (state) => state.auth.status === "authenticated";
export const selectRoles = (state) => state.auth.user?.roles ?? EMPTY;
export const selectMemberships = (state) => state.auth.user?.memberships ?? EMPTY;
export const selectOwnedStudios = createSelector([selectMemberships], (ms) => ms.filter((m) => m.role === "owner"));
export const selectArtistStudios = createSelector([selectMemberships], (ms) => ms.filter((m) => m.role === "artist"));
