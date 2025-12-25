<script lang="ts">
	import { page } from '$app/state';
	import { getDocsBySection } from '$lib/utils/docs';
	import { resolve } from '$app/paths';

	const docsBySection = getDocsBySection();
	const currentPath = $state(page.url.pathname);
</script>

<nav class="sidebar">
	<!-- eslint-disable-next-line svelte/require-each-key -->
	{#each [...docsBySection] as [sectionName, docs]}
		<div class="section">
			<h3>{sectionName}</h3>
			<ul>
				{#each docs as doc (doc)}
					<li>
						<a href={resolve(doc.path)} class:active={currentPath === doc.path}>
							{doc.metadata.title || doc.slug}
						</a>
					</li>
				{/each}
			</ul>
		</div>
	{/each}
</nav>
