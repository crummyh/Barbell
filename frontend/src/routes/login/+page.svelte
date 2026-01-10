<script lang="ts">
</script>

<div class="h-full min-w-full">
	<div class="mx-8 my-8 w-full rounded-lg bg-gray-100 p-5 lg:mx-auto lg:w-lg dark:bg-gray-900">
		<span
			class="mx-auto mb-2 icon-[material-symbols--account-circle] block text-8xl text-gray-700 dark:text-gray-300"
		></span>
		<h1 class="mx-auto mb-4 text-center text-4xl font-semibold">Login</h1>
		<form method="POST" action="">
			<label class="" for="username">Username or Email</label>
			<input class="mb-3 w-full rounded border px-3 py-2" type="text" id="username" />
			<label class="" for="">Password</label>
			<input class="mb-3 w-full rounded border px-3 py-2" type="password" />
			<input
				class="mx-auto mt-3 block w-full rounded-md bg-primary-500 px-4 py-2 text-gray-50"
				type="submit"
				value="Login"
			/>
		</form>
	</div>
</div>
