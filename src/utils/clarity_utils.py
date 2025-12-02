import streamlit as st


def init_clarity(project_id: str):
    """
    Initialize Microsoft Clarity analytics in the Streamlit app.
    
    Args:
        project_id: Your Microsoft Clarity project ID (found in Clarity dashboard)
    
    Usage:
        from src.utils.clarity_utils import init_clarity
        init_clarity("your-project-id")
    """
    if not project_id:
        return
    
    # Microsoft Clarity script tag - inject directly into the page HTML
    clarity_script = f"""
    <script type="text/javascript">
        (function(c,l,a,r,i,t,y){{
            c[a]=c[a]||function(){{(c[a].q=c[a].q||[]).push(arguments)}};
            t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
            y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
        }})(window, document, "clarity", "script", "{project_id}");
    </script>
    """
    
    # Inject the script into the page using markdown with unsafe HTML
    st.markdown(clarity_script, unsafe_allow_html=True)

