import type { RequestEvent } from './$types';

interface RequestData {
	conv_id: number;
	conv_offset: number;
	content: string;
}

interface ResponseData {
	conv_id: number;
	conv_offset: number;
	sender_role: 'assistant';
	content: string;
}

export async function POST(event: RequestEvent): Promise<Response> {
	const { conv_id, conv_offset, content }: RequestData = await event.request.json();

	try {
		const response = await fetch('http://127.0.0.1:5000/chat/newMessage', {
			method: 'POST',
			headers: {
				Authorization: `Bearer ${event.locals.user.token}`,
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				conv_id: conv_id,
				conv_offset: conv_offset,
				content: content
			})
		});
        // ToDo: add some error handling behavior here if the flask app fails

		const data = await response.json();
		const responseData: ResponseData = {
			conv_id: conv_id,
			conv_offset: conv_offset + 1,
			sender_role: 'assistant',
			content: data.content
		};
		return new Response(JSON.stringify(responseData), {
			status: 200,
			headers: {
				'Content-Type': 'application/json'
			}
		});
	} catch (error) {
		return new Response(JSON.stringify({ msg: 'an error has occured' }), {
			status: 500,
			headers: { 'Content-Type': 'application/json' }
		});
	}
}
