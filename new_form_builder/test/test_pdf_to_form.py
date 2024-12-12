import requests
file_path = 'new_form_builder/data/Overman register.pdf'
with open(file_path, 'rb') as f:
    response = requests.post(
        url='http://localhost:8000/ocr-form/',
        files={'file': f} 
    )

# Print the response from the server
print(response.text)
