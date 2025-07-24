from dotenv import load_dotenv
from langsmith import Client

load_dotenv(override=True)

client = Client()

# Create a dataset for text2sql agent with Chinook music database
examples = [
    {
        "inputs": {
            "question": "How many songs do you have by Queen?",
        },
        "outputs": {
            "sql": "SELECT COUNT(*) FROM Track t JOIN Artist a ON t.AlbumId IN (SELECT AlbumId FROM Album WHERE ArtistId = a.ArtistId) WHERE a.Name = 'Queen'",
            "response": "We have 15 songs by Queen in our database.",
        },
    },
    {
        "inputs": {
            "question": "What are the top 5 most expensive tracks?",
        },
        "outputs": {
            "sql": "SELECT Name, UnitPrice FROM Track ORDER BY UnitPrice DESC LIMIT 5",
            "response": "The top 5 most expensive tracks are: [list of tracks with prices]",
        },
    },
    {
        "inputs": {
            "question": "How many albums does Led Zeppelin have?",
        },
        "outputs": {
            "sql": "SELECT COUNT(*) FROM Album a JOIN Artist ar ON a.ArtistId = ar.ArtistId WHERE ar.Name = 'Led Zeppelin'",
            "response": "Led Zeppelin has 14 albums in our database.",
        },
    },
    {
        "inputs": {
            "question": "What is the total revenue from sales in 2010?",
        },
        "outputs": {
            "sql": "SELECT SUM(Total) FROM Invoice WHERE strftime('%Y', InvoiceDate) = '2010'",
            "response": "The total revenue from sales in 2010 was $1,383.51.",
        },
    },
    {
        "inputs": {
            "question": "Which customers have spent more than $100?",
        },
        "outputs": {
            "sql": "SELECT c.FirstName, c.LastName, SUM(i.Total) as TotalSpent FROM Customer c JOIN Invoice i ON c.CustomerId = i.CustomerId GROUP BY c.CustomerId HAVING SUM(i.Total) > 100 ORDER BY TotalSpent DESC",
            "response": "Customers who have spent more than $100 include: [list of customers with their total spending]",
        },
    },
]

dataset_name = "text2sql-agent"

if not client.has_dataset(dataset_name=dataset_name):
    dataset = client.create_dataset(dataset_name=dataset_name)
    client.create_examples(dataset_id=dataset.id, examples=examples)
