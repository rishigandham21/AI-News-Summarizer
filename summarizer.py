from transformers import pipeline

# Load local summarization model once
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_text(text, max_length=60):
    """
    Return a short summary of given text.
    """
    result = summarizer(text, max_length=max_length, min_length=20, do_sample=False)
    return result[0]['summary_text']
