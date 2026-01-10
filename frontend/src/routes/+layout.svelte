<script lang="ts">
	import './layout.css';
	import favicon from '$lib/assets/favicon.svg';
	import TopNav from '$lib/components/TopNav.svelte';
	import type { Snippet } from 'svelte';

	interface Props {
		children: Snippet<[]>;
		data: {
			authed: boolean;
		};
	}

	let { children, data }: Props = $props();
	let authed = $derived(data.authed);
</script>

<svelte:head>
	<meta charset="UTF-8" />
	<meta name="viewport" content="width=device-width, initial-scale=1.0" />
	<!-- <link rel="stylesheet" href="./style.css" /> -->
	<link rel="icon" href={favicon} type="image/x-icon" />
</svelte:head>

<div class="bg-white dark:bg-gray-800">
	<TopNav {authed}></TopNav>
	{@render children()}
</div>
