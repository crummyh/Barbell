import type { Annotation, AnnotationPublic } from './annotation';

enum ImageReviewStatus {
	APPROVED = 'approved',
	AWAITING_LABELS = 'awaiting_labels',
	NOT_REVIEWED = 'not_reviewed'
}

interface ImageBase {
	created_by: number;
	batch: string;
	review_status: ImageReviewStatus;
}

export interface Image extends ImageBase {
	id: string;
	created_at: Date | null;
	annotations: Annotation[];
}

export interface ImageCreate {
	batch: string;
}

export interface ImageUpdate {
	created_at: Date | unknown;
	created_by: number | unknown;
	batch: string | unknown;
	review_status: ImageReviewStatus | unknown;
	annotations: Annotation[] | unknown;
}

export interface ImagePublic extends ImageBase {
	id: string;
	created_at: Date;
	annotations: AnnotationPublic[];
}
