import { error } from '@sveltejs/kit';

export const prerender = true;

const allDocs = import.meta.glob('$content/docs/**/*.md', { eager: true, import: 'metadata' });

export async function load({ params }) {
	let { slug } = params;

	let sections: string[] = slug ? slug.split('/') : [];

	if (sections.length === 0) {
		slug = 'index';
		sections = ['index'];
	}

	let matchedPath: string | null = null;

	for (const path in allDocs) {
		// Extract the parts after /content/docs/
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

	const splitPath = matchedPath.split('/');

	return {
		path: matchedPath,
		metadata: allDocs[matchedPath],
		section: splitPath[splitPath.length - 2].replace(/^\d+-/, '')
	};
}
