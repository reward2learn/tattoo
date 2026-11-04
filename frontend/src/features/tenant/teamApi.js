import { api } from "@/app/api";

export const teamApi = api.injectEndpoints({
  endpoints: (b) => ({
    getTeam: b.query({ query: (slug) => `studios/${slug}/team`, providesTags: (r, e, slug) => [{ type: "Team", id: slug }] }),
    inviteArtist: b.mutation({
      query: ({ slug, email }) => ({ url: `studios/${slug}/invitations`, method: "POST", body: { email } }),
      invalidatesTags: (r, e, { slug }) => [{ type: "Team", id: slug }, "Invitations"],
    }),
    revokeInvitation: b.mutation({
      query: ({ slug, id }) => ({ url: `studios/${slug}/invitations/${id}`, method: "DELETE" }),
      invalidatesTags: (r, e, { slug }) => [{ type: "Team", id: slug }, "Invitations"],
    }),
    removeMember: b.mutation({
      query: ({ slug, id }) => ({ url: `studios/${slug}/members/${id}`, method: "DELETE" }),
      invalidatesTags: (r, e, { slug }) => [{ type: "Team", id: slug }, "PublicStudio", "Me"],
    }),
    getPlatformTenants: b.query({ query: () => "platform/tenants", providesTags: ["Tenants"] }),
  }),
});

export const {
  useGetTeamQuery,
  useInviteArtistMutation,
  useRevokeInvitationMutation,
  useRemoveMemberMutation,
  useGetPlatformTenantsQuery,
} = teamApi;
