import type { Actions, RequestEvent } from './$types';
import { fail, redirect} from '@sveltejs/kit';
import { env } from '$env/dynamic/private';

interface LoginResponseData {
    access_token: string;
}

export const actions: Actions = {
    login: async (event: RequestEvent) => {
        console.log("calling login form action");
        // this should check that the user is in the database then return a 
        // new jwt token and redirect to the home page
        const data = await event.request.formData();
        const username = data.get("username");
        const password = data.get("password");

        if (!username || !password) {
            return fail(400, {error: "missing username or password"});
        }
        
        const response = await fetch(`http://${env.PRIVATE_BACKEND_HOST}:${env.PRIVATE_BACKEND_PORT}/auth/login`, {
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
                // console.log(response_data)
                return fail(401, { error:response_data.msg});
            }

            return fail(401, { error:"flask api error"});
        }

        // add the new JWT token to the users cookies
        // Set the cookie
        const response_data: LoginResponseData = await response.json();
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

    register: async (event: RequestEvent) => {
        console.log("calling register form action");
        const data = await event.request.formData();
        const username = data.get("username");
        const password = data.get("password");

        if (!username || !password) {
            return fail(400, {error: "missing username or password"});
        }
        
        const response = await fetch(`http://${env.PRIVATE_BACKEND_HOST}:${env.PRIVATE_BACKEND_PORT}/auth/register`, {
            method:"POST",
            headers: {
                'Content-Type': "application/json"
            },
            body:JSON.stringify({username:username, password:password})
        });

        if(!response.ok){
            console.log("request failed");
            if (response.status == 422){
                const response_data = await response.json();
                console.log(response_data)
                return fail(422, { error:response_data.msg});
            }

            return fail(401, { error:"flask api error"});
        }
        // add the new JWT token to the users cookies
        // Set the cookie
        const response_data: LoginResponseData = await response.json();
        const token: string = response_data["access_token"];
        console.log("registration success");
        console.log("inside form action register: ", token);

        event.cookies.set('AuthorizationToken', `Bearer ${token}`, {
            path: '/',
            sameSite: 'strict',
            maxAge: 60 * 60 * 24 // 1 day
        });

        return redirect(302, "/conversations");
    }
};