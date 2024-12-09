from chatbot.components.general_chatbot.knowledgebase import KnowledgeBase
import os
from dotenv import load_dotenv
load_dotenv()

kb = KnowledgeBase(google_api_key=os.getenv('GOOGLE_API_KEY'))

# Add a document
kb.add_document('chatbot/test/dgmstechst-circular-no-13-of-2002-safety-management-system.pdf')
print('Successfully added')
