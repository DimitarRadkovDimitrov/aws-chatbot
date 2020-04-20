import boto3
from botocore.exceptions import ClientError

def grant_lex_lambda_permissions(client, function_name):
    try:
        response = client.add_permission(
            Action='lambda:InvokeFunction',
            FunctionName=function_name,
            Principal='lex.amazonaws.com',
            StatementId='ID-1'
        )
    except ClientError as e:
        pass


def create_bot_if_not_exists(client, bot_name, alias, intent_names, locale='en-US', child_directed=False):
    intents = []
    for intent_name in intent_names:
        intents.append({
            'intentName': intent_name,
            'intentVersion': '$LATEST'
        })

    chatbot = get_bot_by_name_and_alias(client, bot_name, alias)
    if chatbot is None:
        chatbot = client.put_bot(
            name=bot_name,
            locale=locale,
            childDirected=child_directed,
            intents=intents,
            abortStatement={
                'messages': [
                    build_message_dict("Sorry I can't fulfill your request.")
                ]
            }
        )
        print("Created bot with name {} and alias {}".format(bot_name, alias))
        client.put_bot_alias(name=alias, botName=bot_name, botVersion='$LATEST')
    return chatbot
    

def get_bot_by_name_and_alias(client, bot_name, alias):
    try:
        bot_metadata = client.get_bot(name=bot_name, versionOrAlias=alias)
        print("Bot with name {} and alias {} already exists".format(bot_name, alias))
        return bot_metadata
    except ClientError as e:
        print("Bot with name {} and alias {} doesn't exist".format(bot_name, alias))
        return None
    

def create_service_intents_if_not_exists(client):
    slots = build_user_data_slot_types()
    create_taxi_service_intent(client, slots)
    create_food_service_intent(client, slots)
    create_home_care_service_intent(client, slots)
    create_cleaning_service_intent(client, slots)
    return ['OrderTaxi', 'OrderFood', 'OrderHomeCare', 'OrderCleaning']


def build_user_data_slot_types():
    slots = []
    slots.append(build_first_name_slot())
    slots.append(build_last_name_slot())
    slots.append(build_street_address_slot())
    slots.append(build_city_slot())
    slots.append(build_email_address_slot())
    slots.append(build_phone_number_slot())
    slots.append(build_date_slot())
    slots.append(build_time_slot())
    return slots


def build_first_name_slot():
    first_name_slot = {
        'name': 'FirstName',
        'slotConstraint': 'Required',
        'slotType': 'AMAZON.US_FIRST_NAME',
        'valueElicitationPrompt': {
            'messages': [
                build_message_dict("What's your first name?")
            ],
            'maxAttempts': 5
        },
        'priority': 1
    }
    return first_name_slot 


def build_last_name_slot():
    last_name_slot = {
        'name': 'LastName',
        'slotConstraint': 'Required',
        'slotType': 'AMAZON.US_LAST_NAME',
        'valueElicitationPrompt': {
            'messages': [
                build_message_dict("What's your last name?")
            ],
            'maxAttempts': 5
        },
        'priority': 2
    }
    return last_name_slot


def build_street_address_slot():
    address_slot = {
        'name': 'Address',
        'slotConstraint': 'Required',
        'slotType': 'AMAZON.StreetAddress',
        'valueElicitationPrompt': {
            'messages': [
                build_message_dict("What's your street address?")
            ],
            'maxAttempts': 5
        },
        'priority': 3
    }
    return address_slot


def build_city_slot():
    city_slot = {
        'name': 'City',
        'slotConstraint': 'Required',
        'slotType': 'AMAZON.EUROPE_CITY',
        'valueElicitationPrompt': {
            'messages': [
                build_message_dict("What city are you in?")
            ],
            'maxAttempts': 5
        },
        'priority': 4
    }
    return city_slot


def build_email_address_slot():
    email_slot = {
        'name': 'Email',
        'slotConstraint': 'Required',
        'slotType': 'AMAZON.EmailAddress',
        'valueElicitationPrompt': {
            'messages': [
                build_message_dict("What's your email address?")
            ],
            'maxAttempts': 5
        },
        'priority': 5
    }
    return email_slot


def build_phone_number_slot():
    phone_number_slot = {
        'name': 'PhoneNumber',
        'slotConstraint': 'Required',
        'slotType': 'AMAZON.PhoneNumber',
        'valueElicitationPrompt': {
            'messages': [
                build_message_dict("What's your phone number?")
            ],
            'maxAttempts': 5
        },
        'priority': 6
    }
    return phone_number_slot


def build_date_slot():
    date_slot = {
        'name': 'Date',
        'slotConstraint': 'Required',
        'slotType': 'AMAZON.DATE',
        'valueElicitationPrompt': {
            'messages': [
                build_message_dict("On what date should I place the order?")
            ],
            'maxAttempts': 5
        },
        'priority': 7
    }
    return date_slot


def build_time_slot():
    time_slot = {
        'name': 'Time',
        'slotConstraint': 'Required',
        'slotType': 'AMAZON.TIME',
        'valueElicitationPrompt': {
            'messages': [
                build_message_dict("For what time should I place the order?")
            ],
            'maxAttempts': 5
        },
        'priority': 8
    }
    return time_slot


