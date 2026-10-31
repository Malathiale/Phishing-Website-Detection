
import streamlit as st
import pandas as pd
import joblib
import re
import math
from collections import Counter
from urllib.parse import urlparse
import matplotlib.pyplot as plt
import seaborn as sns
import os
import ipaddress

# Page configuration
st.set_page_config(
    page_title="PhishGuard AI",
    page_icon="🛡️",
    layout="wide"
)


# Load saved model and metrics
@st.cache_resource
def load_model():
    model = joblib.load("models/phishing_model.pkl")
    features = joblib.load("models/features.pkl")
    metrics = joblib.load("models/metrics.pkl")
    return model, features, metrics


# Extract URL features
def extract_features(url):

    if not re.match(r"^https?://", url, re.I):
        url = "http://" + url

    parsed = urlparse(url)

    hostname = parsed.hostname or ""
    path = parsed.path or ""
    query = parsed.query or ""

    domain_parts = hostname.split(".")
    tld = domain_parts[-1] if domain_parts else ""

    special_chars = sum(not char.isalnum() for char in url)

    trusted_tlds = ["com", "org", "net", "edu", "gov"]

    entropy = 0
    if url:
        counts = Counter(url)
        entropy = -sum(
            (count / len(url)) * math.log2(count / len(url))
            for count in counts.values()
        )

    try:
        ipaddress.ip_address(hostname)
        is_ip = 1
    except ValueError:
        is_ip = 0

    return {
        "url_length": len(url),
        "hyphen_count": url.count("-"),
        "digit_count": sum(c.isdigit() for c in url),
        "subdomain_count": max(len(domain_parts) - 2, 0),
        "trusted_tld": int(tld.lower() in trusted_tlds),
        "protocol_exists": int(parsed.scheme in ["http", "https"]),
        "special_char_count": special_chars,
        "entropy": entropy,
        "path_depth": len([p for p in path.split("/") if p]),
        "domain_length": len(hostname),
        "is_domain_ip": is_ip,
        "has_at_symbol": int("@" in url),
        "has_double_slash_redirect": int("//" in path),
        "tld_length": len(tld),
        "query_param_count": len(query.split("&")) if query else 0,
        "path_length": len(path)
    }


# Sidebar
st.sidebar.title("🛡️ PhishGuard AI")

page = st.sidebar.radio(
    "Navigation",
    ["Website Scanner", "Model Performance", "About Project"]
)


# Load model
try:
    model, features, metrics = load_model()

except FileNotFoundError:
    st.error("Model files missing. Please run train_model.py first.")
    st.stop()


# PAGE 1: WEBSITE SCANNER
if page == "Website Scanner":

    st.title("🛡️ PhishGuard AI")

    st.subheader(
        "Machine Learning Based Phishing Website Detection"
    )

    st.write(
        "Enter a website URL to analyse its phishing characteristics."
    )

    st.warning(
        "This tool provides a machine-learning prediction, "
        "not a guarantee that a website is safe."
    )

    url = st.text_input(
        "Enter Website URL",
        placeholder="https://example.com"
    )

    if st.button("Analyze Website", type="primary"):

        cleaned_url = url.strip()

        if not cleaned_url:
            st.error("Please enter a website URL.")

        elif " " in cleaned_url:
            st.error("Please enter a valid URL without spaces.")

        else:
            try:
                extracted = extract_features(cleaned_url)

                input_data = pd.DataFrame(
                    [[extracted[f] for f in features]],
                    columns=features
                )

                prediction = model.predict(input_data)[0]

                probabilities = model.predict_proba(input_data)[0]

                phishing_probability = probabilities[1] * 100

                st.divider()

                if prediction == 1:
                    st.error("⚠️ Potential Phishing Website")
                else:
                    st.success("✅ Predicted as Legitimate")

                st.metric(
                    "Model's Phishing Probability",
                    f"{phishing_probability:.2f}%"
                )

                st.progress(float(probabilities[1]))

                st.caption(
                    "Probability is a model estimate, "
                    "not verified website safety."
                )

                with st.expander("View Extracted URL Features"):

                    st.dataframe(
                        pd.DataFrame(
                            extracted.items(),
                            columns=["Feature", "Value"]
                        ),
                        use_container_width=True
                    )

            except Exception as error:
                st.error(f"Unable to analyse this URL: {error}")


# PAGE 2: MODEL PERFORMANCE
elif page == "Model Performance":

    st.title("📊 Model Performance Dashboard")

    st.write(
        "Evaluation results from the held-out test dataset."
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Accuracy",
        f"{metrics['accuracy'] * 100:.2f}%"
    )

    col2.metric(
        "Precision",
        f"{metrics['precision'] * 100:.2f}%"
    )

    col3.metric(
        "Recall",
        f"{metrics['recall'] * 100:.2f}%"
    )

    col4.metric(
        "F1 Score",
        f"{metrics['f1_score'] * 100:.2f}%"
    )

    st.divider()

    st.subheader("Confusion Matrix")

    cm = metrics["confusion_matrix"]

    fig, ax = plt.subplots(figsize=(6, 4))

    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=["Legitimate", "Phishing"],
        yticklabels=["Legitimate", "Phishing"],
        ax=ax
    )

    ax.set_xlabel("Predicted Label")
    ax.set_ylabel("Actual Label")

    st.pyplot(fig)
    plt.close(fig)

    st.caption(
        f"Total test samples: {metrics['test_samples']}"
    )

    st.subheader("Feature Importance")

    importance = pd.DataFrame({
        "Feature": features,
        "Importance": model.feature_importances_
    }).sort_values(
        "Importance",
        ascending=False
    )

    fig2, ax2 = plt.subplots(figsize=(9, 6))

    sns.barplot(
        data=importance,
        x="Importance",
        y="Feature",
        ax=ax2
    )

    ax2.set_title("Random Forest Feature Importance")

    st.pyplot(fig2)
    plt.close(fig2)

    st.dataframe(
        importance,
        use_container_width=True
    )


# PAGE 3: ABOUT PROJECT
elif page == "About Project":

    st.title("ℹ️ About PhishGuard AI")

    st.markdown("""
    ### Project Overview

    PhishGuard AI is an educational cybersecurity application
    that uses Machine Learning to classify website URLs.

    ### Technologies Used

    - Python
    - Pandas and NumPy
    - Scikit-learn
    - Random Forest Classifier
    - Streamlit
    - Matplotlib and Seaborn

    ### Dataset

    PhishTrap labelled URL dataset.

    ### Model

    Random Forest Classifier with 200 decision trees.

    ### Limitations

    - Predictions depend on the quality of the training dataset.
    - URL-based features cannot establish whether a website is genuinely safe.
    - New phishing techniques may not be recognized.
    - This application is an educational tool, not a replacement
      for professional security software.
    """)

    st.info(
        "Never enter passwords, OTPs or other personal information "
        "into suspicious websites."
    )


# Footer
st.divider()

st.caption(
    "PhishGuard AI | Educational Cybersecurity Project"
)
