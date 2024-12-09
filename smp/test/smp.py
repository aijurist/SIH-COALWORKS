from smp.core.smp import HazardAnalysisChain
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    analysis_chain = HazardAnalysisChain(GOOGLE_API_KEY)
    activity_name = "Blasting Operations"
    input_info = "In a meet conducted before, it was discussed that there were several dead in the past due to improper safety during blasting"
    result = analysis_chain.perform_hazard_analysis(activity_name=activity_name, input_info=input_info)
    print(result)

if __name__ == "__main__":
    main()