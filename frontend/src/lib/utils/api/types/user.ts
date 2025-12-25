import type { DownloadBatch } from './downloadBatch';
import type { Team } from './team';
import type { UploadBatch } from './uploadBatch';

export enum UserRole {
	DEFAULT = 0,
	TEAM_LEADER = 1,
	MODERATOR = 2,
	ADMIN = 3
}

interface UserBase {
	username: string;
	email: string;
}

export interface User extends UserBase {
	id: number;
	created_at: Date | null;
	disabled: boolean | null;
	api_key: string | null;
	password: string;
	role: UserRole | null;
	code: string | null;
	led_team: Team | null;
	upload_batches: UploadBatch[];
	download_batches: DownloadBatch[];
}

export interface UserCreate extends UserBase {
	password: string;
}

export interface UserUpdate {
	username: string | undefined;
	email: string | undefined;
	password: string | undefined;
	disabled: boolean | undefined;
	team: number | undefined;
	role: UserRole | undefined;
	code: string | undefined;
}

export interface UserPublic extends UserBase {
	id: number;
	created_at: Date;
	disabled: boolean;
	role: UserRole;
	team: number | null;
}
