import { error } from '@sveltejs/kit';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params }) => {
	let { slug } = params;

	let sections: string[] = slug ? slug.split('/') : [];

	if (sections.length === 0) {
		slug = 'index';
		sections = ['index'];
	}

	const allDocs = import.meta.glob('$content/docs/**/*.md');

	let matchedPath: string | null = null;
	let contents = {};

	for (const path in allDocs) {
		// Extract the parts after /content/docs/
		// Example: "/content/docs/01-intro/02-quickstart.md" -> ["01-intro", "02-quickstart.md"]
		const pathParts = path.replace('/src/content/docs/', '').split('/');

		// Remove numeric prefixes and .md extension for comparison
		const cleanPathParts = pathParts.map((part) => part.replace(/^\d+-/, '').replace(/\.md$/, ''));

		// Check if this path matches our slug segments
		if (
			sections.length === cleanPathParts.length &&
			sections.every((seg, i) => seg === cleanPathParts[i])
		) {
			matchedPath = path;
			break;
		}
	}

	if (!matchedPath) {
		throw error(404, `Documentation page not found: ${slug}`);
	}

	try {
		const doc = await allDocs[matchedPath]();

		return {
			component: doc.default,
			metadata: doc.metadata || {}
		};
	} catch (e) {
		throw error(500, `Failed to load documentation: ${e.message}`);
	}
};
