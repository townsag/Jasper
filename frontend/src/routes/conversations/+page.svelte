<script lang="ts">

    interface ConversationData {
        conv_id: number;
        user_id: number;
        tag_description: string;
        started_date: string;
        most_recent_entry_date: string;
    }
    import Header from '$lib/components/header.svelte';
    export let data;
</script>

<Header />

<section class="bg-black flex flex-col items-center p-8 space-y-4">
    <div class="flex flex-row items-center w-full max-w-4xl">
        <h1 class="text-slate-50 text-5xl">Your Conversations</h1>
    </div>
    <ul class="max-w-4xl w-full space-y-2">
        <form action="?/newConversation" method="POST">
            <button class="bg-jax-blue hover:bg-jax-blue-hover w-full min-h-24 rounded-md text-3xl text-slate-200">New Conversation</button>
        </form>
        {#each data.conversations as conversation}
            <form action="?/viewConversation&conv_id={conversation.conv_id}" method="POST">
                <button class="bg-slate-800 hover:bg-slate-700 flex flex-row min-h-24 justify-between items-center p-4 w-full rounded-md">
                    <input type="hidden" name="conv_id" value={conversation.conv_id} />
                    <h2 class="text-3xl text-slate-50">{conversation["tag_description"]}</h2>
                    <div class="flex flex-col space-y-1">
                        <p class="text-md text-slate-50">{conversation["started_date"]}</p>
                        <p class="text-md text-slate-50">{conversation["most_recent_entry_date"]}</p>
                    </div>
                </button>
            </form>
        {/each}
    </ul>
</section>

