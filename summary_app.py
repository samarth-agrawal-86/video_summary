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

st.title("Summarize YouTube Video or Website text")
st.subheader("Summarize URL")

st.sidebar.title("Settings")
api_key = st.sidebar.text_input("Enter your API key", type='password')
model = st.sidebar.selectbox("Select Model", ["gemma2-9b-it", "llama3-70b-8192", "distil-whisper-large-v3-en"], index=0)


prompt_template = '''
Provide a summary of the following content in 300 words.
Content : 
{text}
'''

prompt = PromptTemplate(input_variables=['text'], template=prompt_template)

generic_url = st.text_input("Enter URL", label_visibility='collapsed')

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

                st.success(output_summary)

        except Exception as e:
            st.exception(f"Something is not right, {e}")