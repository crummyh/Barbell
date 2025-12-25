import { apiClient } from '../client';
import type {
	LabelCategoryCreate,
	LabelCategoryPublic,
	LabelCategoryUpdate,
	LabelSuperCategoryCreate,
	LabelSuperCategoryPublic,
	LabelSuperCategoryUpdate
} from '../types/labelCategory';

export const categoriesService = {
	async createLabelSuperCategory(
		category: LabelSuperCategoryCreate
	): Promise<LabelSuperCategoryPublic> {
		return apiClient.post<LabelSuperCategoryPublic>('/categories/super', { category });
	},

	async getLabelSuperCategories(): Promise<LabelSuperCategoryPublic[]> {
		return apiClient.get<LabelSuperCategoryPublic[]>('/categories/super');
	},

	async modifyLabelSuperCategory(
		id: number,
		update: LabelSuperCategoryUpdate
	): Promise<LabelSuperCategoryPublic> {
		return apiClient.put<LabelSuperCategoryPublic>('categories/super', { id, update });
	},

	async removeLabelSuperCategory(id: number): Promise<unknown> {
		return apiClient.delete<unknown>('categories/super', { params: { id: id } });
	},

	async createLabelCategory(category: LabelCategoryCreate): Promise<LabelCategoryPublic> {
		return apiClient.post<LabelCategoryPublic>('/categories', { category });
	},

	async modifyLabelCategory(id: number, update: LabelCategoryUpdate): Promise<LabelCategoryPublic> {
		return apiClient.put<LabelCategoryPublic>('categories', { id, update });
	},

	async removeLabelCategory(id: number): Promise<unknown> {
		return apiClient.delete<unknown>('categories', { params: { id: id } });
	}
};
