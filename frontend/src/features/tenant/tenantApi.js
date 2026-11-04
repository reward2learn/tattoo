import { api } from "@/app/api";

export const tenantApi = api.injectEndpoints({
  endpoints: (b) => ({
    getPublicStudios: b.query({ query: () => "public/studios", providesTags: ["PublicStudio"] }),
    getPublicStudio: b.query({
      query: (slug) => `public/studios/${slug}`,
      providesTags: (r, e, slug) => [{ type: "PublicStudio", id: slug }],
    }),
    checkSlug: b.query({ query: (slug) => ({ url: "studios/slug-check", params: { slug } }) }),
    createStudio: b.mutation({
      query: (body) => ({ url: "studios", method: "POST", body }),
      invalidatesTags: ["Me", "PublicStudio", "Tenants"],
    }),
    getStudioSettings: b.query({
      query: (slug) => `studios/${slug}/settings`,
      providesTags: (r, e, slug) => [{ type: "Studio", id: slug }],
    }),
    updateBranding: b.mutation({
      query: ({ slug, ...body }) => ({ url: `studios/${slug}/branding`, method: "PATCH", body }),
      invalidatesTags: (r, e, { slug }) => [{ type: "Studio", id: slug }, "PublicStudio", "Me"],
    }),
    uploadLogo: b.mutation({
      query: ({ slug, file }) => {
        const body = new FormData();
        body.append("file", file);
        return { url: `studios/${slug}/logo`, method: "POST", body };
      },
      invalidatesTags: (r, e, { slug }) => [{ type: "Studio", id: slug }, "PublicStudio"],
    }),
    getWorkspace: b.query({
      query: (slug) => `studios/${slug}/workspace`,
      providesTags: (r, e, slug) => [{ type: "Workspace", id: slug }],
    }),
    getMyInvitations: b.query({ query: () => "me/invitations", providesTags: ["Invitations"] }),
    acceptInvitation: b.mutation({
      query: (id) => ({ url: `me/invitations/${id}/accept`, method: "POST" }),
      invalidatesTags: ["Invitations", "Me", "PublicStudio", "Team", "Workspace"],
    }),
    declineInvitation: b.mutation({
      query: (id) => ({ url: `me/invitations/${id}/decline`, method: "POST" }),
      invalidatesTags: ["Invitations", "Me"],
    }),
  }),
});

export const {
  useGetPublicStudiosQuery,
  useGetPublicStudioQuery,
  useLazyCheckSlugQuery,
  useCreateStudioMutation,
  useGetStudioSettingsQuery,
  useUpdateBrandingMutation,
  useUploadLogoMutation,
  useGetWorkspaceQuery,
  useGetMyInvitationsQuery,
  useAcceptInvitationMutation,
  useDeclineInvitationMutation,
} = tenantApi;
