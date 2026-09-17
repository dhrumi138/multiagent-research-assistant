import streamlit as st
import time
import traceback
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

from pipeline import run_research_pipeline

st.set_page_config(
    page_title="Multi-Agent Research Assistant",
    page_icon="🔎",
    layout="wide",
)

st.title("🔎 Multi-Agent Research Assistant")
st.caption("Search → Read → Write → Critique")

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.header("Research Agent")
 
    st.divider()
    st.write("**Pipeline**")
    st.write("1. 🔍 Search Agent")
    st.write("2. 📖 Reader Agent")
    st.write("3. ✍️ Writer Chain")
    st.write("4. 🧐 Critic Chain")

# -----------------------------
# Input
# -----------------------------
topic = st.text_input(
    "Enter a research topic",
    placeholder="e.g. Impact of Generative AI on software development",
)

run_button = st.button("🚀 Run Research", type="primary", use_container_width=True)

# -----------------------------
# Run pipeline
# -----------------------------
if run_button:
    if not topic.strip():
        st.warning("Please enter a research topic.")
    else:
        start_time = time.time()

        try:
            with st.status(
                "Running multi-agent research pipeline...",
                expanded=True,
            ) as status:

                st.write("🔍 Running search agent...")
                result = run_research_pipeline(topic.strip())

                status.update(
                    label="✅ Research completed",
                    state="complete",
                    expanded=False,
                )

            elapsed = time.time() - start_time

            st.success(f"Research completed in {elapsed:.1f} seconds.")

            # Save result so it remains visible after Streamlit reruns
            st.session_state["result"] = result
            st.session_state["topic"] = topic.strip()

        except Exception as e:
            st.error(f"Pipeline error: {e}")

            with st.expander("Show full error"):
                st.code(traceback.format_exc())

# -----------------------------
# Display result
# -----------------------------
if "result" in st.session_state:
    result = st.session_state["result"]
    topic = st.session_state["topic"]

    st.divider()
    st.header(f"Research Results: {topic}")

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "📄 Final Report",
            "🧐 Critic Feedback",
            "🔍 Search Results",
            "📖 Scraped Content",
        ]
    )

    def get_content(value):
        if value is None:
            return ""

        if isinstance(value, str):
            return value

        if hasattr(value, "content"):
            return value.content

        return str(value)

    with tab1:
        report = get_content(result.get("report"))

        if report:
            st.markdown(report)

            # Create a real PDF
            pdf_buffer = BytesIO()

            doc = SimpleDocTemplate(
                pdf_buffer,
                pagesize=letter
            )

            styles = getSampleStyleSheet()
            story = []

            story.append(
                Paragraph(
                    "Multi-Agent Research Report",
                    styles["Title"]
                )
            )

            story.append(Spacer(1, 20))

            for paragraph in report.split("\n"):
                if paragraph.strip():
                    story.append(
                        Paragraph(
                            paragraph.replace("&", "&amp;"),
                            styles["BodyText"]
                        )
                    )
                    story.append(Spacer(1, 8))

            doc.build(story)

            st.download_button(
                "⬇️ Download Report",
                pdf_buffer.getvalue(),
                file_name="research_report.pdf",
                mime="application/pdf",
            )

        else:
            st.info("No final report was returned.")

    with tab2:
        feedback = get_content(result.get("feedback"))

        if feedback:
            st.markdown(feedback)
        else:
            st.info("No critic feedback was returned.")

    with tab3:
        search_results = get_content(result.get("search_results"))

        if search_results:
            st.text_area(
                "Search Results",
                search_results,
                height=500,
            )
        else:
            st.info("No search results were returned.")

    with tab4:
        scraped_content = get_content(result.get("scraped_content"))

        if scraped_content:
            st.text_area(
                "Scraped Content",
                scraped_content,
                height=500,
            )
        else:
            st.info("No scraped content was returned.")