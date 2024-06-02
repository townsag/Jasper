<svelte:head>
	<title>Jasper</title>
	<meta name="description" content="Svelte demo app" />
</svelte:head>

<script lang="ts">
    import type { ActionData } from "./$types";
    export let form: ActionData;

    import { env } from '$env/dynamic/public';
</script>

<div class="flex flex-row space-x-2 h-full">
    <section class="flex flex-col m-2 rounded-md p-4 bg-slate-800 w-1/2 justify-center">
        <h1 class="text-jax-yellow text-6xl mb-2">Welcome to Jasper</h1>
        <p class="text-slate-50">
            Jasper is an open source programming companion for developers working
            on projects in JAX. I was motivated to make this project because GPT-3.5
            is pretty bad at writing JAX and I want the benefits of writing code
            with an LLM companion but grounded in the truthfullness of the JAX 
            documentation. Jasper uses RAG to find chunks of text from the JAX
            documentation website that are semantically similar to the question
            asked in the chat. These chunks are then appended to the user question
            when it is sent to a chat api enpoint for completion.
        </p>
        <br />
        <p class="text-slate-50">JAX + expert ~= JAXpert ~= Jasper</p>
        <br />
        <p class="text-slate-50">You can find the implementation of Jasper 
            <a class="underline focus:text-yellow-300" href="https://github.com/townsag/Jasper" target="_blank" >here</a>
        </p>
    </section>
    <section class="w-1/2 flex items-center justify-center">
        <form method="POST" action="?/login" class="flex flex-col space-y-2 items-center w-max m-2 bg-slate-800 rounded-md p-8">
    
            <h3 class="text-sky-50 text-3xl">Build with Jasper</h3>
            <div class="flex flex-col min-w-64">
                <label for="username" class="text-slate-50">Username</label>
                <input name="username" type="username" id="username"
                        class="rounded-lg border border-solid border-slate-600 bg-slate-300 p-1"
                    />
            </div>
            <div class="flex flex-col min-w-64">
                <label for="password" class="text-slate-50">Password</label>
                <input name="password" type="password" id="password"
                        class="rounded-lg border border-solid border-slate-600 bg-slate-300 p-1"
                    />
            </div>
            <div class="w-full flex flex-row space-x-1">
                <button class="bg-jax-blue rounded-xl p-1 w-full text-slate-200" >Login</button>
                <button formaction="?/register" class="bg-jax-purple rounded-xl p-1 w-full text-slate-200">Register</button>
            </div>
            {#if form?.error}
                <div class="w-full bg-slate-500  rounded-md p-1 text-center">{form.error}</div>
            {/if}
        </form>
    </section>
</div>


