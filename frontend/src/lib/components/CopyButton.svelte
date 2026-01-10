<script lang="ts">
	let { text }: { text: string } = $props();

	let icon = $state('icon-[material-symbols--content-copy]');

	async function writeClipboardText() {
		await navigator.clipboard.writeText(text);
		icon = 'icon-[material-symbols--library-add-check]';
		setTimeout(() => {
			icon = 'icon-[material-symbols--content-copy]';
		}, 2000);
	}
</script>

<button onclick={writeClipboardText} aria-label="Copy content">
	<span class={icon}></span>
</button>
