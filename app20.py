import streamlit as st
import requests
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup


# Streamlit setup
st.set_page_config(page_title="LeetCode & Kaggle Reviewer", layout="centered")
st.title("🧠 LeetCode & Kaggle Profile Reviewer")

leetcode_username = st.text_input("Enter your LeetCode username")
kaggle_username = st.text_input("Enter your Kaggle username")

# ----- LeetCode Function -----
def fetch_leetcode_profile(username):
    url = "https://leetcode.com/graphql"
    query = {
        "operationName": "getUserProfile",
        "variables": {"username": username},
        "query": """
        query getUserProfile($username: String!) {
            matchedUser(username: $username) {
                username
                profile {
                    realName
                    ranking
                    userAvatar
                }
                submitStats {
                    acSubmissionNum {
                        difficulty
                        count
                    }
                }
            }
        }
        """
    }

    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, data=json.dumps(query))

    if response.status_code == 200:
        user_data = response.json().get("data", {}).get("matchedUser")
        if user_data:
            submissions = user_data["submitStats"]["acSubmissionNum"]
            total_solved = next((item["count"] for item in submissions if item["difficulty"] == "All"), 0)

            return {
                "username": user_data["username"],
                "realName": user_data["profile"]["realName"],
                "ranking": user_data["profile"]["ranking"],
                "totalSolved": total_solved,
            }
    return None

# ----- Kaggle Function (Web Scraping with Selenium) -----
def fetch_kaggle_profile(username):
    try:
        url = f"https://www.kaggle.com/{username}"
        response = requests.get(url)
        
        if response.status_code != 200:
            return {"error": "User not found or page not accessible."}

        # Use BeautifulSoup to scrape the name
        soup = BeautifulSoup(response.text, "html.parser")

        return {
            "username": username,
            "datasetLink": f"https://www.kaggle.com/{username}/datasets",
            "notebookLink": f"https://www.kaggle.com/{username}/code",
            "discussionLink": f"https://www.kaggle.com/{username}/discussion",
        }
    except Exception as e:
        return {"error": f"Failed to fetch profile: {str(e)}"}


# ----- Show LeetCode Result -----
if leetcode_username:
    st.subheader("🔍 LeetCode Review")
    leet_data = fetch_leetcode_profile(leetcode_username)
    if leet_data:
        st.markdown(f"**Name**: {leet_data['realName'] or 'N/A'}")
        st.markdown(f"**Username**: {leet_data['username']}")
        st.markdown(f"**Ranking**: {leet_data['ranking']}")
        st.markdown(f"**Problems Solved**: {leet_data['totalSolved']}")
    else:
        st.error("❌ Couldn't fetch LeetCode profile. Please check the username.")

# ----- Show Kaggle Result -----
if kaggle_username:
    st.subheader("🔍 Kaggle Review")
    kaggle_data = fetch_kaggle_profile(kaggle_username)
    if kaggle_data and "error" not in kaggle_data:
        st.markdown(f"**Username**: {kaggle_data['username']}")
        st.markdown(f"[📊 View Datasets]({kaggle_data['datasetLink']})")
        st.markdown(f"[📓 View Notebooks]({kaggle_data['notebookLink']})")
        st.markdown(f"[💬 View Discussions]({kaggle_data['discussionLink']})")
    else:
        st.error(kaggle_data.get("error", "❌ Couldn't fetch Kaggle profile."))

