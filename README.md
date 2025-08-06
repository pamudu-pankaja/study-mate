# 📚 Study Mate

**Study Mate** is your friendly study companion — a simple web app that lets you upload PDFs (like textbooks), ask questions, and get smart answers powered by Google Gemini!  

Whether you want detailed AI explanations or quick lookups inside your study materials, Study Mate makes it easy — all from a clean, user-friendly web interface.

---

## 📖 About Study Mate

Study Mate is a simple and friendly web app that helps you study smarter. Here’s what it offers:

- **Web frontend:** built with Flask, HTML, CSS, and JavaScript.  
- Upload PDFs and ask questions right from your browser.  
- Powered by **Google Gemini Flash 2.0** with conversation memory to keep your chats smooth.  
- Vector similarity search for pinpointing answers inside your PDFs.  
- Basic web search is working but still needs improvement — stay tuned!  
- Runs locally by launching `main.py` and opening `localhost` in your browser.

---

## ✨ Features

- Upload **PDF files** and have them automatically split and indexed (File size must be under 1mb).
- Tracks real and logical page numbers (including Roman numerals for preface pages,You can set the start logical page as the page you want to start counting)
- Recognizes sections even across multiple PDF files
- Choose between:
  - **General Gemini LLM response**
  - **Vector similarity search**
  - **Web search**

---

## 🛠 Tech Stack

- Backend: Python, Flask  
- Frontend: HTML, CSS, JavaScript  
- AI: Google Gemini API  
- Vector Storage: Pinecone  
- Web Search: Google Custom Search API

---

## 🚀 Getting Started

1. **Clone the repo**

    ```bash
    git clone https://github.com/pamudu-pankaja/study-mate.git
    cd study-mate
    ```

2. **Install requirements**

    ```bash
    pip install -r requirements.txt
    ```

3. **Setup environment variables**

- Copy `.env.example` to `.env` and add your API keys:  
  - [Google AI Studio (Gemini)](https://aistudio.google.com/u/2/apikey)
  - [Pinecone](app.pinecone.io/organizations) 
  - [Google Custom Search API](https://console.cloud.google.com/apis)

4. **Run the app**

    ```bash
    python main.py
    ```

5. **Open your browser** and go to `http://localhost:5000` to start using Study Mate!

---

## 🤝 Contributing

Found bugs or have ideas? Open an issue or submit a pull request — I’m still learning and appreciate all feedback.

---

## Credits 🙏 

This project uses frontend code originally developed by [Ramon Victor](https://github.com/ramon-victor)
Licensed under the GNU General Public License v3.0
---

## 📜 License

This project is licensed under the [Creative Commons Attribution-NonCommercial 4.0 International License](https://creativecommons.org/licenses/by-nc/4.0/).

You are free to:

- **Share** — Copy and redistribute the material in any medium or format.

- **Adapt** — Remix, transform, and build upon the material.

Under the following terms:

- **Attribution** — You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.

- **NonCommercial** — You may not use the material for commercial purposes.



