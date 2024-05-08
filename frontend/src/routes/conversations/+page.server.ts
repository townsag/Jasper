import { redirect, type Actions } from "@sveltejs/kit";

interface Conversation {
    conv_id: number,
    user_id: number,
    tag_description: string,
    started_date: string,
    most_recent_entry_date: string
}

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
    // ToDo: failing to load conversations should show some type of error

    console.log("inside conversations page server load function");
    if (response.ok) {
        const conversations: Conversation[] = await response.json();
        return { conversations };
    } else {
        const conversations: Conversation[] = [];
        return { conversations };
    }
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
        // ToDo: starting a new conversation should redirect to the new conversation page
        // ToDo: failing to start a new conversation should show some sort of error
    },
};