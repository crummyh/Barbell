export interface DocMetadata {
	title?: string;
	description?: string;
	icon?: string;
}

interface DocInfo {
	path: string; // URL path like "/docs/intro/quickstart"
	filePath: string; // File path like "/content/docs/01-intro/02-quickstart.md"
	section: string; // Like "intro"
	slug: string; // Like "quickstart"
	order: number; // The numeric prefix (01, 02, etc.)
	metadata: DocMetadata;
}

export function getAllDocs(): DocInfo[] {
	// Eager import gets the actual modules immediately
	const allDocs = import.meta.glob<{ metadata?: DocMetadata }>('$content/docs/**/*.md', {
		eager: true
	});

	const docs: DocInfo[] = [];

	for (const filePath in allDocs) {
		const doc = allDocs[filePath];

		// Parse the file path
		// "/content/docs/01-intro/02-quickstart.md"
		const pathParts = filePath.replace('/src/content/docs/', '').replace('.md', '').split('/');

		// Skip if it's not a valid doc file
		if (pathParts.length < 2) continue;

		// Extract section (e.g., "01-intro")
		const sectionWithPrefix = pathParts[0];
		const fileWithPrefix = pathParts[pathParts.length - 1];

		// Get the numeric order
		const orderMatch = fileWithPrefix.match(/^(\d+)-/);
		const order = orderMatch ? parseInt(orderMatch[1]) : 999;

		// Remove numeric prefixes for clean URLs
		const section = sectionWithPrefix.replace(/^\d+-/, '');
		const slug = fileWithPrefix.replace(/^\d+-/, '');

		// Build the URL path
		const urlPath = `/docs/${pathParts.map((p) => p.replace(/^\d+-/, '')).join('/')}`;

		docs.push({
			path: urlPath,
			filePath: filePath,
			section: section,
			slug: slug,
			order: order,
			metadata: doc.metadata || {}
		});
	}

	// Sort by order number
	return docs.sort((a, b) => {
		// First sort by section
		const sectionA = a.filePath.split('/')[3]; // Get "01-intro" part
		const sectionB = b.filePath.split('/')[3];
		if (sectionA !== sectionB) {
			return sectionA.localeCompare(sectionB);
		}
		// Then by page order within section
		return a.order - b.order;
	});
}

// Helper to organize docs by section
export function getDocsBySection() {
	const allDocs = getAllDocs();
	const sections = new Map<string, DocInfo[]>();

	for (const doc of allDocs) {
		if (!sections.has(doc.section)) {
			sections.set(doc.section, []);
		}
		sections.get(doc.section)!.push(doc);
	}

	return sections;
}
