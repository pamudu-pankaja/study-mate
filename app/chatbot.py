query = "What was the of MacDowell's mission  ?"
path = "vector"
index_name = "history-text-1"
start_page = 11

# from vector_store.vectore_search import search

# result = search(query,index_name)

# print(result)


# from vector_store.file_load import load_pdf

file_path = "app/data/3_grade-11-history-text-book.pdf"
# result = load_pdf(file_path=file_path)

# from vector_store.pinecorn_client import pinecone_db

# response = pinecone_db.create_index()
# upsert = pinecone_db.upsert(data=result)

# print(upsert)

# from agents import RAGAgent
# result=RAGAgent.vector_search(query,index_name)
# RAGAgent.import_file(file_path,index_name)

# from agents.web_search.web_agent import web_search
# from agents.chat_bot_agent.tools.summarizer import summerize_result
# from agents.llm.llm import GeminiLLM

# data = web_search("Who is the sri lankan president")
# print(data)
# data = [{'title': 'President of Sri Lanka - Wikipedia', 'url': 'https://en.wikipedia.org/wiki/President_of_Sri_Lanka', 'snippet': 'Anura Kumara Dissanayake is the 10th and current president, having assumed office on 23 September 2024, after being declared the winner of the 2024 presidential\xa0...'}, {'title': "Anura Kumara Dissanayake: Who is Sri Lanka's new president?", 'url': 'https://www.bbc.com/news/articles/c206l7pz5v1o', 'snippet': "Sep 22, 2024 ... Who is Sri Lanka's new president Anura Kumara Dissanayake? ... Left-leaning politician Anura Kumara Dissanayake has been elected as Sri Lanka's\xa0..."}, {'title': 'Ranil Wickremesinghe - Wikipedia', 'url': 'https://en.wikipedia.org/wiki/Ranil_Wickremesinghe', 
# 'snippet': 'Ranil Wickremesinghe is a Sri Lankan politician who served as the ninth president of Sri Lanka from 2022 to 2024. Previously, he served as Prime Minister of\xa0...'}, {'title': "Anura Kumara Dissanayake sworn in as Sri Lanka's president", 'url': 'https://www.bbc.com/news/articles/cqxr03x4dvzo', 'snippet': "Sep 22, 2024 ... Sri Lanka swears in new left-leaning president ... Sri Lanka President Media via Reuters Sri Lanka's new president Anura Kumara Dissanayake speaks\xa0..."}, {'title': "Sri Lanka's Uprising Forces Out a President but Leaves System in ...", 'url': 'https://www.crisisgroup.org/asia/south-asia/sri-lanka/sri-lankas-uprising-forces-out-president-leaves-system-crisis', 'snippet': "Jul 18, 2022 ... Sri Lanka's Uprising Forces Out a President but Leaves System in Crisis. Crowds of ordinary Sri Lankans stormed the presidential residence on 9\xa0..."}]

# summary = summerize_result(data)
# from agents.chat_bot_agent.tool_handler import ToolHandle 


# data = ToolHandle.get_context(query,index_name=index_name)
# result = GeminiLLM.get_response(query,context=data)
# print(result)

from agents import RAGAgent
results = RAGAgent.import_file(file_path,index_name,start_page=start_page)

# from agents import ChatBotAgent

# results = ChatBotAgent.get_response(query,path,index_name)

print(f"\n\n{results}")

