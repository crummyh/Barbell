import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ cookies }) => {
	if (cookies.get('access_token')) {
		return { authed: true };
	} else {
		return { authed: false };
	}
};
