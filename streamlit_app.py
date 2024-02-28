import streamlit as st
from transformers import GPT2Tokenizer, GPT2LMHeadModel
import torch
import nltk
from nltk.util import ngrams
from nltk.lm.preprocessing import pad_sequence
from nltk.probability import FreqDist
import plotly.express as px
from collections import Counter
from nltk.corpus import stopwords
import string

nltk.download('punkt')
nltk.download('stopwords')
tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
model = GPT2LMHeadModel.from_pretrained('gpt2')
min_perplexity = 0
max_perplexity = 60000
min_burstiness = 0
max_burstiness = 1 

def calculate_perplexity(text):
    encoded_input = tokenizer.encode(text, add_special_tokens=False, return_tensors='pt')
    input_ids = encoded_input[0]

    with torch.no_grad():
        outputs = model(input_ids)
        logits = outputs.logits

    perplexity = torch.exp(torch.nn.functional.cross_entropy(logits.view(-1, logits.size(-1)), input_ids.view(-1)))
    return perplexity.item()

def calculate_burstiness(text):
    tokens = nltk.word_tokenize(text.lower())
    word_freq = FreqDist(tokens)
    repeated_count = sum(count > 1 for count in word_freq.values())
    burstiness_score = repeated_count / len(word_freq)
    return burstiness_score

def plot_top_repeated_words(text):
    # Tokenize the text and remove stopwords and special characters
    tokens = text.split()
    stop_words = set(stopwords.words('english'))
    tokens = [token.lower() for token in tokens if token.lower() not in stop_words and token.lower() not in string.punctuation]

    # Count the occurrence of each word
    word_counts = Counter(tokens)

    # Get the top 10 most repeated words
    top_words = word_counts.most_common(10)

    # Extract the words and their counts for plotting
    words = [word for word, count in top_words]
    counts = [count for word, count in top_words]

    # Plot the bar chart using Plotly
    fig = px.bar(x=words, y=counts, labels={'x': 'Words', 'y': 'Counts'}, title='Top 10 Most Repeated Words')
    st.plotly_chart(fig, use_container_width=True)

st.set_page_config(layout="wide")

st.title("GPT Shield: AI Plagiarism Detector")
text_area = st.text_area("Enter text", "")

if text_area is not None:
    if st.button("Analyze"):
        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            st.info("Your Input Text")
            st.success(text_area)
        
        with col2:
            st.info("Detection Score")
            perplexity = calculate_perplexity(text_area)
            burstiness_score = calculate_burstiness(text_area)
            ai_percentage = ((perplexity - min_perplexity) / (max_perplexity - min_perplexity)) * ((max_burstiness - burstiness_score) / (max_burstiness - min_burstiness)) * 100


            st.write("Perplexity:", perplexity)
            st.write("Burstiness Score:", burstiness_score)
            st.write("Percentage of being generated by AI:", ai_percentage, "%")
            
            if ai_percentage > 75:
                st.error("Text Analysis Result: Highly likely AI generated content")
            elif ai_percentage > 50:
                st.warning("Text Analysis Result: Moderately likely AI generated content")
            else:
                st.success("Text Analysis Result: Likely not generated by AI")

            
        with col3:
            st.info("Basic Details")
            plot_top_repeated_words(text_area)

