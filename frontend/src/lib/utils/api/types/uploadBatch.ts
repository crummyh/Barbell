import type { User } from './user';

export enum UploadStatus {
	UPLOADING = 'uploading',
	PROCESSING = 'processing',
	COMPLETED = 'completed',
	FAILED = 'failed'
}

interface BaseUploadBatch {
	status: UploadStatus;
	file_size: number | null;
	images_valid: number;
	images_rejected: number;
	images_total: number;
	capture_time: Date;
	start_time: Date | null;
	error_message: string | null;
}

export interface UploadBatch extends BaseUploadBatch {
	id: string;
	user_id: number;
	user: User;
}

export interface UploadBatchCreate {
	capture_time: Date;
	file_size: number;
	user_id: number;
}

export interface UploadBatchUpdate {
	status: UploadStatus | undefined;
	file_size: number | undefined;
	images_valid: number | undefined;
	images_rejected: number | undefined;
	images_total: number | undefined;
	capture_time: Date | undefined;
	start_time: Date | undefined;
	error_message: string | undefined;
	user_id: number | undefined;
}

export interface UploadBatchPublic extends BaseUploadBatch {
	id: string;
	username: string;
	estimated_time_left: number | null;
}
