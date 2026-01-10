import { apiClient } from '../client';
import type { UserPublic } from '../types/user';

export const authService = {
	async login(username: string, password: string): Promise<{ message: 'Login successful' }> {
		return apiClient.request<{ message: 'Login successful' }>('/auth/v1/token', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/x-www-form-urlencoded'
			},
			body: new URLSearchParams({
				username,
				password
			}),
			credentials: 'include'
		});
	},

	async readUsersMe(): Promise<UserPublic> {
		return apiClient.get<UserPublic>('users/me');
	}
};
