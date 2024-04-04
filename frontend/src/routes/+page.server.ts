import type { Actions } from './$types';
import { fail, redirect} from '@sveltejs/kit';

export const actions: Actions = {
    login: async (event) => {
        console.log("calling login form action");
        // this should check that the user is in the database then return a 
        // new jwt token and redirect to the home page
        const data = await event.request.formData();
        const username = data.get("username");
        const password = data.get("password");

        if (!username || !password) {
            return fail(400, {error: "missing username or password"});
        }
        
        const response = await fetch("http://127.0.0.1:5000/auth/login", {
            method:"POST",
            headers: {
                'Content-Type': "application/json"
            },
            body:JSON.stringify({username:username, password:password})
        });
        
        let response_data: any;

        if(!response.ok){
            console.log("request failed");
            if (response.status == 401){
                response_data = await response.json();
                // console.log(response_data)
                return fail(401, { error:response_data.msg});
            }

            return fail(401, { error:"flask api error"});
        }

        // add the new JWT token to the users cookies
        // Set the cookie
        response_data = await response.json();
        const token: string = response_data["access_token"];
        console.log("login success");
        console.log("inside form action login: ", token);

        event.cookies.set('AuthorizationToken', `Bearer ${token}`, {
            path: '/',
            sameSite: 'strict',
            maxAge: 60 * 60 * 24 // 1 day
        });

        console.log("redirecting to conversations\n\n");
        return redirect(302, "/conversations");
    },

    register: async (event) => {
        console.log("calling register form action");
        const data = await event.request.formData();
        const username = data.get("username");
        const password = data.get("password");

        if (!username || !password) {
            return fail(400, {error: "missing username or password"});
        }
        
        const response = await fetch("http://127.0.0.1:5000/auth/register", {
            method:"POST",
            headers: {
                'Content-Type': "application/json"
            },
            body:JSON.stringify({username:username, password:password})
        });

        if(!response.ok){
            console.log("request failed");
            if (response.status == 401){
                const response_data = await response.json();
                console.log(response_data)
                return fail(401, { error:response_data.msg});
            }

            return fail(401, { error:"flask api error"});
        }

        return redirect(302, "/conversations");
    }
};