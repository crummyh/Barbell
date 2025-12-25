import { apiClient } from '../client';
import type { ImagePublic } from '../types/image';

export const imagesService = {
	async get_image_for_review(): Promise<ImagePublic> {
		return apiClient.get<ImagePublic>('/images');
	},

	async updateImage(): Promise<ImagePublic | null> {
		return apiClient.get<ImagePublic | null>('/images');
	},

	async getLabels(): Promise<LabelSuperCategoryPublic[]> {
		return apiClient.get<LabelSuperCategoryPublic[]>('/stats/labels');
	}
};
