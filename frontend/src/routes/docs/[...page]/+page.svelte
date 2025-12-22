<script lang="ts">
	import type { PageData } from './$types';

	export let data: PageData;

	const { component: DocComponent, metadata } = data;
</script>

<svelte:head>
	<title>{metadata.title || 'Barbell Documentation'}</title>
</svelte:head>

<div class="docs-container">
	{#if DocComponent}
		<svelte:component this={DocComponent} />
	{:else}
		<h1>Welcome to Documentation</h1>
	{/if}
</div>
