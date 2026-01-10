import { PUBLIC_API_BASE_URL } from '$env/static/public';

export class APIError extends Error {
	constructor(
		public status: number,
		public statusText: string,
		public data: unknown
	) {
		super(`API Error: ${status} ${statusText}`);
		this.name = 'APIError';
	}
}

interface RequestOptions extends RequestInit {
	params?: Record<string, string | number | boolean>;
}

class APIClient {
	private baseURL: string;

	constructor(baseURL: string) {
		this.baseURL = baseURL;
	}

	async request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
		const { params, ...fetchOptions } = options;

		// Build URL with query parameters
		let url = `${this.baseURL}${endpoint}`;
		if (params) {
			const searchParams = new URLSearchParams(
				Object.entries(params).map(([k, v]) => [k, String(v)])
			);
			url += `?${searchParams}`;
		}

		// Set default headers
		const headers = new Headers(fetchOptions.headers);
		if (!headers.has('Content-Type') && fetchOptions.body) {
			headers.set('Content-Type', 'application/json');
		}

		// Include credentials to send HTTPOnly cookies
		const response = await fetch(url, {
			...fetchOptions,
			headers,
			credentials: 'include'
		});

		if (!response.ok) {
			const errorData = await response.json().catch(() => ({}));
			throw new APIError(response.status, response.statusText, errorData);
		}

		// Handle empty responses
		const contentType = response.headers.get('content-type');
		if (contentType?.includes('application/json')) {
			return response.json();
		}
		return response.text() as T;
	}

	async get<T>(endpoint: string, options?: RequestOptions): Promise<T> {
		return this.request<T>(endpoint, { ...options, method: 'GET' });
	}

	async post<T>(endpoint: string, data?: unknown, options?: RequestOptions): Promise<T> {
		return this.request<T>(endpoint, {
			...options,
			method: 'POST',
			body: data ? JSON.stringify(data) : undefined
		});
	}

	async put<T>(endpoint: string, data?: unknown, options?: RequestOptions): Promise<T> {
		return this.request<T>(endpoint, {
			...options,
			method: 'PUT',
			body: data ? JSON.stringify(data) : undefined
		});
	}

	async patch<T>(endpoint: string, data?: unknown, options?: RequestOptions): Promise<T> {
		return this.request<T>(endpoint, {
			...options,
			method: 'PATCH',
			body: data ? JSON.stringify(data) : undefined
		});
	}

	async delete<T>(endpoint: string, options?: RequestOptions): Promise<T> {
		return this.request<T>(endpoint, { ...options, method: 'DELETE' });
	}

	async uploadPost<T>(endpoint: string, formData: FormData, options?: RequestOptions): Promise<T> {
		const { params, ...fetchOptions } = options || {};

		let url = `${this.baseURL}${endpoint}`;
		if (params) {
			const searchParams = new URLSearchParams(
				Object.entries(params).map(([k, v]) => [k, String(v)])
			);
			url += `?${searchParams}`;
		}

		// Don't set Content-Type - browser will set it with boundary for multipart/form-data
		const headers = new Headers(fetchOptions.headers);

		const response = await fetch(url, {
			...fetchOptions,
			method: 'POST',
			headers,
			body: formData,
			credentials: 'include'
		});

		if (!response.ok) {
			const errorData = await response.json().catch(() => ({}));
			throw new APIError(response.status, response.statusText, errorData);
		}

		const contentType = response.headers.get('content-type');
		if (contentType?.includes('application/json')) {
			return response.json();
		}
		return response.text() as any;
	}

	async downloadGet(
		endpoint: string,
		options?: RequestOptions
	): Promise<{ blob: Blob; filename: string | null }> {
		const { params, ...fetchOptions } = options || {};

		let url = `${this.baseURL}${endpoint}`;
		if (params) {
			const searchParams = new URLSearchParams(
				Object.entries(params).map(([k, v]) => [k, String(v)])
			);
			url += `?${searchParams}`;
		}

		const response = await fetch(url, {
			...fetchOptions,
			method: 'GET',
			credentials: 'include'
		});

		if (!response.ok) {
			const errorData = await response.json().catch(() => ({}));
			throw new APIError(response.status, response.statusText, errorData);
		}

		// Extract filename from Content-Disposition header
		const contentDisposition = response.headers.get('content-disposition');
		let filename: string | null = null;
		if (contentDisposition) {
			const filenameMatch = contentDisposition.match(/filename="?(.+)"?/i);
			if (filenameMatch) {
				filename = filenameMatch[1];
			}
		}

		const blob = await response.blob();
		return { blob, filename };
	}
}

export const apiClient = new APIClient(PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1');
