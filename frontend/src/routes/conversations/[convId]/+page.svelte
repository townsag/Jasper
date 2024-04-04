<script lang="ts">
    import Header from '$lib/components/header.svelte';
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { marked } from 'marked';
    export let data;
    console.log("in messages page");

    const renderer = {
        listitem(text:string, task:boolean, checked:boolean){
            return `<li>${text}</li>`;
        }
    }
    marked.use({ renderer });

    let user_question: string = "";

    let messages = data.messages ? data.messages : [];

    const onSubmit = async () => {
        // add the new user question to data.messages
        // Todo: add some logic to see if the messages array is populated
        console.log("this is messages", messages);
        const user_message = {
            conv_id:$page.params.convId,
            conv_offset:messages.length > 0 ? messages.at(-1).conv_offset + 1 : 1,
            sender_role:"user",
            content:user_question
        };
        messages.push(user_message);
        // this is so that svelt will reactively redraw the messages view
        // need assignment to the variable to trigger svelte reactivity
        messages = messages;

        console.log("inside conv_id slug page on submit button function");
        console.log("user questions", user_question);
        console.log("user message", user_message);
        console.log("this is messages", messages);

        const server_response = await fetch("/api/chat-submit",{
            method:"POST",
            headers:{
                "Content-Type":"application/json"
            },
            body:JSON.stringify(user_message)
        });

        if (server_response.ok){
            const assistant_message = await server_response.json();
            messages.push(assistant_message);
            messages = messages;
            console.log("server response data", assistant_message);
        }
    };
</script>

<div class="h-full flex flex-col items-center justify-center">
    <Header />
    <section class="bg-slate-800 rounded-md m-2 max-w-3xl w-full flex flex-col overflow-y-auto space-y-3 p-3">
        {#if messages && messages.length > 0}
            {#each messages as message}
                {#if message.sender_role === "user"}
                    <div class="bg-slate-500 rounded-md self-end ml-10 p-2">
                        <div class="text-slate-50 whitespace-pre-wrap">{message.content}</div>
                    </div>
                {:else}
                    <div class="self-start pr-10 max-w-full">
                        <div class="bg-slate-700 rounded-md p-2 ">
                            <div class="text-slate-50 text-sm overflow-x-auto">{@html marked(message.content)}</div>
                        </div>
                    </div>
                    
                    <!-- <div class="bg-slate-700 max-w-full rounded-md self-start mr-10 p-2">
                        <div class="text-slate-50 whitespace-pre-wrap overflow-x-auto">{@html marked(message.content)}</div>
                    </div> -->
                {/if}
            {/each}
        {:else}
            <p class="text-xl text-slate-50 p-2">No messages yet, type below to start the conversation</p>
        {/if}
    </section>

    <section class="bg-slate-200 flex flex-row items-center max-w-3xl w-full rounded-md mx-2 mb-3">
        <textarea class="bg-slate-200 h-36 w-full rounded-md p-2 resize-none outline-none" 
                    type="text" 
                    name="user-content"
                    bind:value={user_question}></textarea>
        <button class="bg-jax-blue h-max m-2 p-2 rounded-md hover:bg-jax-blue-hover"
                on:click={onSubmit}>Submit</button>
    </section>
    
</div>


<!-- max-w-full -->
<!-- min-h-max grow -->
<!-- <p class="text-slate-50">{message.content}</p> -->


<!-- <div class="bg-slate-700 max-w-full rounded-md self-start mr-10 p-2">
    <div class="text-slate-50 whitespace-pre-wrap overflow-x-auto">{@html marked(message.content)}</div>
</div> -->