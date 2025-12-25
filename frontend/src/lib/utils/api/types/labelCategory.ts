interface LabelCategoryBase {
	name: string;
}

export interface LabelSuperCategory extends LabelCategoryBase {
	id: number;
	sub_categories: LabelCategory[];
}

export interface LabelCategory extends LabelCategoryBase {
	id: number;
	super_category_id: number | null;
	super_category: LabelSuperCategory | null;
}

export interface LabelCategoryCreate extends LabelCategoryBase {
	super_category_id: number | null;
}

export type LabelSuperCategoryCreate = LabelCategoryBase;

export interface LabelCategoryUpdate {
	name: string | undefined;
	super_category_id: number | undefined;
}

export interface LabelSuperCategoryUpdate extends LabelCategoryUpdate {
	name: string | undefined;
}

export interface LabelCategoryPublic extends LabelCategoryBase {
	id: number;
	super_category_id: number | null;
}

export interface LabelSuperCategoryPublic extends LabelCategoryBase {
	id: number;
	sub_categories: LabelCategoryPublic[];
}
