<script lang="ts">
	import { goto } from '$app/navigation';
    import Header from '$lib/components/header.svelte';
	import type { ActionData } from '../$types';
    
    interface ConversationData {
        conv_id: number;
        user_id: number;
        tag_description: string;
        started_date: string;
        most_recent_entry_date: string;
    };

    interface LoadData {
        conversations: ConversationData[];
        error?: string;
    }

    export let data: LoadData;
    export let form: ActionData;
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
        {#if data?.error}
            <div class="w-full rounded-md border-2 border-rose-500 text-rose-500 text-xl text-center">
                {data.error}
            </div>
        {/if}

        {#if form?.error}
            <div class="w-full rounded-md border-2 border-rose-500 text-rose-500 text-xl text-center">
                {form.error}
            </div>      
        {/if}

        {#each data.conversations as conversation}
            <button class="bg-slate-800 hover:bg-slate-700 flex flex-row min-h-24 justify-between items-center p-4 w-full rounded-md"
                    on:click={ () => goto(`/conversations/${conversation.conv_id}`) }>
                <!-- this uses client side navigation instead of server side navigation. I am not sure if we want that
                because the next page will require a server side api call to the flask api to makes sure that
                the user is authenticated and to get the messages from thed database. 
                ToDo: test this navigation to see if it is consitent with what we want-->
                <input type="hidden" name="conv_id" value={conversation.conv_id} />
                <h2 class="text-3xl text-slate-50">{conversation.tag_description}</h2>
                <div class="flex flex-col items-start space-y-1 w-max">
                    <div class="flex flex-row justify-between space-x-1 w-full">
                        <p class="text-md text-slate-50">Started: </p>
                        <p class="text-md text-slate-50">{(new Date(conversation.started_date)).toLocaleString()}</p>
                    </div>
                    <div class="flex flex-row justify-between space-x-1 w-full">
                        <p class="text-md text-slate-50">Most Recent: </p>
                        <p class="text-md text-slate-50">{(new Date(conversation.most_recent_entry_date)).toLocaleString()}</p>
                    </div>
                    <!-- <p class="text-md text-slate-50">Started: {(new Date(conversation.started_date)).toLocaleString()}</p> -->
                    <!-- <p class="text-md text-slate-50">Most Rencent: {(new Date(conversation.most_recent_entry_date)).toLocaleString()}</p> -->
                </div>
            </button>
        {/each}
    </ul>
</section>

