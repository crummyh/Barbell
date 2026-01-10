import { api } from '$lib/utils/api/index.js';
import { redirect } from '@sveltejs/kit';

export function load({ cookies, url }) {
	if (!cookies.get('access_token')) {
		redirect(303, `/login?redirectTo=${url.pathname}`);
	} else {
		try {
			api.auth.readUsersMe();
		} catch {
			redirect(303, `/login?redirectTo=${url.pathname}`);
		}
	}
}
