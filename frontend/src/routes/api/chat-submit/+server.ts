

export async function POST(event){
    console.log("inside api.chat-submit server post route");
    const { conv_id, conv_offset, content } = await event.request.json();
    console.log("conv_id", conv_id);
    console.log("conv_offset", conv_offset);
    console.log("content", content);

    const response = await fetch("http://127.0.0.1:5000/chat/newMessage",{
        method:"POST",
        headers:{
            'Authorization':`Bearer ${event.locals.user.token}`,
            "Content-Type":"application/json"
        },
        body:JSON.stringify({
            conv_id:conv_id,
            conv_offset:conv_offset,
            content:content
        })
    });

    const data = await response.json();
    console.log("inside the api/chat-submit/POST fucntion");
    console.log(data);



    return new Response(
        JSON.stringify({ 
            conv_id:conv_id, 
            conv_offset:conv_offset + 1,
            sender_role:'assistant',
            content:data.content
        }), 
        {
            status:200,
            headers: {
                'Content-Type': 'application/json'
            }
      });
}

// optionally doesnt have to have a message id

// "message_id": message[0],
// "conv_id": message[1],
// "conv_offset": message[2],
// "sender_role": message[3],
// "content":message[4]