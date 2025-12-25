import type { UserRole } from './user';

export interface StatsOut {
	image_count: number;
	un_reviewed_image_count: number;
	team_count: number;
}

export interface TeamStatsOut {
	image_count: number;
	un_reviewed_image_count: number;
	years_available: string[number];
	upload_batches: number;
}

export interface RateLimitUpdate {
	route: string;
	requests_limit: number;
	time_window: number;
}

export interface Token {
	access_token: string;
	token_type: string;
}

export interface TokenData {
	username: string | null;
	role: UserRole | null;
}

export interface Ping {
	ping: string;
}
