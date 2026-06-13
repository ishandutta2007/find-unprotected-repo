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
    progress_bar = st.progress(0)
    status_text = st.empty()
    results_container = st.container()
    
    unprotected_count = 0
    
    try:
        generator = find_unprotected_repos.find_unprotected_repos(ignore_forks=ignore_forks)
        
        for step in generator:
            # Update progress bar
            progress_bar.progress(step['current'] / step['total'])
            status_text.text(f"🔍 Scanning {step['current']}/{step['total']} repositories...")
            
            # If an unprotected repo is found, display it immediately
            if step['repo']:
                unprotected_count += 1
                repo = step['repo']
                with results_container:
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"### 📦 [{repo['full_name']}]({repo['html_url']})")
                            # st.link_button("🌐 Visit Repo", repo['html_url'])
                        with col2:
                            st.write("") # Spacer
                            st.write("") # Spacer
                            st.write(f"**Default Branch:** `{repo['default_branch']}`")
                        st.divider()
        
        if unprotected_count > 0:
            st.success(f"✅ Audit Complete! Found {unprotected_count} unprotected repository/repositories.")
        else:
            st.balloons()
            st.success("🎉 Audit Complete! All repositories have branch protection configured.")
            
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
