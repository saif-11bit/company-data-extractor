import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

def clean_html(raw_html):
    # Using BeautifulSoup to clean HTML tags
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text(separator="\n").strip()

session = requests.Session()

# Make an initial request to capture cookies
response = session.get('https://www.ambitionbox.com/')
headers = {}
headers["User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
headers["accept"] = "*/*"
headers["accept-encoding"] = "gzip, deflate, br, zstd"
headers["accept-language"] = "en-GB,en-US;q=0.9,en;q=0.8"
headers["cache-control"] = "no-cache"

def fetch_company_data(company_name):
    print("running")
    """Fetch company data from an external source."""
    company_name = company_name.lower().replace(" ", "-")
    AMBITION_BOX_URI = f"https://www.ambitionbox.com/_next/data/HK3rQbSwgvzPDSMVXAAfT/overview/{company_name}-overview.json"
    response = session.get(AMBITION_BOX_URI, headers=headers)
    data = {}
    if response.status_code == 200:
        response = response.json()
        for k, v in response["pageProps"].items():
            if k in ["companyMetaInformation", "benefits", "companyHeaderData", "interviewsData", "salariesList", "photosData", "jobsData", "faqs", "aggregatedRatingsData", "officeLocations", "similarCompanies"]:
                data[k] = v
        return data, True
    else:
        return data, False

def display_company_data(data):
    """Display the company data in the Streamlit app."""
    meta_info = data.get('companyMetaInformation', {})
    st.header(f"Company Overview: {meta_info.get('companyName', 'N/A')}")

    # Display basic company info with checks for missing data
    st.markdown(f"""
    - **Name**: {meta_info.get('companyName', 'N/A')}
    - **Description**: {meta_info.get('description', 'N/A')}
    - **Website**: [{meta_info.get('websiteName', 'N/A')}]({meta_info.get('website', '#')})
    - **CEO**: {meta_info.get('ceo', 'N/A')}
    - **Founded Year**: {meta_info.get('foundedYear', 'N/A')}
    - **Global Employee Count**: {meta_info.get('globalEmployeeCount', 'N/A')}
    - **Type of Company**: {', '.join([type['name'] for type in meta_info.get('typeOfCompany', [])]) or 'N/A'}
    - **Ownership**: {meta_info.get('ownership', {}).get('name', 'N/A')}
    """)

    st.subheader("Social Media Links")
    social_links = meta_info.get('socialLinks', {})
    if social_links:
        for platform, url in social_links.items():
            if url:
                st.markdown(f"- [{platform.capitalize()}]({url})")
    else:
        st.write("No social media links available.")

    # Display company ratings
    st.subheader("Company Ratings")
    ratings_data = data.get('aggregatedRatingsData', {}).get('ratingDistribution', {}).get('data', {}).get('ratings', {})
    if ratings_data:
        st.write(pd.DataFrame.from_dict(ratings_data, orient='index', columns=['Rating']))
    else:
        st.write("No ratings data available.")

    # Interview data
    st.subheader("Interview Insights")
    interview_data = data.get('interviewsData', {})
    if interview_data:
        st.write(f"Total Interview Count: {interview_data.get('interviewRoundsData', {}).get('Meta', {}).get('InterviewCount', 'N/A')}")
        st.write("Interview Duration:")
        st.write(pd.DataFrame(interview_data.get('interviewRoundsData', {}).get('Duration', [])))
        st.write("Difficulty Levels:")
        st.write(pd.DataFrame(interview_data.get('interviewRoundsData', {}).get('Difficulty', [])))
    else:
        st.write("No interview insights available.")

    # Display job details
    st.subheader("Job Listings")
    jobs_data = data.get('jobsData', {}).get('data', {}).get('Jobs', [])
    if jobs_data:
        job_listings = pd.DataFrame(jobs_data)
        st.dataframe(job_listings[['Title', 'Locations', 'MinExp', 'MaxExp', 'Skills', 'PostedOn']], width=700)
    else:
        st.write("No job listings available.")

    # Salary insights
    st.subheader("Salary Insights")
    salaries = data.get('salariesList', {}).get('designations', {}).get('jobProfiles', [])
    if salaries:
        salary_df = pd.DataFrame(salaries)
        st.dataframe(salary_df[['jobProfileName', 'minExperience', 'maxExperience', 'minCtc', 'maxCtc', 'avgCtc']], width=700)
    else:
        st.write("No salary insights available.")

    # Work policy distribution
    st.subheader("Work Policy Distribution")
    work_policy = data.get('aggregatedRatingsData', {}).get('workPolicyDistribution', {}).get('data', {}).get('workPolicyList', [])
    if work_policy:
        st.write(pd.DataFrame(work_policy))
    else:
        st.write("No work policy distribution data available.")

    # Gender insights
    st.subheader("Gender Insights")
    gender_insights = data.get('aggregatedRatingsData', {}).get('genderInsights', {}).get('data', {})
    if gender_insights:
        st.write("Male:")
        st.write(pd.DataFrame(gender_insights.get('M', {}).get('topRatings', [])))
        st.write("Female:")
        st.write(pd.DataFrame(gender_insights.get('F', {}).get('topRatings', [])))
    else:
        st.write("No gender insights available.")

    # Employee benefits
    st.subheader("Employee Benefits")
    benefits = data.get('benefits', {}).get('benefits', [])
    if benefits:
        st.dataframe(pd.DataFrame(benefits)[['name', 'count']], width=500)
    else:
        st.write("No employee benefits data available.")

    # Display office photos
    st.subheader("Company Photos")
    photos = data.get('photosData', {}).get('data', {}).get('Photos', [])
    if photos:
        for photo in photos:
            st.image(photo.get('Url'), caption=photo.get('Caption', ''))
    else:
        st.write("No company photos available.")

    # FAQs section
    st.subheader("Frequently Asked Questions")
    faqs = data.get('faqs', [])
    if faqs:
        for faq in faqs:
            with st.expander(faq.get('question', 'N/A')):
                st.write(clean_html(faq.get('answer', 'N/A')))
    else:
        st.write("No FAQs available.")


def main():
    # Load local data for backup (optional)
    # local_data = load_json_data()

    # Streamlit app title
    st.title("Company Overview Finder")

    # Input field for company name
    input_company = st.text_input("Enter the company name:", "")
    # Button to trigger the search
    if st.button("Search"):
        if input_company:
            data, success = fetch_company_data(input_company.strip())

            if success:
                # Display company data if found
                display_company_data(data)
            else:
                st.write("Company not found or data unavailable.")
                # Optional: Display local backup data if needed
                # display_company_data(local_data)
        else:
            st.write("Please enter a company name to search.")
# Run the main function
if __name__ == "__main__":
    main()
