<script lang="ts">
	import type { Snippet } from 'svelte';
	import CopyButton from '../CopyButton.svelte';
	import { getLangIcon } from '$lib/utils/docs';

	let { tabs }: { tabs: { label: string; content: Snippet; lang?: string }[] } = $props();

	let activeTab = $state(0);
	let activeContent: HTMLElement | null = $state(null);

	function selectTab(index: number) {
		activeTab = index;
	}
</script>

<div class="not-prose mb-6 rounded-md bg-[#24292e]">
	<div class="flex py-3">
		<div class="mx-2 rounded-full bg-gray-800 p-0.5">
			{#each tabs as tab, index (index)}
				<button
					class="rounded-full px-3 py-2 text-gray-50 transition-all duration-200 not-last:me-3 {activeTab ===
					index
						? 'bg-primary-500'
						: ''}"
					onclick={() => selectTab(index)}
				>
					{#if tab.lang}
						<span class={getLangIcon(tab.lang)}></span>
					{/if}
					{tab.label}
				</button>
			{/each}
		</div>
		<div class="ms-auto me-3 text-xl text-gray-50">
			<CopyButton text={activeContent?.textContent}></CopyButton>
		</div>
	</div>

	<div class="overflow-auto px-4 py-3" bind:this={activeContent}>
		{#if tabs[activeTab]}
			{@render tabs[activeTab].content()}
		{/if}
	</div>
</div>
