import { redirect, type Actions } from "@sveltejs/kit";

export async function load(event){
    console.log("in conversations page.server.ts");
    if(!event.locals.user){
        console.log("no user so redirecting");
        throw redirect(302, '/');
    }

    // load the conversation history from the flask api
    const response = await fetch("http://127.0.0.1:5000/chat/allConversations", {
        method:"GET",
        headers: {
            'Authorization':`Bearer ${event.locals.user.token}`
        }
    });
    // console.log(response);
    const conversations = await response.json();

    console.log("inside conversations page server load function");
    // console.log(conversations);
    return {
        conversations
    };
}

export const actions: Actions = {
    newConversation: async (event) => {
        // call the api routes to make a new conversation
        const response = await fetch("http://127.0.0.1:5000/chat/conversation", {
            method:"POST",
            headers: {
                'Authorization':`Bearer ${event.locals.user.token}`
            },
        });
        // ToDo: redirect to the conversation page
    },

    // viewConversation: async (event) => {
    //     // console.log(event);
    //     const data = await event.request.formData();
    //     console.log(data.get("conv_id"));
    //     const conv_id = event.url.searchParams.get('conv_id');
    //     console.log(data);
    //     console.log(conv_id);
    // }
};