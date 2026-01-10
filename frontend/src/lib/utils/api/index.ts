import { adminService } from './services/admin';
import { authService } from './services/auth';
import { categoriesService } from './services/categories';
import { imagesService } from './services/images';

export { apiClient, APIError } from './client';
export * from './types/annotation';
export * from './types/downloadBatch';
export * from './types/image';
export * from './types/labelCategory';
export * from './types/team';
export * from './types/types';
export * from './types/uploadBatch';
export * from './types/user';

export const api = {
	admin: adminService,
	auth: authService,
	categories: categoriesService,
	images: imagesService
};
