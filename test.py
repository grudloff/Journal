
import pymongo

uri = "mongodb+srv://gabrielrudloff:5HyvTcRDKhEhXlbA@stoned-parrot.nazmopu.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = pymongo.MongoClient(uri)


# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# print db names
print(client.list_database_names())