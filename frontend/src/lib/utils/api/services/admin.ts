import { apiClient } from '../client';
import type { RateLimitUpdate } from '../types/types';

export const adminService = {
	async updateRateLimitingConfig(cfg: RateLimitUpdate): Promise<unknown> {
		return apiClient.post<unknown>('/admin/rate-limiting', cfg);
	},

	async updateImage(): Promise<unknown> {
		return apiClient.get<unknown>('/admin/rate-limiting');
	}
};
