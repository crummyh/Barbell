import type { User } from './user';

interface TeamBase {
	team_number: number;
	team_name: string;
}

export interface Team extends TeamBase {
	id: number;
	created_at: Date;
	disabled: boolean;
	leader_user: number | null;
	leader: User | null;
}

export interface TeamCreate {
	team_number: number;
	team_name: string;
	leader_username: string;
}

export interface TeamUpdate {
	team_number: number | undefined;
	team_name: string | undefined;
	leader_username: string | undefined;
}

export interface TeamPublic extends TeamBase {
	id: number;
	created_at: Date;
	disabled: boolean;
}
