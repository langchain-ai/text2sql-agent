from langsmith import Client
from dotenv import load_dotenv

load_dotenv(override=True)

client = Client()

# Create a dataset
examples = [
    {
        "inputs": {
            "question": "How many songs do you have by James Brown",
        },
        "outputs": {
            "response": "We have 20 songs by James Brown",
            "trajectory": ["question_answering_agent", "lookup_track"]
        }
    },
    {
        "inputs": {
            "question": "My name is Aaron Mitchell and I'd like a refund.",
        },
        "outputs": {
            "response": "I need some more information to help you with the refund. Please specify your phone number, the invoice ID, or the line item IDs for the purchase you'd like refunded.",
            "trajectory": ["refund_agent"],
        }
    },
    {
        "inputs": {
            "question": "My name is Aaron Mitchell and I'd like a refund on my Led Zeppelin purchases. My number is +1 (204) 452-6452",
        },
        "outputs": {
            "response": 'Which of the following purchases would you like to be refunded for?\n\n  invoice_line_id  track_name                        artist_name    purchase_date          quantity_purchased    price_per_unit\n-----------------  --------------------------------  -------------  -------------------  --------------------  ----------------\n              267  How Many More Times               Led Zeppelin   2009-08-06 00:00:00                     1              0.99\n              268  What Is And What Should Never Be  Led Zeppelin   2009-08-06 00:00:00                     1              0.99',
            "trajectory": ["refund_agent", "lookup"],
        },
    },
    {
        "inputs": {
            "question": "Who recorded Wish You Were Here again? What other albums of there's do you have?",
        },
        "outputs": {
            "response": "Wish You Were Here is an album by Pink Floyd",
            "trajectory": ["question_answering_agent", "lookup_album"],
        },
    },
    {
        "inputs": {
            "question": "I want a full refund for invoice 237",
        },
        "outputs": {
            "response": "You have been refunded $0.99.",
            "trajectory": ["refund_agent", "refund"],
        }
    },
]

dataset_name = "Text2SQL Agent: E2E"

if not client.has_dataset(dataset_name=dataset_name):
    dataset = client.create_dataset(dataset_name=dataset_name)
    client.create_examples(
        dataset_id=dataset.id,
        examples=examples
    )