import { redirect, type Actions } from "@sveltejs/kit";

export async function load(event) {
    // console.log(event);
    // console.log(event.params);
    // console.log(event.params.slug);

    console.log("in slug page server load function");
    if(!event.locals.user){
        console.log("no user so redirecting");
        throw redirect(302, '/');
    }
    const conv_id = event.params.convId;

    // query the messages from this conversation
    const response = await fetch(`http://127.0.0.1:5000/chat/allMessages?conv_id=${conv_id}`, {
        method:"GET",
        headers: {
            'Authorization':`Bearer ${event.locals.user.token}`
        }
    });

    // console.log("response\n", response);
    const data = await response.json();

    return {
        messages: data
    };
}

