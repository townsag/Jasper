import type { Handle } from "@sveltejs/kit";

// check with the backend server that the user is authenticated then add the authentication information
// to the local storage associated with the current request on the server side
export const handle: Handle = async ({ event, resolve }) => {
    const cookies: string | null = event.request.headers.get("cookie");
    const parsed_cookies: Record<string, string> = parse_cookies(cookies ?? "");
    console.log("in hooks");
    // console.log("parsed cookies", parsed_cookies);
    if (parsed_cookies.AuthorizationToken){
        console.log("found authorization token");
        const token: string = parsed_cookies.AuthorizationToken.split("%20")[1];
        // console.log("token: ", token, "\n");
        // console.log("authorization:", `Bearer ${token}`);
        const response = await fetch("http://127.0.0.1:5000/auth/whoami", {
            method:"GET",
            headers: {
                'Authorization':`Bearer ${token}`
            }
        });

        // console.log(response);
        const response_data = await response.json();
        // console.log("response data", response_data);
        if(response.ok){
            console.log("adding username to locals");
            event.locals.user = {
                username: response_data["username"],
                token: token
            };
        }
    }
    return await resolve(event);
}

function parse_cookies(cookies: string):Record<string,string > {
    const pairs = cookies.split("; ");
    const result: Record<string, string> = {};

    for (const pair of pairs){
        const [key, value] = pair.split("=");
        if (key && value) {
            result[key] = value;
        }
    }
    return result;
}