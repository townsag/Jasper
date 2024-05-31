import { redirect } from "@sveltejs/kit";
import { env } from '$env/dynamic/private';

interface Message {
    conv_id: number;
    conv_offset: number;
    sender_role: string;
    content: string;
}

export async function load(event) {
    if(!event.locals.user){
        console.log("no user so redirecting");
        throw redirect(302, '/');
    }
    const conv_id = event.params.convId;

    // query the messages from this conversation
    const response = await fetch(`http://${env.PRIVATE_BACKEND_HOST}:${env.PRIVATE_BACKEND_PORT}/chat/allMessages?conv_id=${conv_id}`, {
        method:"GET",
        headers: {
            'Authorization':`Bearer ${event.locals.user.token}`
        }
    });

    if (response.ok) {
        const data: Message[] = await response.json();
        return {
            messages: data
        };
    } else {
        return {
            messages: [],
            error: "an error occured when loading messages"
        };
    }
}

