<script lang="ts">
	import { resolve } from '$app/paths';
	import ColorModeSwitch from './ColorModeSwitch.svelte';

	let toggled = $state(false);

	interface Props {
		authed: boolean;
	}

	let { authed }: Props = $props();
	$inspect(authed);

	function toggleMobileNav() {
		toggled = !toggled;
	}
</script>

<nav class="sticky top-0 z-30 w-full bg-primary-500 text-white">
	<div class="mx-auto flex max-w-7xl items-center justify-between p-4">
		<a href="/" class="flex items-center">
			<span class="text-xl font-semibold">[Barbell]</span>
		</a>
		<button
			onclick={toggleMobileNav}
			type="button"
			class="hover:bg-primary-400-600 inline-flex h-10 w-10 rounded-b-sm text-2xl md:hidden dark:hover:bg-primary-600"
			aria-controls="navbar-default"
			aria-expanded={toggled}
		>
			<span class="sr-only">Open navigation menu</span>
			<span class="icon-[material-symbols--menu]"></span>
		</button>
		<div class="hidden w-full md:block md:w-auto" id="navbar-default">
			<ul class="flex">
				<li><a href={resolve('/docs')} class="text-heading px-2">Docs</a></li>
				<li><a href={resolve('/about')} class="text-heading px-2">About</a></li>
				<li><ColorModeSwitch /></li>
				{#if authed}
					<li>
						<button class="text-heading" aria-label="account"
							><span class="icon-[material-symbols--account-circle]"></span></button
						>
					</li>
				{:else}
					<li>
						<a
							href={resolve('/login')}
							class="text-heading mx-2 rounded-md bg-white p-2 text-gray-950">Log in</a
						>
					</li>
					<li>
						<a
							href={resolve('/register')}
							class="text-heading mx-2 rounded-md bg-white p-2 text-gray-950">Sign Up</a
						>
					</li>
				{/if}
			</ul>
		</div>
	</div>
</nav>
