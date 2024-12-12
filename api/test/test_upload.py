import requests

def test_upload_file():
    # URL of the FastAPI server
    url = "http://127.0.0.1:8000/upload"  # Change this to your running server's URL if different

    # Path to a sample file for testing (replace with your file path)
    file_path = "data/raw/smp2.pdf"  # Ensure the file exists in the directory

    # Open the file in binary mode
    with open(file_path, "rb") as file:
        # Send POST request with file
        response = requests.post(
            url,
            files={"file": (file_path, file, "application/pdf")},
        )

    # Print the response
    print("Status Code:", response.status_code)
    print("Response Content:", response.json())

if __name__ == "__main__":
    test_upload_file()
