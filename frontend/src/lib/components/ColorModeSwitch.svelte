<script lang="ts">
	import { onMount } from 'svelte';

	let theme = $state('default');

	onMount(() => {
		updateTheme();
	});

	function toggleTheme() {
		if (document.documentElement.classList.contains('dark')) {
			localStorage.theme = 'light';
			theme = 'light';
		} else {
			localStorage.theme = 'dark';
			theme = 'dark';
		}
		updateTheme();
	}

	function updateTheme() {
		document.documentElement.classList.toggle(
			'dark',
			localStorage.theme === 'dark' ||
				(!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)
		);
		if (document.documentElement.classList.contains('dark')) {
			theme = 'dark';
		} else {
			theme = 'light';
		}
	}
</script>

<button class="px-2 text-xl" onclick={toggleTheme}>
	{#if theme === 'dark'}
		<span class="icon-[material-symbols--light-mode]"></span>
	{:else}
		<span class="icon-[material-symbols--dark-mode]"></span>
	{/if}
</button>
