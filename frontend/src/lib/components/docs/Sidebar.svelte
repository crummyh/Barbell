<script lang="ts">
	import { page } from '$app/state';
	import { getDocsBySection } from '$lib/utils/docs';
	import { resolve } from '$app/paths';

	const docsBySection = getDocsBySection();
	const currentPath = $state(page.url.pathname);
</script>

<nav class="sticky top-20 me-4">
	<!-- eslint-disable-next-line svelte/require-each-key -->
	{#each [...docsBySection] as [sectionName, docs]}
		<div class="mb-3">
			<h3 class="text-lg">{sectionName}</h3>
			<ul>
				{#each docs as doc (doc)}
					<li class="mb-1">
						<a
							href={resolve(doc.path)}
							class:active={currentPath === doc.path}
							class="text-gray-700"
						>
							{doc.metadata.title || doc.slug}
						</a>
					</li>
				{/each}
			</ul>
		</div>
	{/each}
</nav>
