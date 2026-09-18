import streamlit as st
import time
import traceback
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from xml.sax.saxutils import escape
from io import BytesIO
import re

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

    # -----------------------------
    # PDF formatting helpers
    # -----------------------------
    def clean_pdf_text(text):
        text = text.replace("\u2011", "-")
        text = text.replace("\u2013", "-")
        text = text.replace("\u2014", "-")
        text = text.replace("\u2018", "'")
        text = text.replace("\u2019", "'")
        text = text.replace("\u201c", '"')
        text = text.replace("\u201d", '"')
        text = text.replace("\u00a0", " ")

        # Convert HTML line breaks
        text = re.sub(
            r"<br\s*/?>",
            "\n",
            text,
            flags=re.IGNORECASE
        )

        return text

    def markdown_to_pdf_elements(report, styles, doc):
        elements = []
        lines = report.split("\n")

        i = 0

        while i < len(lines):
            line = lines[i].strip()

            # Empty line
            if not line:
                elements.append(Spacer(1, 8))
                i += 1
                continue

            # -----------------------------
            # Markdown table
            # -----------------------------
            if line.startswith("|") and "|" in line:

                table_lines = []

                while (
                    i < len(lines)
                    and lines[i].strip().startswith("|")
                ):
                    table_lines.append(lines[i].strip())
                    i += 1

                table_data = []

                for table_line in table_lines:

                    # Skip Markdown separator row
                    if re.match(
                        r"^\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?$",
                        table_line
                    ):
                        continue

                    cells = [
                        cell.strip()
                        for cell in table_line.strip("|").split("|")
                    ]

                    formatted_cells = []

                    for cell in cells:
                        cell = clean_pdf_text(cell)
                        cell = escape(cell)

                        # Markdown bold
                        cell = re.sub(
                            r"\*\*(.*?)\*\*",
                            r"<b>\1</b>",
                            cell
                        )

                        # Markdown italic
                        cell = re.sub(
                            r"(?<!\*)\*(?!\*)(.*?)\*(?!\*)",
                            r"<i>\1</i>",
                            cell
                        )

                        formatted_cells.append(
                            Paragraph(
                                cell,
                                styles["BodyText"]
                            )
                        )

                    table_data.append(formatted_cells)

                if table_data:

                    column_count = len(table_data[0])

                    table = Table(
                        table_data,
                        colWidths=[
                            doc.width / column_count
                        ] * column_count,
                        repeatRows=1,
                    )

                    table.setStyle(
                        TableStyle([
                            (
                                "GRID",
                                (0, 0),
                                (-1, -1),
                                0.5,
                                colors.grey,
                            ),
                            (
                                "BACKGROUND",
                                (0, 0),
                                (-1, 0),
                                colors.lightgrey,
                            ),
                            (
                                "VALIGN",
                                (0, 0),
                                (-1, -1),
                                "TOP",
                            ),
                            (
                                "LEFTPADDING",
                                (0, 0),
                                (-1, -1),
                                6,
                            ),
                            (
                                "RIGHTPADDING",
                                (0, 0),
                                (-1, -1),
                                6,
                            ),
                            (
                                "TOPPADDING",
                                (0, 0),
                                (-1, -1),
                                6,
                            ),
                            (
                                "BOTTOMPADDING",
                                (0, 0),
                                (-1, -1),
                                6,
                            ),
                        ])
                    )

                    elements.append(table)
                    elements.append(Spacer(1, 12))

                continue

            # -----------------------------
            # Main heading
            # -----------------------------
            if line.startswith("# "):

                text = clean_pdf_text(line[2:])
                text = escape(text)

                elements.append(
                    Paragraph(
                        text,
                        styles["Heading1"]
                    )
                )

            # -----------------------------
            # Section heading
            # -----------------------------
            elif line.startswith("## "):

                text = clean_pdf_text(line[3:])
                text = escape(text)

                elements.append(
                    Paragraph(
                        text,
                        styles["Heading2"]
                    )
                )

            # -----------------------------
            # Subsection heading
            # -----------------------------
            elif line.startswith("### "):

                text = clean_pdf_text(line[4:])
                text = escape(text)

                elements.append(
                    Paragraph(
                        text,
                        styles["Heading3"]
                    )
                )

            # -----------------------------
            # Horizontal rule
            # -----------------------------
            elif line in ["---", "***", "___"]:

                elements.append(
                    Spacer(1, 5)
                )

            # -----------------------------
            # Normal paragraph
            # -----------------------------
            else:

                text = clean_pdf_text(line)
                text = escape(text)

                # Markdown bold
                text = re.sub(
                    r"\*\*(.*?)\*\*",
                    r"<b>\1</b>",
                    text
                )

                # Markdown italic
                text = re.sub(
                    r"(?<!\*)\*(?!\*)(.*?)\*(?!\*)",
                    r"<i>\1</i>",
                    text
                )

                elements.append(
                    Paragraph(
                        text,
                        styles["BodyText"]
                    )
                )

            elements.append(Spacer(1, 8))

            i += 1

        return elements

    # -----------------------------
    # Final Report
    # -----------------------------
    with tab1:

        report = get_content(result.get("report"))

        if report:

            st.markdown(report)

            # Create professional PDF
            pdf_buffer = BytesIO()

            doc = SimpleDocTemplate(
                pdf_buffer,
                pagesize=letter,
                rightMargin=50,
                leftMargin=50,
                topMargin=50,
                bottomMargin=50,
            )

            styles = getSampleStyleSheet()

            styles["Title"].fontSize = 24
            styles["Title"].leading = 28
            styles["Title"].spaceAfter = 20

            styles["Heading1"].fontSize = 18
            styles["Heading1"].leading = 22
            styles["Heading1"].spaceBefore = 12
            styles["Heading1"].spaceAfter = 10

            styles["Heading2"].fontSize = 15
            styles["Heading2"].leading = 19
            styles["Heading2"].spaceBefore = 10
            styles["Heading2"].spaceAfter = 8

            styles["Heading3"].fontSize = 13
            styles["Heading3"].leading = 17
            styles["Heading3"].spaceBefore = 8
            styles["Heading3"].spaceAfter = 6

            styles["BodyText"].fontSize = 10
            styles["BodyText"].leading = 15

            story = []

            story.append(
                Paragraph(
                    "Multi-Agent Research Report",
                    styles["Title"]
                )
            )

            story.append(Spacer(1, 10))

            story.extend(
                markdown_to_pdf_elements(
                    report,
                    styles,
                    doc
                )
            )

            doc.build(story)

            st.download_button(
                "⬇️ Download Report",
                pdf_buffer.getvalue(),
                file_name="research_report.pdf",
                mime="application/pdf",
            )

        else:
            st.info("No final report was returned.")

    # -----------------------------
    # Critic Feedback
    # -----------------------------
    with tab2:

        feedback = get_content(result.get("feedback"))

        if feedback:
            st.markdown(feedback)
        else:
            st.info("No critic feedback was returned.")

    # -----------------------------
    # Search Results
    # -----------------------------
    with tab3:

        search_results = get_content(
            result.get("search_results")
        )

        if search_results:
            st.text_area(
                "Search Results",
                search_results,
                height=500,
            )
        else:
            st.info("No search results were returned.")

    # -----------------------------
    # Scraped Content
    # -----------------------------
    with tab4:

        scraped_content = get_content(
            result.get("scraped_content")
        )

        if scraped_content:
            st.text_area(
                "Scraped Content",
                scraped_content,
                height=500,
            )
        else:
            st.info("No scraped content was returned.")