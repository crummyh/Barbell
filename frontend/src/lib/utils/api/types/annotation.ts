import type { Image } from './image';

interface AnnotationBase {
	category_id: number;
	iscrowd: boolean;
	area: number | null;
	bbox_x: number | null;
	bbox_y: number | null;
	bbox_w: number | null;
	bbox_h: number | null;
}

export interface Annotation extends AnnotationBase {
	id: number;
	image_id: string;
	image: Image;
}

export type AnnotationCreate = AnnotationBase;

export interface AnnotationUpdate {
	category_id: number | undefined;
	iscrowd: boolean | undefined;
	area: number | undefined;
	bbox_x: number | undefined;
	bbox_y: number | undefined;
	bbox_w: number | undefined;
	bbox_h: number | undefined;
	image_id: string | undefined;
}

export interface AnnotationPublic extends AnnotationBase {
	id: number;
	image_id: string;
}
