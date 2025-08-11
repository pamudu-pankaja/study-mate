from pinecone import Pinecone
from app.config.config import PINECORN_API_KEY


pc = Pinecone(api_key=PINECORN_API_KEY)

def delete_book(index_name , namespace):
    index = pc.Index(index_name)
    try:
        index.delete(delete_all=True , namespace=namespace)
        print(f"All vectors deleted in namespace '{namespace}'.")
        return "success"
    except Exception as e:
        print(f"Error deleting vectors in namespace '{namespace}': {e}")
        return f"error"
    
delete_book("text-books","History Grade10")

# try:
#     result = RAGAgent.import_file(file_path, index_name, starting_page)
# except Exception as e:
#     print(e)

# if result == "success":
#     return jsonify({"message": "File added successfully", "status": "success"})
# else:
#     return jsonify({"message": "Failed to process PDF"}), 500

# except Exception as e:
# print(f"Error during file importing : {e}")
# return (
#     jsonify(
#         {
#             "message": "Error during file import",
#             "status": "error",
#             "error_msg": f"Something went wrong while importing file : {e}",
#         }
#     ),
#     500,
# )