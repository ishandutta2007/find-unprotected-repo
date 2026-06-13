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

# Custom CSS for modern aesthetics
st.markdown("""
<style>
    /* Main container styling */
    .main {
        background-color: transparent;
    }
    
    /* Header styling */
    .main-header {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        font-size: 3rem;
        margin-bottom: 0.5rem;
        background: linear-gradient(90deg, #58a6ff 0%, #238636 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .sub-header {
        color: #8b949e;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }

    /* Repo Card Styling */
    .repo-card {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 14px 20px;
        margin-bottom: 12px;
        background-color: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(128, 128, 128, 0.15);
        border-radius: 12px;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        text-decoration: none !important;
    }
    
    .repo-card:hover {
        transform: translateY(-2px);
        background-color: rgba(255, 255, 255, 0.05);
        border-color: rgba(88, 166, 255, 0.4);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }
    
    .repo-info {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .repo-icon {
        font-size: 1.2rem;
    }
    
    .repo-link {
        font-weight: 600;
        color: #58a6ff !important;
        text-decoration: none !important;
        font-size: 1.05rem;
    }
    
    .repo-link:hover {
        text-decoration: underline !important;
    }
    
    .branch-badge {
        background-color: rgba(128, 128, 128, 0.1);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
        color: #8b949e;
        border: 1px solid rgba(128, 128, 128, 0.1);
    }

    /* Primary button styling override if needed, but we'll use Streamlit's primary type */
</style>
""", unsafe_allow_html=True)

# Title and Description
st.markdown('<h1 class="main-header">🛡️ Unprotected Finder</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Automated security auditing for your GitHub repositories.</p>', unsafe_allow_html=True)

# Sidebar settings
st.sidebar.header("Settings")
st.sidebar.markdown("---")
ignore_forks = st.sidebar.checkbox("Ignore Forked Repositories", value=True)
ignore_private = st.sidebar.checkbox("Ignore Private Repositories", value=True)
st.sidebar.info("The cache will be used if a scan was performed within the last 25 hours.")

# Main Area
if st.button("🚀 Run Security Scan", type="primary", use_container_width=True):
    progress_bar = st.progress(0)
    status_text = st.empty()
    results_container = st.container()
    
    unprotected_count = 0
    
    try:
        generator = find_unprotected_repos.find_unprotected_repos(
            ignore_forks=ignore_forks, 
            ignore_private=ignore_private
        )
        
        for step in generator:
            # Update progress bar
            progress_bar.progress(step['current'] / step['total'])
            status_text.markdown(f"🔍 **Scanning:** `{step['current']}` / `{step['total']}` repositories... (⚠️ Unprotected: `{unprotected_count}`)")
            
            # If an unprotected repo is found, display it immediately
            if step['repo']:
                unprotected_count += 1
                repo = step['repo']
                with results_container:
                    # Create HTML for the modern card
                    card_html = f"""
                    <div class="repo-card">
                        <div class="repo-info">
                            <span class="repo-icon">📦</span>
                            <a href="{repo['html_url']}" target="_blank" class="repo-link">{repo['full_name']}</a>
                        </div>
                        <div class="repo-meta">
                            <span class="branch-badge">🏷️ {repo['default_branch']}</span>
                        </div>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)
        
        status_text.empty()
        if unprotected_count > 0:
            st.success(f"✅ Audit Complete! Found **{unprotected_count}** unprotected repository/repositories.")
        else:
            st.balloons()
            st.success("🎉 Audit Complete! All repositories have branch protection configured.")
            
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
        st.info("Make sure your `.env` file is configured with a valid `ADMIN_TOKEN`.")

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.divider()
st.markdown("""
<div align="center">
  <sub>Built with ❤️ for a safer GitHub ecosystem.</sub>
</div>
""", unsafe_allow_html=True)
