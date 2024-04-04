<script lang="ts">
    console.log("inside conversations page script js");
	import { goto } from '$app/navigation';

    // interface ConversationData {
    //     conv_id: number;
    //     user_id: number;
    //     tag_description: string;
    //     started_date: string;
    //     most_recent_entry_date: string;
    // };
    
    // console.log("conversations js 2");
    import Header from '$lib/components/header.svelte';
    // console.log("conversations js 3");
    export let data;
    // console.log("conversations.js 4");
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
            <button class="bg-slate-800 hover:bg-slate-700 flex flex-row min-h-24 justify-between items-center p-4 w-full rounded-md"
                    on:click={ () => goto(`/conversations/${conversation.conv_id}`) }>
                <!-- this uses client side navigation instead of server side navigation. I am not sure if we want that
                because the next page will require a server side api call to the flask api to makes sure that
                the user is authenticated and to get the messages from thed database. 
                ToDo: test this navigation to see if it is consitent with what we want-->
                <input type="hidden" name="conv_id" value={conversation.conv_id} />
                <h2 class="text-3xl text-slate-50">{conversation["tag_description"]}</h2>
                <div class="flex flex-col space-y-1">
                    <p class="text-md text-slate-50">{conversation["started_date"]}</p>
                    <p class="text-md text-slate-50">{conversation["most_recent_entry_date"]}</p>
                </div>
            </button>
        {/each}
    </ul>
</section>

