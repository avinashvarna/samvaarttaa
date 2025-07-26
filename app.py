import streamlit as st
from google import genai
from google.genai import types
import pyperclip

client = genai.Client(api_key=st.secrets["gemini_api_key"])

SYSTEM_INSTRUCTION = """Rewrite this news article into classical Sanskrit without English punctuation 
    or foreign letters like ऑ and with moderate sandhi but proper rules applied. 
    A direct translation is not required; instead, provide an original composition 
    that conveys the facts and details in an informative, engaging, fun-to-read, 
    and easy-to-understand manner, following classical Sanskrit style. 
    You may add additional context or gentle humor, or view of the shastras (with correct references), 
    but ensure accuracy and avoid altering the core facts (like quotes of people). 
    Carefully recheck the output for grammatical accuracy (correct case endings, verb conjugations, 
    and sandhi rules) and stylistic consistency before finalizing. Write surnames before names 
    and ensure proper sandhi all throughout the name. (e.g. शर्मरोहितः)
    Similarly write english name in devanagari with original name in brackets (e.g. काविन्डीस्येक्ष् (CoinDCX))

    Provide just the translation without any other extra introductory text.
    """

DEMO_INPUT = """On July 19, 2025, CoinDCX, one of India’s largest crypto exchanges, 
suffered a major hack resulting in a loss of about $44.2 million. The breach 
targeted an internal wallet used by CoinDCX for liquidity with a partner exchange 
and did not affect any customer funds, which remain safe in cold storage. 
Blockchain investigators like ZachXBT uncovered the hack before CoinDCX 
made it public, noting the hacker used a sophisticated server-side attack 
and laundered the funds by moving them from Solana to Ethereum and using 
Tornado Cash. CoinDCX has drawn some criticism for a 17-hour delay in disclosing 
the breach, especially since the compromised wallet was not part of the exchange’s 
published proof-of-reserves. In response, the company froze all impacted systems, 
engaged third-party security experts, and has covered the losses using its own 
treasury to ensure normal trading and withdrawals. CEO Sumit Gupta assured users 
that all customer holdings are safe, and the company has launched a bug bounty 
to strengthen future security while cooperating with authorities. This incident, 
the second major Indian exchange hack within a year, has intensified scrutiny on 
how centralized crypto platforms handle security and crisis management."""

if "output" not in st.session_state:
    st.session_state.output = None

# Cache API responses
@st.cache_data
def generate_sanskrit_translation(input_text, system_instruction):
    api_response = client.models.generate_content(
        model="gemini-2.5-pro",
        config=types.GenerateContentConfig(system_instruction=system_instruction),
        contents=input_text,
    )
    parts = api_response.candidates[0].content.parts
    return "".join(part.text for part in parts)

st.title("संवार्त्ता")
st.markdown(
    """
    ### Disclaimers: 
      * AI translation may contain errors or hallucinations. __*Always proofread*__ before publishing.
      * Generating the response *will* be slow. Please be patient!
      * Please note that this demo supports a limited number of requests and may be unavailable 
      if too many people use the service. Thank you for your understanding.
"""
)

# Collapsible prompt section
with st.expander("View Prompt (Non-editable)"):
    st.markdown(
        "Feel free to copy the prompt and experiment with it at "
        "[Google AI studio](https://aistudio.google.com/prompts/new_chat):"
        )
    st.markdown(SYSTEM_INSTRUCTION)

# Input form
with st.form("input_form"):
    st.write("Enter a detailed news article for best results. "
        "To reiterate -  __*Always proofread*__ before publishing, "
        "as it might contain errors or hallucinations (i.e. made-up facts)."
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.form_submit_button("Paste", icon=":material/content_paste:"):
            try:
                pasted_text = pyperclip.paste()
                st.session_state.input_text = pasted_text
            except Exception as e:
                st.error("Failed to paste text. Please try again or paste manually.", icon="🚨")
    with col2:
        if st.form_submit_button("Clear"):
            st.session_state.input_text = ""
            st.session_state.output = None
    with col3:
        if st.form_submit_button("Load Demo Article"):
            st.session_state.input_text = DEMO_INPUT

    input_text = st.text_area("Enter article below",
        height="stretch",
    )

    st.write(f"Input character count: {len(input_text)}")
    if len(input_text) > 5000:
        st.warning("Input is very long. Consider shortening it for better performance.")

    submitted = st.form_submit_button("Submit")

if submitted:
    if not input_text.strip():
        st.error("Please enter a valid news article.")
    try:
        with st.spinner("Generating Sanskrit translation... Please wait."):
            response = generate_sanskrit_translation(input_text, SYSTEM_INSTRUCTION)
        st.session_state.output = response
    except Exception as e:
        st.error(f"Error generating translation: {str(e)}")
        if "rate limit" in str(e).lower():
            st.warning("Rate limit exceeded. Please try again later, as this demo supports a limited number of requests.")

# Display output if available
if st.session_state.output:
    st.markdown("### Output")
    st.markdown(st.session_state.output)
    
    col1, col2 = st.columns(2)
    with col1:
        # Copy button
        if st.button("Copy Output"):
            try:
                pyperclip.copy(st.session_state.output)
                st.success("Output copied to clipboard!")
            except Exception as e:
                st.error("Failed to copy text. Please try again or copy manually.")
    
    with col2:
        # Download button
        st.download_button(
            label="Download Output",
            data=st.session_state.output,
            file_name="sanskrit_translation.txt",
            mime="text/plain",
            icon=":material/download:"
        )