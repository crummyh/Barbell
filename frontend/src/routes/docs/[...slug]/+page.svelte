<script lang="ts">
	import Sidebar from '$lib/components/docs/Sidebar.svelte';
	import { type Component } from 'svelte';
	import type { PageData } from './$types';
	import type { DocMetadata } from '$lib/utils/docs';

	let { data }: { data: PageData } = $props();

	let metadata = $derived(data.metadata as DocMetadata);

	let DocsComponent: Component | null = $state(null);

	$effect(() => {
		const path = data.path;
		DocsComponent = null;

		const modules = import.meta.glob('$content/docs/**/*.md');

		if (modules[path]) {
			modules[path]().then((module: any) => {
				DocsComponent = module.default;
			});
		}
	});
</script>

<svelte:head>
	<title>{metadata?.title || 'Barbell Documentation'}</title>
</svelte:head>

<div class="flex min-h-full w-full">
	<Sidebar />
	<div class="prose dark:prose-invert">
		{#if DocsComponent}
			<DocsComponent></DocsComponent>
		{/if}
	</div>
</div>
