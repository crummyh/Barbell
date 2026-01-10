<script lang="ts">
	let { sections }: { sections: string[] } = $props();
</script>

<div class="flex">
	{#each sections as section (section)}
		<div class="text-gray-800 dark:text-gray-200">{section}</div>
		{#if !(section === sections[sections.length - 1])}
			<span class="mx-2 text-gray-700 dark:text-gray-300">/</span>
		{/if}
	{/each}
</div>
