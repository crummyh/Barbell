import type { User } from './user';

export enum DownloadStatus {
	STARTING = 'starting',
	ASSEMBLING_LABELS = 'assembling_labels',
	ASSEMBLING_IMAGES = 'assembling_images',
	ADDING_MANIFEST = 'adding_manifest',
	READY = 'ready',
	FAILED = 'failed'
}

export interface AnnotationSelection {
	id: number;
	super: boolean;
}

export interface BaseDownloadBatch {
	status: DownloadStatus;
	non_match_images: boolean;
	image_count: number;
	annotations: AnnotationSelection[];
	start_time: Date;
	hash: string | null;
	error_message: string | null;
}

export interface DownloadBatch extends BaseDownloadBatch {
	id: string;
	user_id: number;
	user: null;
}

export interface DownloadBatchCreate {
	annotations: AnnotationSelection[];
	count: number;
	non_match_images: boolean;
}

export interface DownloadBatchUpdate {
	status: DownloadStatus | undefined;
	non_match_images: boolean | undefined;
	image_count: number | undefined;
	annotations: AnnotationSelection[] | undefined;
	start_time: Date | undefined;
	hash: string | undefined;
	error_message: string | undefined;
	user: User | undefined;
}

export interface DownloadBatchPublic extends BaseDownloadBatch {
	id: string;
	estimated_time_left: number;
}
