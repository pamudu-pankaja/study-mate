# 📚 TexT Book Chat BoT

A simple command-line tool that lets you choose how you want to search:

- 🤖 General LLM-based answers  
- 📘 Vector search through uploaded PDFs (perfect for textbooks)  
- 🌐 Basic web search  

This app mainly focuses on **vector-based search** for study material and textbooks.

**The web search option is still developing.** 

---

## ✨ Features

- Upload PDF files and have them automatically split and indexed
- Tracks real and logical page numbers (including Roman numerals for preface pages,You can set the start logical page as the page you want to start counting)
- Recognizes sections even across multiple PDF files
- Choose between:
  - General Gemini LLM response
  - Vector similarity search
  - Web search
- Simple CLI interface — just run and use!

---

## 🛠 Tech Stack

- **Python**
- **Google Gemini API**
- **Google Custom Search API**
- **Pinecone** (for vector storage)

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
```

### 2. Install requirements

```bash
pip install -r requirements.txt
```

> ⚠️ I'm so sorry if any package is missing in that file — feel free to install them manually if needed 🙏

### 3. Environment variables

- Copy the `.env.example` file to `.env`
- Add your own API keys:

> You can get your keys from:
> - [Google AI Studio](https://aistudio.google.com/u/2/apikey)
> - [Pinecone](app.pinecone.io/organizations)
> - [Google Custom Search API](https://console.cloud.google.com/apis)

### 4. Run the app

```bash
python main.py
```

A CLI will launch and you can choose the type of search you want to perform.

---

## 💡 Future Plans

I'd like to improve this as a **website for schoolwork**, making it more accessible and visually friendly. This is just the beginning — more features and polish to come!

---

## 🙏 Credits

Thanks to **Code Jam: Future Minds** for giving me this problem and the inspiration. Honestly, just getting the idea is the most important part — everything builds from there.

---

## 🤝 Contribute

Feel free to open issues or pull requests if you find bugs or want to improve anything. I'm still learning and always open to feedback!

---

## 📜 License 

This project is under the MIT License.

