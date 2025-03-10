import os
from dotenv import load_dotenv
load_dotenv()
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_community.document_loaders import YoutubeLoader, UnstructuredURLLoader
from langchain.chains.summarize import load_summarize_chain
import validators

# LLM Model
# os.environ['HF_TOKEN'] = os.getenv("HF_TOKEN")
# groq_api_key = os.getenv("GROQ_API_KEY")
# llm = ChatGroq(api_key=groq_api_key, model="gemma2-9b-it")

# Langsmith tracking

os.environ["LANGCHAIN_API_KEY"]= st.secrets["LANGCHAIN_API_KEY"]
os.environ["LANGCHAIN_PROJECT"] = st.secrets["LANGCHAIN_PROJECT"]
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGSMITH_ENDPOINT"]="https://api.smith.langchain.com"

st.title("Summarize YouTube Video")
st.subheader("Enter URL")

st.sidebar.title("Settings")
api_key = st.sidebar.text_input("Enter your API key", type='password')
model = st.sidebar.selectbox("Select Model", ["gemma2-9b-it", "llama3-70b-8192", "distil-whisper-large-v3-en"], index=0)


summary_prompts = {
    "Key Points": '''
        Provide a detailed summary of the following content, in a proper format highlighting the main ideas or takeaways. Use `Key Points` as the header. Maximum 500 words.
        Content: {text}
    ''',
    "Narrative": '''
        Provide a detailed narrative summary of the following content, in a proper format. Use `Narrative Summary` as the header. Describe the content from beginning to end. Maximum 500 words.
        Content: {text}
    ''',
    "Analytical": '''
        Provide a detailed analytical summary of the following content, formatted in Markdown under the header `# Analytical Summary`. Summarize the main content and include brief insights or evaluations of the ideas presented, using subheaders (`##`) for key sections if needed.
        Content: {text}
    ''',
    "Step-by-Step": '''
        Provide a detailed step-by-step summary of the following content, formatted in Markdown as a numbered list under the header `# Step-by-Step Summary`. Break down any processes or instructions into a clear sequence.
        Content: {text}
    ''',
    "Thematic": '''
        Provide a detailed thematic summary of the following content, formatted in Markdown under the header `# Thematic Summary`. Identify and group the content into 3-5 major themes or topics, using subheaders (`##`) for each theme with detailed explanations.
        Content: {text}
    ''',
    "Highlights": '''
        Provide a detailed highlights summary of the following content, formatted in Markdown as a bulleted list under the header `# Highlights`. Focus on the most memorable, surprising, or impactful moments, described in a casual tone.
        Content: {text}
    ''',
    "Q&A": '''
        Provide a detailed Q&A summary of the following content, formatted in Markdown under the header `# Q&A Summary`. Include 4-6 key questions viewers might have as subheaders (`##`), with detailed answers based on the content.
        Content: {text}
    ''',
    "Quote-Based": '''
        Provide a detailed quote-based summary of the following content, formatted in Markdown under the header `# Quote-Based Summary`. Select 4-6 key verbatim quotes that capture its essence, presented as a bulleted list with minimal additional explanation.
        Content: {text}
    '''
}


generic_url = st.text_input("Enter URL", label_visibility='collapsed')
# Dropdown for summary types
summary_type = st.selectbox(
    "Select Summary Type",
    ["Key Points", "Narrative", "Analytical", "Step-by-Step", "Thematic", "Highlights", "Q&A", "Quote-Based"],
    index=0
)

# Select the prompt based on the chosen summary type
prompt_template = summary_prompts[summary_type]
prompt = PromptTemplate(input_variables=['text'], template=prompt_template)


if st.button("Summarize"):
    if not api_key.strip() or not generic_url.strip():
        st.error("Please enter required information")

    elif not validators.url(generic_url):
        st.error("Please enter a valid YouTube URL")

    else:
        if api_key=="samarth":
            llm = ChatGroq(model=model, api_key=st.secrets["GROQ_API_KEY"])
        else : 
            llm = ChatGroq(model=model, api_key=api_key)
        try:
            with st.spinner("Waiting...."):
                if "youtube.com" in generic_url:
                    loader = YoutubeLoader.from_youtube_url(generic_url, add_video_info=False)
                else:
                    st.error("Please check the link you have entered")

                docs = loader.load()
                chain = load_summarize_chain(llm=llm, chain_type='stuff', prompt=prompt)
                output_summary = chain.invoke(docs)

                # st.success(output_summary)
                st.write(output_summary.get('output_text', str(output_summary)))

        except Exception as e:
            st.exception(f"Something is not right, {e}")