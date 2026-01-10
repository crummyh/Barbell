import { api } from '$lib/utils/api/index';
import { fail } from '@sveltejs/kit';

export const actions = {
	default: async ({ cookies, request }) => {
		const data = await request.formData();

    const username = data.get('username');
    const password = data.get('password')

		if (username === null || password === null) {
      return fail(422, { error: 'Username and Password are required' });
		}

		try {
      api.auth.login(username.toString(), password.toString());
		} catch (error) {
      return fail(422, { error: 'Username and Password are required' });
		}
	}
};
