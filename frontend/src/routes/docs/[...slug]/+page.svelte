<script lang="ts">
	import Sidebar from '$lib/components/docs/Sidebar.svelte';
	import { type Component } from 'svelte';
	import type { PageData } from './$types';
	import type { DocMetadata } from '$lib/utils/docs';
	import Breadcrumbs from '$lib/components/Breadcrumbs.svelte';

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
	<title>{metadata?.title + ' - Barbell Documentation'}</title>
</svelte:head>

<div class="min-h-full w-full justify-center">
	<div class="mx-auto flex w-full lg:w-5xl">
		<Sidebar />
		<div>
			<Breadcrumbs sections={[data.section, metadata.title]}></Breadcrumbs>
			<h1 class="text-5xl font-semibold">{metadata.title}</h1>
			<h3>{metadata.description}</h3>
			<div class="prose dark:prose-invert prose-code:before:hidden prose-code:after:hidden">
				{#if DocsComponent}
					<DocsComponent></DocsComponent>
				{/if}
			</div>
		</div>
	</div>
</div>
