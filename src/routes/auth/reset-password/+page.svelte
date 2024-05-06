<script>
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { userResetPassword } from '$lib/apis/auths';
	import { WEBUI_BASE_URL } from '$lib/constants';
	import { getContext, onMount } from 'svelte';
	import { toast } from 'svelte-sonner';

	const i18n = getContext('i18n');

	let password = '';

	$: token = $page.url.searchParams.get('token');

	const submitHandler = async (/** @type {string} */ token) => {
		const res = await userResetPassword(password, token).catch((error) => {
			toast.error(error);
			return null;
		});

    if (!res) return;

    goto('/auth');
	};

	onMount(() => {
		console.log('what', JSON.stringify($page), $page.url.searchParams.get('token'));
	});
</script>

<div class="fixed m-10 z-50">
	<div class="flex space-x-2">
		<div class=" self-center">
			<img src="{WEBUI_BASE_URL}/static/favicon.png" class=" w-8 rounded-full" alt="logo" />
		</div>
	</div>
</div>

<div class=" bg-white dark:bg-gray-900 min-h-screen w-full flex justify-center font-mona">
	<div class="w-full sm:max-w-lg px-4 min-h-screen flex flex-col">
		{#if !token}
			<p>{$i18n.t('Error: Password reset link is invalid or has expired.')}</p>
		{:else}
			<div class=" my-auto pb-10 w-full">
				<form
					class=" flex flex-col justify-center bg-white py-6 sm:py-16 px-6 sm:px-16 rounded-2xl"
					on:submit|preventDefault={() => {
						submitHandler(token);
					}}
				>
					<div class=" text-xl sm:text-2xl font-bold">
						{$i18n.t('Reset Password')}
					</div>
					<div>
						<label for="password" class=" text-sm font-semibold text-left mb-1"
							>{$i18n.t('New Password')}</label
						>
						<input
							id="password"
							bind:value={password}
							type="password"
							class=" border px-4 py-2.5 rounded-2xl w-full text-sm"
							placeholder={$i18n.t('Enter Your Password')}
							autocomplete="new-password"
							required
						/>
					</div>

					<div class="mt-5">
						<button
							class=" bg-gray-900 hover:bg-gray-800 w-full rounded-full text-white font-semibold text-sm py-3 transition"
							type="submit"
						>
							{$i18n.t('Reset Password')}
						</button>
					</div>
				</form>
			</div>
		{/if}
	</div>
</div>
