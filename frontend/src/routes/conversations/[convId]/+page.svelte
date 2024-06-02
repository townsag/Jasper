<script lang="ts">
    import Header from '$lib/components/header.svelte';
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { marked } from 'marked';
    import { SyncLoader } from 'svelte-loading-spinners';

    interface Message {
        conv_id: number;
        conv_offset: number;
        sender_role: string;
        content: string;
    }

    interface LoadData {
        messages: Message[];
        error?: string;
    }

    export let data: LoadData;

    // I dont rememeber what this does, should have added a comment haha
    const renderer = {
        listitem(text:string, task:boolean, checked:boolean){
            return `<li>${text}</li>`;
        }
    }
    marked.use({ renderer });

    // this is bound to the value of the input text field
    let user_question: string = "";
    let messages: Message[] = data.messages ? data.messages : [];
    let new_message_error: boolean = false;
    let is_loading: boolean = false;

    function handleKeydown(event: KeyboardEvent) {
        if(event.key === 'Enter' && !event.shiftKey){
            event.preventDefault();
            handleSubmit();
        }
    }

    const handleSubmit = async () => {
        if (is_loading) {
            return;
        }
        is_loading = true;

        // add the new user question to data.messages
        // Todo: add some logic to see if the messages array is populated
        // design choice: if messages has undefined elements then assume that the offset of the
        // new message should be 1. I dont know why messages would have undefined elements
        new_message_error = false;
        const user_message = {
            conv_id:Number($page.params.convId),
            conv_offset:Number(messages.length > 0 ? (messages.at(-1)?.conv_offset ?? 0) + 1 : 1),
            sender_role:"user",
            content:user_question
        };
        messages.push(user_message);
        // this is so that svelt will reactively redraw the messages view
        // need assignment to the variable to trigger svelte reactivity
        // kinda hacky but it is suggested to do it this way in the svelte docs
        messages = messages;

        // console.log("inside conv_id slug page on submit button function");
        // console.log("user questions", user_question);
        // console.log("user message", user_message);
        // console.log("this is messages", messages);

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
            // for svelte reactivity
            messages = messages;
            user_question = "";
            // console.log("server response data", assistant_message);
        } else {
            // remove the failed user message from the ui
            // use assignment to trigger sveltekit reactivity
            messages.pop();
            messages = messages;
            new_message_error = true;
        }
        is_loading = false;
    };
</script>

<div class="h-full flex flex-col items-center justify-center">
    <Header />
    <section class="bg-slate-800 rounded-md m-2 max-w-3xl w-full flex flex-col overflow-y-auto space-y-3 p-3">
        {#if data?.error}
            <div class="w-max border-2 rounded-md border-rose-500 text-rose-500 text-2xl px-2">
                {data?.error}
            </div>
        {:else if messages && messages.length > 0}
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
            {#if is_loading}
                <div class="self-start">
                    <SyncLoader color="#4e96fd" duration="1s"/>
                </div>
            {/if}
        {:else}
            <p class="text-xl text-slate-50 p-2">No messages yet, type below to start the conversation</p>
        {/if}
        {#if new_message_error}
            <div class="bg-slate-700 rounded-md self-end ml-10 p-2 border-2 border-rose-500">
                <div class="text-rose-500">Error sending new message, please try again in a few minutes</div>
            </div>
        {/if}
    </section>

    <section class="bg-slate-200 flex flex-row items-center max-w-3xl w-full rounded-md mx-2 mb-3">
        <textarea 
            class="bg-slate-200 h-36 w-full rounded-md p-2 resize-none outline-none"
            name="user-content"
            bind:value={user_question}
            on:keydown={handleKeydown}
        ></textarea>
        <!-- Design choice: added these checks here instead of in handleSubmit to reduce flickering in the ui and reduce number of function calls  -->
        {#if is_loading || user_question.length < 1}
            <div class="bg-gray-400 h-max m-2 p-2 rounded-md">Submit</div>
        {:else}
            <button 
                class="bg-jax-blue h-max m-2 p-2 rounded-md hover:bg-jax-blue-hover"
                on:click={handleSubmit}
                >
                Submit
            </button>
        {/if}
    </section>
    
</div>


<!-- max-w-full -->
<!-- min-h-max grow -->
<!-- <p class="text-slate-50">{message.content}</p> -->


<!-- <div class="bg-slate-700 max-w-full rounded-md self-start mr-10 p-2">
    <div class="text-slate-50 whitespace-pre-wrap overflow-x-auto">{@html marked(message.content)}</div>
</div> -->