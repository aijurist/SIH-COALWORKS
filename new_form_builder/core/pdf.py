from langchain_community.document_loaders import UnstructuredPDFLoader
# Specify the path to your PDF file
file_path = 'new_form_builder/data/Overman register.pdf'

# Initialize the UnstructuredLoader with desired parameters
loader = UnstructuredPDFLoader(
    file_path=file_path,
    strategy="hi_res",
)

# List to hold the extracted documents
docs = []

# Load documents lazily and append to the list
for doc in loader.lazy_load():
    docs.append(doc)

# Optionally, print out the extracted content from each document
for document in docs:
    print(document.page_content)
