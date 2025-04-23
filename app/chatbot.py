from app.agents import ChatBotAgent
from app.agents import RAGAgent  

def ask_question():
    while True:
        print("\n=== Ask a Question ===")
        print("1. Use Vector Search")
        print("2. Use Web Search")        
        print("3. Use LLM")
        print("4. Previous")
        choice = input("Choose a method (1-4): ")

        if choice == "4":
            return
        
        index_name = ""
        while True:
            query = input("Enter your question (q to quit): ")
            if query.lower() == "q":
                ask_question()
                break 
            
            if choice == "2":
                result = ChatBotAgent.get_response(query,path="web")
                print("\n--- Web Search Results ---")
                print(f"\n{result}")
                
            elif choice == "1":
                get_index_name = input("Enter the index name: ") if index_name == "" else index_name
                index_name = get_index_name
                result = ChatBotAgent.get_response(query,path="vector",index_name=index_name)
                print("\n--- Vector Search Results ---")
                print(f"\n{result}")
            elif choice == "3":
                result = ChatBotAgent.get_response(query,path=None)
                print("\n--- LLM Response ---")
                print(f"\n{result}")
            else:
                print("Invalid choice")

            next_action = input("\nAsk another question? (y/n): ")
            if next_action.lower() != "y":
                break

def add_file_flow():
    print("\n=== Add File to Index ===")
    index_name = input("Enter index name: ")
    file_path = input("Enter file path: ")
    start_page = int(input("Enter logical start page: "))
    
    RAGAgent.import_file(file_path, index_name, start_page)
    print("File indexed successfully.")

    while True:
        print("\n1. Add Another File")
        print("2. Add New Index")
        print("3. Previous")
        choice = input("Choose an option (1-3): ")

        if choice == "1":
            file_path = input("Enter file path: ")
            RAGAgent.import_file(file_path, index_name, start_page)
            print("File added to the existing index.")
        elif choice == "2":
            add_file_flow() 
            break
        elif choice == "3":
            return
        else:
            print("Invalid option.")

def main():
    while True:
        print("\n=== AI Assistant CLI ===")
        print("1. Ask a Question")
        print("2. Add a File to Index")
        print("3. Quit")
        choice = input("Select an option (1-3): ")

        if choice == "1":
            ask_question()
        elif choice == "2":
            add_file_flow()
        elif choice == "3":
            print("Exiting program. Goodbye!")
            break
        else:
            print("Invalid choice.")

