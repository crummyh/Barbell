<script lang="ts">
	let { children } = $props();

	let activeTab = $state(0);

	let tabs = $derived(children?.() || []);

	function selectTab(index: number) {
		activeTab = index;
	}
</script>

<div>
	<div>
		{#each tabs as tab, index (index)}
			<button class:active={activeTab === index} onclick={() => selectTab(index)}>
				{tab.label}
			</button>
		{/each}
	</div>

	<div>
		{#if tabs[activeTab]}
			{@render tabs[activeTab].content()}
		{/if}
	</div>
</div>
