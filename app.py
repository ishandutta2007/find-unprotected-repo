import streamlit as st
import find_unprotected_repos
import sys
import io

# Page Configuration
st.set_page_config(
    page_title="GitHub Unprotected Repo Finder",
    page_icon="🛡️",
    layout="wide"
)

# Title and Description
st.title("🛡️ GitHub Repository Branch Protection Checker")
st.markdown("""
This tool scans your GitHub repositories to identify those that lack branch protection rules.
Click **Run Scan** below to start the audit.
""")

# Sidebar settings
st.sidebar.header("Settings")
ignore_forks = st.sidebar.checkbox("Ignore Forked Repositories", value=True)

# Main Area
if st.button("🚀 Run Scan"):
    with st.spinner("🔍 Auditing repositories... (This may take a minute)"):
        try:
            # Capture tqdm output (stderr) if we want to show it in Streamlit, 
            # but for simplicity we'll just run the logic and show results.
            unprotected_repos = find_unprotected_repos.find_unprotected_repos(ignore_forks=ignore_forks)
            
            if unprotected_repos:
                st.success(f"✅ Found {len(unprotected_repos)} unprotected repository/repositories!")
                
                # Display results in a nice layout
                for repo in unprotected_repos:
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"### 📦 [{repo['full_name']}]({repo['html_url']})")
                            st.write(f"**URL:** {repo['html_url']}")
                            st.write(f"**Default Branch:** `{repo['default_branch']}`")
                        with col2:
                            st.write("") # Spacer
                            st.write("") # Spacer
                            st.link_button("🌐 Visit Repo", repo['html_url'])
                        st.divider()
            else:
                st.balloons()
                st.success("🎉 All repositories have branch protection configured!")
                
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            st.info("Make sure your `.env` file is configured with a valid `ADMIN_TOKEN`.")

# Footer
st.divider()
st.markdown("""
<div align="center">
  <sub>Built with ❤️ for a safer GitHub ecosystem.</sub>
</div>
""", unsafe_allow_html=True)