def create_taxi_service_intent(client, slots):
    intent_name = 'OrderTaxi'

    try:
        client.get_intent(name=intent_name, version='$LATEST')
        print("Intent with name {} already exists".format(intent_name))

    except ClientError as e:
        confirmation_prompt = {}
        conclusion_statement = {}
        rejection_statement = {}

        confirmation_prompt['messages'] = []
        confirmation_prompt['maxAttempts'] = 5
        conclusion_statement['messages'] = []
        rejection_statement['messages'] = []

        sample_utterances = [
            "Taxi",
            "Order taxi",
            "I want to order a taxi",
            "Call me a taxi"
        ]

        confirmation_prompt['messages'].append(build_message_dict("Should I order the Taxi?"))
        conclusion_statement['messages'].append(build_message_dict("Taxi is on its way!"))
        rejection_statement['messages'].append(build_message_dict("Okay, I cancelled the order"))    

        response = client.put_intent(
            name=intent_name,
            slots=slots,
            sampleUtterances=sample_utterances,
            confirmationPrompt=confirmation_prompt,
            rejectionStatement=rejection_statement,
            conclusionStatement=conclusion_statement,
            fulfillmentActivity={
                'type': 'CodeHook',
                'codeHook': {
                    'uri': '[YOUR_LAMBDA_ARN]',
                    'messageVersion': '1.0'
                }
            }
        )
        print("Intent with name {} doesn't exist. Created one instead".format(intent_name))


def create_food_service_intent(client, slots):
    intent_name = 'OrderFood'

    try:
        client.get_intent(name=intent_name, version='$LATEST')
        print("Intent with name {} already exists".format(intent_name))

    except ClientError as e:
        confirmation_prompt = {}
        conclusion_statement = {}
        rejection_statement = {}

        confirmation_prompt['messages'] = []
        confirmation_prompt['maxAttempts'] = 5
        conclusion_statement['messages'] = []
        rejection_statement['messages'] = []

        sample_utterances = [
            "Food",
            "Order food",
            "I want to order food",
            "Order me some food"
        ]

        confirmation_prompt['messages'].append(build_message_dict("Should I place the order?"))
        conclusion_statement['messages'].append(build_message_dict("Food is on its way!"))
        rejection_statement['messages'].append(build_message_dict("Okay, I cancelled the order"))    

        response = client.put_intent(
            name=intent_name,
            slots=slots,
            sampleUtterances=sample_utterances,
            confirmationPrompt=confirmation_prompt,
            rejectionStatement=rejection_statement,
            conclusionStatement=conclusion_statement,
            fulfillmentActivity={
                'type': 'CodeHook',
                'codeHook': {
                    'uri': '[YOUR_LAMBDA_ARN]',
                    'messageVersion': '1.0'
                }
            }
        )
        print("Intent with name {} doesn't exist. Created one instead".format(intent_name))


def create_home_care_service_intent(client, slots):
    intent_name = 'OrderHomeCare'

    try:
        client.get_intent(name=intent_name, version='$LATEST')
        print("Intent with name {} already exists".format(intent_name))

    except ClientError as e:
        confirmation_prompt = {}
        conclusion_statement = {}
        rejection_statement = {}

        confirmation_prompt['messages'] = []
        confirmation_prompt['maxAttempts'] = 5
        conclusion_statement['messages'] = []
        rejection_statement['messages'] = []

        sample_utterances = [
            "Home care",
            "I need a home care service"    
        ]

        confirmation_prompt['messages'].append(build_message_dict("Should I place the order?"))
        conclusion_statement['messages'].append(build_message_dict("A home care professional is on their way!"))
        rejection_statement['messages'].append(build_message_dict("Okay, I cancelled the order"))    

        response = client.put_intent(
            name=intent_name,
            slots=slots,
            sampleUtterances=sample_utterances,
            confirmationPrompt=confirmation_prompt,
            rejectionStatement=rejection_statement,
            conclusionStatement=conclusion_statement,
            fulfillmentActivity={
                'type': 'CodeHook',
                'codeHook': {
                    'uri': '[YOUR_LAMBDA_ARN]',
                    'messageVersion': '1.0'
                }
            }
        )
        print("Intent with name {} doesn't exist. Created one instead".format(intent_name))


def create_cleaning_service_intent(client, slots):
    intent_name = 'OrderCleaning'

    try:
        client.get_intent(name=intent_name, version='$LATEST')
        print("Intent with name {} already exists".format(intent_name))

    except ClientError as e:
        confirmation_prompt = {}
        conclusion_statement = {}
        rejection_statement = {}

        confirmation_prompt['messages'] = []
        confirmation_prompt['maxAttempts'] = 5
        conclusion_statement['messages'] = []
        rejection_statement['messages'] = []

        sample_utterances = [
            "Cleaning service",
            "Order cleaning service",
            "I need someone to clean my house",
            "Order me a maid"
        ]

        confirmation_prompt['messages'].append(build_message_dict("Should I place the order?"))
        conclusion_statement['messages'].append(build_message_dict("A maid is on their way!"))
        rejection_statement['messages'].append(build_message_dict("Okay, I cancelled the order"))    

        response = client.put_intent(
            name=intent_name,
            slots=slots,
            sampleUtterances=sample_utterances,
            confirmationPrompt=confirmation_prompt,
            rejectionStatement=rejection_statement,
            conclusionStatement=conclusion_statement,
            fulfillmentActivity={
                'type': 'CodeHook',
                'codeHook': {
                    'uri': '[YOUR_LAMBDA_ARN]',
                    'messageVersion': '1.0'
                }
            }
        )
        print("Intent with name {} doesn't exist. Created one instead".format(intent_name))


def build_message_dict(message_content, content_type='PlainText'):
    message = {}
    message['contentType'] = content_type
    message['content'] = message_content
    return message

    
if __name__ == "__main__":
    grant_lex_lambda_permissions(boto3.client('lambda', 'us-east-1'), 'update_service_data_table')
    client = boto3.client('lex-models', 'us-east-1')
    created_service_names = create_service_intents_if_not_exists(client)
    chatbot = create_bot_if_not_exists(client, 'dimbot', 'dim', created_service_names)

