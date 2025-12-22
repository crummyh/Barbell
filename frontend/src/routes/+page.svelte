<script lang="ts">
	import { countUp } from '$lib/utils/transitions';
	import { onMount } from 'svelte';

	let visible = $state(false);
	let containerEl = $state();

	onMount(() => {
		const observer = new IntersectionObserver(
			(entries) => {
				if (entries[0].isIntersecting) {
					visible = true;
					observer.disconnect();
				}
			},
			{ threshold: 0.5 }
		);

		if (containerEl) {
			observer.observe(containerEl);
		}

		return () => observer.disconnect();
	});
</script>

<div class="min-h-screen bg-white dark:bg-gray-800">
	<section class="mx-auto max-w-7xl px-6 py-20 md:py-32">
		<div class="mx-auto max-w-4xl text-center">
			<h1 class="mb-6 text-5xl font-bold text-gray-900 md:text-6xl dark:text-gray-100">
				Build Better Vision Models,<br />
				<span class="text-primary-500 dark:text-primary-400">Together</span>
			</h1>
			<p class="mb-10 text-xl text-gray-600 md:text-2xl dark:text-gray-400">
				An open-source hub where FRC teams upload and share labeled match photos to build large,
				high-quality training datasets for object detection.
			</p>
			<div class="flex flex-col justify-center gap-4 sm:flex-row">
				<button
					class="flex items-center justify-center gap-2 rounded-lg bg-gray-500 px-8 py-4 text-lg font-semibold text-white transition-colors hover:bg-primary-600"
				>
					<span class="icon-[simple-icons--github]"></span>
					View on GitHub
				</button>
				<button
					class="flex items-center justify-center gap-2 rounded-lg bg-primary-500 px-8 py-4 text-lg font-semibold text-white transition-colors hover:bg-primary-600"
				>
					Get Started
					<span class="icon-[material-symbols--arrow-forward-rounded]"></span>
				</button>
			</div>
		</div>
	</section>

	<section class="bg-gray-200 px-6 py-16 dark:bg-gray-700">
		<div class="mx-auto grid max-w-6xl grid-cols-1 text-center md:grid-cols-3">
			<div bind:this={containerEl}>
				{#if visible}
					<div
						class="mb-2 min-w-36 text-5xl font-bold text-gray-900 tabular-nums dark:text-gray-100"
						in:countUp={{ duration: 5000, delay: 1000, goal: 99999 }}
					>
						99,999
					</div>
				{:else}
					<div
						class="mb-2 min-w-36 text-5xl font-bold text-gray-900 tabular-nums dark:text-gray-100"
					>
						99,999
					</div>
				{/if}
				<div class="text-lg text-gray-600 dark:text-gray-300">Labeled Images</div>
			</div>
			<div>
				{#if visible}
					<div
						class="mb-2 min-w-36 text-5xl font-bold text-gray-900 tabular-nums dark:text-gray-100"
						in:countUp={{ duration: 5000, delay: 1000, goal: 999 }}
					>
						999
					</div>
				{:else}
					<div
						class="mb-2 min-w-36 text-5xl font-bold text-gray-900 tabular-nums dark:text-gray-100"
					>
						999
					</div>
				{/if}
				<div class="text-lg text-gray-600 dark:text-gray-300">Contributing Teams</div>
			</div>
			<div>
				{#if visible}
					<div
						class="mb-2 min-w-36 text-5xl font-bold text-gray-900 tabular-nums dark:text-gray-100"
						in:countUp={{ duration: 5000, delay: 1000, goal: 100, suffix: '%' }}
					>
						100%
					</div>
				{:else}
					<div
						class="mb-2 min-w-36 text-5xl font-bold text-gray-900 tabular-nums dark:text-gray-100"
					>
						100%
					</div>
				{/if}
				<div class="text-lg text-gray-600 dark:text-gray-300">Open Source</div>
			</div>
		</div>
	</section>

	<section class="mx-auto max-w-6xl px-8 py-20">
		<h2 class="mb-6 text-center text-4xl font-bold text-gray-700 dark:text-gray-200">
			How Barbell Works
		</h2>
		<div class="grid grid-cols-1 gap-12 md:grid-cols-3">
			<div class="text-center">
				<div
					class="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-xl bg-primary-500 text-3xl"
				>
					<span class="icon-[material-symbols--cloud-upload] text-white"></span>
				</div>
				<h3 class="mb-4 text-2xl font-semibold text-gray-900 dark:text-gray-100">Upload</h3>
				<p class="text-gray-700 dark:text-gray-300">
					Teams upload match photos from competitions, scrimmages, and practices.
				</p>
			</div>
			<div class="text-center">
				<div
					class="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-xl bg-primary-500 text-3xl"
				>
					<span class="icon-[material-symbols--groups] text-white"></span>
				</div>
				<h3 class="mb-4 text-2xl font-semibold text-gray-900 dark:text-gray-100">Collaborate</h3>
				<p class="text-gray-700 dark:text-gray-300">
					The community reviews, improves, and validates labels to ensure dataset quality and
					consistency.
				</p>
			</div>
			<div class="text-center">
				<div
					class="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-xl bg-primary-500 text-3xl"
				>
					<span class="icon-[material-symbols--database] text-white"></span>
				</div>
				<h3 class="mb-4 text-2xl font-semibold text-gray-900 dark:text-gray-100">Train</h3>
				<p class="text-gray-700 dark:text-gray-300">
					Download curated datasets ready for training robust object detection models for your team.
				</p>
			</div>
		</div>
	</section>

	<section class="bg-gray-200 px-6 py-20 dark:bg-gray-700">
		<div class="mx-auto max-w-6xl">
			<div class="grid grid-cols-1 items-center gap-12 md:grid-cols-2">
				<div>
					<h2 class="mb-6 text-4xl font-bold text-gray-900 dark:text-gray-100">
						Stronger Models Through Community
					</h2>
					<p class="mb-6 text-lg leading-relaxed text-gray-700 dark:text-gray-300">
						Individual teams struggle with limited training data. Barbell solves this by pooling
						resources across the entire FRC community, creating datasets that are larger, more
						diverse, and higher quality than any single team could produce alone.
					</p>
					<ul class="space-y-4">
						<li class="flex">
							<div class="me-2 flex h-6 w-6 justify-center rounded-full bg-primary-500">
								<span class="my-auto icon-[material-symbols--check-rounded] text-white"></span>
							</div>
							<div class="text-gray-900 dark:text-gray-100">
								Diverse lighting conditions and field setups
							</div>
						</li>
						<li class="flex">
							<div class="me-2 flex h-6 w-6 justify-center rounded-full bg-primary-500">
								<span class="my-auto icon-[material-symbols--check-rounded] text-white"></span>
							</div>
							<div class="text-gray-900 dark:text-gray-100">
								Multiple camera angles and perspectives
							</div>
						</li>
						<li class="flex">
							<div class="me-2 flex h-6 w-6 justify-center rounded-full bg-primary-500">
								<span class="my-auto icon-[material-symbols--check-rounded] text-white"></span>
							</div>
							<div class="text-gray-900 dark:text-gray-100">
								Community-validated labeling standards
							</div>
						</li>
					</ul>
				</div>
				<div class="flex h-80 items-center justify-center rounded-2xl bg-primary-100">
					<div class="text-center text-primary-600">
						<p class="text-lg font-medium">Dataset Preview</p>
					</div>
				</div>
			</div>
		</div>
	</section>

	<section class="mx-auto max-w-4xl px-6 py-20 text-center">
		<h2 class="mb-6 text-4xl font-bold text-gray-900 dark:text-gray-100">Ready to Contribute?</h2>
		<p class="mb-10 text-xl text-gray-700 dark:text-gray-300">
			Join teams from around the word building the future of FRC vision.
		</p>
		<button
			class="mx-auto flex gap-2 rounded-lg bg-primary-500 px-10 py-5 text-xl font-semibold text-white transition-colors hover:bg-primary-600"
		>
			Start Uploading
			<span class="icon-[material-symbols--arrow-forward-rounded]"></span>
		</button>
	</section>
</div>
