<script lang="ts">
	import Sidebar from '$lib/components/docs/Sidebar.svelte';
	import type { PageData } from './$types';

	export let data: PageData;

	const { component: DocComponent, metadata } = data;
</script>

<svelte:head>
	<title>{metadata.title || 'Barbell Documentation'}</title>
</svelte:head>

<div class="flex min-h-full w-full">
	<Sidebar />
	<div class="prose dark:prose-invert">
		<svelte:component this={DocComponent} />
	</div>
</div>
