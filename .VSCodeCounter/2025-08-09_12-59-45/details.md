# Details

Date : 2025-08-09 12:59:45

Directory d:\\Programming\\Code Jam 2025\\Hisory Chat Bot\\history-chat-bot

Total : 99 files,  7055 codes, 315 comments, 1482 blanks, all 8852 lines

[Summary](results.md) / Details / [Diff Summary](diff.md) / [Diff Details](diff-details.md)

## Files
| filename | language | code | comment | blank | total |
| :--- | :--- | ---: | ---: | ---: | ---: |
| [README.md](/README.md) | Markdown | 71 | 0 | 45 | 116 |
| [app/\_\_init\_\_.py](/app/__init__.py) | Python | 2 | 0 | 1 | 3 |
| [app/agents/\_\_init\_\_.py](/app/agents/__init__.py) | Python | 3 | 0 | 1 | 4 |
| [app/agents/chat\_bot\_agent/\_\_init\_\_.py](/app/agents/chat_bot_agent/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [app/agents/chat\_bot\_agent/chat\_bot\_agent.py](/app/agents/chat_bot_agent/chat_bot_agent.py) | Python | 44 | 11 | 20 | 75 |
| [app/agents/chat\_bot\_agent/tool\_handler.py](/app/agents/chat_bot_agent/tool_handler.py) | Python | 27 | 2 | 8 | 37 |
| [app/agents/chat\_bot\_agent/tools/\_\_init\_\_.py](/app/agents/chat_bot_agent/tools/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [app/agents/chat\_bot\_agent/tools/is\_english.py](/app/agents/chat_bot_agent/tools/is_english.py) | Python | 9 | 0 | 3 | 12 |
| [app/agents/chat\_bot\_agent/tools/summarizer.py](/app/agents/chat_bot_agent/tools/summarizer.py) | Python | 42 | 0 | 18 | 60 |
| [app/agents/chat\_bot\_agent/tools/summarizer\_NEW.py](/app/agents/chat_bot_agent/tools/summarizer_NEW.py) | Python | 41 | 0 | 13 | 54 |
| [app/agents/chat\_bot\_agent/tools/translator.py](/app/agents/chat_bot_agent/tools/translator.py) | Python | 22 | 0 | 4 | 26 |
| [app/agents/llm/\_\_init\_\_.py](/app/agents/llm/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [app/agents/llm/llm.py](/app/agents/llm/llm.py) | Python | 108 | 52 | 52 | 212 |
| [app/agents/rag\_agent/rag\_agent.py](/app/agents/rag_agent/rag_agent.py) | Python | 34 | 3 | 14 | 51 |
| [app/agents/rag\_agent/vector\_store/\_\_init\_\_.py](/app/agents/rag_agent/vector_store/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [app/agents/rag\_agent/vector\_store/embedder.py](/app/agents/rag_agent/vector_store/embedder.py) | Python | 36 | 4 | 13 | 53 |
| [app/agents/rag\_agent/vector\_store/file\_load.py](/app/agents/rag_agent/vector_store/file_load.py) | Python | 102 | 0 | 28 | 130 |
| [app/agents/rag\_agent/vector\_store/pinecorn\_client.py](/app/agents/rag_agent/vector_store/pinecorn_client.py) | Python | 73 | 6 | 21 | 100 |
| [app/agents/rag\_agent/vector\_store/vectore\_search.py](/app/agents/rag_agent/vector_store/vectore_search.py) | Python | 23 | 3 | 15 | 41 |
| [app/agents/web\_search/\_\_init\_\_.py](/app/agents/web_search/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [app/agents/web\_search/web\_agent.py](/app/agents/web_search/web_agent.py) | Python | 16 | 0 | 5 | 21 |
| [app/backup/main.py](/app/backup/main.py) | Python | 14 | 3 | 10 | 27 |
| [app/backup/static\_index.html](/app/backup/static_index.html) | HTML | 140 | 23 | 24 | 187 |
| [app/chatbot.py](/app/chatbot.py) | Python | 280 | 1 | 63 | 344 |
| [app/config/\_\_init\_\_.py](/app/config/__init__.py) | Python | 1 | 0 | 1 | 2 |
| [app/config/config.py](/app/config/config.py) | Python | 7 | 0 | 4 | 11 |
| [app/static/css/button.css](/app/static/css/button.css) | PostCSS | 26 | 0 | 5 | 31 |
| [app/static/css/buttons.css](/app/static/css/buttons.css) | PostCSS | 15 | 0 | 3 | 18 |
| [app/static/css/checkbox.css](/app/static/css/checkbox.css) | PostCSS | 47 | 0 | 9 | 56 |
| [app/static/css/conversation.css](/app/static/css/conversation.css) | PostCSS | 194 | 5 | 41 | 240 |
| [app/static/css/dropdown.css](/app/static/css/dropdown.css) | PostCSS | 9 | 0 | 2 | 11 |
| [app/static/css/field.css](/app/static/css/field.css) | PostCSS | 10 | 0 | 2 | 12 |
| [app/static/css/global.css](/app/static/css/global.css) | PostCSS | 92 | 0 | 23 | 115 |
| [app/static/css/hljs.css](/app/static/css/hljs.css) | PostCSS | 59 | 1 | 9 | 69 |
| [app/static/css/label.css](/app/static/css/label.css) | PostCSS | 19 | 0 | 1 | 20 |
| [app/static/css/mail.css](/app/static/css/mail.css) | PostCSS | 130 | 9 | 33 | 172 |
| [app/static/css/main.css](/app/static/css/main.css) | PostCSS | 14 | 0 | 1 | 15 |
| [app/static/css/message-input.css](/app/static/css/message-input.css) | PostCSS | 30 | 0 | 12 | 42 |
| [app/static/css/message.css](/app/static/css/message.css) | PostCSS | 213 | 2 | 39 | 254 |
| [app/static/css/options.css](/app/static/css/options.css) | PostCSS | 9 | 0 | 2 | 11 |
| [app/static/css/right-sidebar.css](/app/static/css/right-sidebar.css) | PostCSS | 366 | 29 | 59 | 454 |
| [app/static/css/select.css](/app/static/css/select.css) | PostCSS | 28 | 1 | 7 | 36 |
| [app/static/css/settings.css](/app/static/css/settings.css) | PostCSS | 36 | 0 | 9 | 45 |
| [app/static/css/sidebar.css](/app/static/css/sidebar.css) | PostCSS | 197 | 4 | 42 | 243 |
| [app/static/css/stop-generating.css](/app/static/css/stop-generating.css) | PostCSS | 33 | 0 | 6 | 39 |
| [app/static/css/style.css](/app/static/css/style.css) | PostCSS | 20 | 0 | 0 | 20 |
| [app/static/css/typing.css](/app/static/css/typing.css) | PostCSS | 13 | 0 | 3 | 16 |
| [app/static/img/site.webmanifest](/app/static/img/site.webmanifest) | JSON | 19 | 0 | 0 | 19 |
| [app/static/js/change-language.js](/app/static/js/change-language.js) | JavaScript | 39 | 4 | 7 | 50 |
| [app/static/js/chat.js](/app/static/js/chat.js) | JavaScript | 605 | 19 | 118 | 742 |
| [app/static/js/drop-down.js](/app/static/js/drop-down.js) | JavaScript | 73 | 3 | 18 | 94 |
| [app/static/js/highlight.min.js](/app/static/js/highlight.min.js) | JavaScript | 1 | 0 | 0 | 1 |
| [app/static/js/highlightjs-copy.min.js](/app/static/js/highlightjs-copy.min.js) | JavaScript | 1 | 0 | 0 | 1 |
| [app/static/js/icons.js](/app/static/js/icons.js) | JavaScript | 1 | 0 | 0 | 1 |
| [app/static/js/import-file.js](/app/static/js/import-file.js) | JavaScript | 120 | 3 | 28 | 151 |
| [app/static/js/index-name.js](/app/static/js/index-name.js) | JavaScript | 74 | 1 | 12 | 87 |
| [app/static/js/mail.js](/app/static/js/mail.js) | JavaScript | 66 | 3 | 15 | 84 |
| [app/static/js/sidebar-toggler.js](/app/static/js/sidebar-toggler.js) | JavaScript | 113 | 7 | 17 | 137 |
| [app/static/js/theme-toggler.js](/app/static/js/theme-toggler.js) | JavaScript | 17 | 0 | 6 | 23 |
| [app/static/js/toggle-button.js](/app/static/js/toggle-button.js) | JavaScript | 7 | 0 | 2 | 9 |
| [app/templates/index.html](/app/templates/index.html) | HTML | 286 | 22 | 30 | 338 |
| [docs/index.html](/docs/index.html) | HTML | 294 | 22 | 22 | 338 |
| [docs/static/css/button.css](/docs/static/css/button.css) | PostCSS | 26 | 0 | 5 | 31 |
| [docs/static/css/buttons.css](/docs/static/css/buttons.css) | PostCSS | 4 | 0 | 1 | 5 |
| [docs/static/css/checkbox.css](/docs/static/css/checkbox.css) | PostCSS | 47 | 0 | 9 | 56 |
| [docs/static/css/conversation.css](/docs/static/css/conversation.css) | PostCSS | 194 | 5 | 41 | 240 |
| [docs/static/css/dropdown.css](/docs/static/css/dropdown.css) | PostCSS | 9 | 0 | 2 | 11 |
| [docs/static/css/field.css](/docs/static/css/field.css) | PostCSS | 10 | 0 | 2 | 12 |
| [docs/static/css/global.css](/docs/static/css/global.css) | PostCSS | 93 | 0 | 17 | 110 |
| [docs/static/css/hljs.css](/docs/static/css/hljs.css) | PostCSS | 59 | 1 | 9 | 69 |
| [docs/static/css/label.css](/docs/static/css/label.css) | PostCSS | 19 | 0 | 1 | 20 |
| [docs/static/css/mail.css](/docs/static/css/mail.css) | PostCSS | 89 | 4 | 23 | 116 |
| [docs/static/css/main.css](/docs/static/css/main.css) | PostCSS | 13 | 0 | 1 | 14 |
| [docs/static/css/message-input.css](/docs/static/css/message-input.css) | PostCSS | 30 | 0 | 12 | 42 |
| [docs/static/css/message.css](/docs/static/css/message.css) | PostCSS | 210 | 2 | 37 | 249 |
| [docs/static/css/options.css](/docs/static/css/options.css) | PostCSS | 9 | 0 | 2 | 11 |
| [docs/static/css/right-sidebar.css](/docs/static/css/right-sidebar.css) | PostCSS | 376 | 14 | 61 | 451 |
| [docs/static/css/select.css](/docs/static/css/select.css) | PostCSS | 28 | 1 | 7 | 36 |
| [docs/static/css/settings.css](/docs/static/css/settings.css) | PostCSS | 36 | 0 | 9 | 45 |
| [docs/static/css/sidebar.css](/docs/static/css/sidebar.css) | PostCSS | 194 | 4 | 41 | 239 |
| [docs/static/css/stop-generating.css](/docs/static/css/stop-generating.css) | PostCSS | 33 | 0 | 6 | 39 |
| [docs/static/css/style.css](/docs/static/css/style.css) | PostCSS | 20 | 0 | 0 | 20 |
| [docs/static/css/typing.css](/docs/static/css/typing.css) | PostCSS | 13 | 0 | 3 | 16 |
| [docs/static/img/site.webmanifest](/docs/static/img/site.webmanifest) | JSON | 19 | 0 | 0 | 19 |
| [docs/static/js/change-language.js](/docs/static/js/change-language.js) | JavaScript | 39 | 4 | 7 | 50 |
| [docs/static/js/chat.js](/docs/static/js/chat.js) | JavaScript | 605 | 19 | 118 | 742 |
| [docs/static/js/drop-down.js](/docs/static/js/drop-down.js) | JavaScript | 73 | 3 | 18 | 94 |
| [docs/static/js/highlight.min.js](/docs/static/js/highlight.min.js) | JavaScript | 1 | 0 | 0 | 1 |
| [docs/static/js/highlightjs-copy.min.js](/docs/static/js/highlightjs-copy.min.js) | JavaScript | 1 | 0 | 0 | 1 |
| [docs/static/js/icons.js](/docs/static/js/icons.js) | JavaScript | 1 | 0 | 0 | 1 |
| [docs/static/js/import-file.js](/docs/static/js/import-file.js) | JavaScript | 120 | 3 | 28 | 151 |
| [docs/static/js/index-name.js](/docs/static/js/index-name.js) | JavaScript | 74 | 1 | 12 | 87 |
| [docs/static/js/mail.js](/docs/static/js/mail.js) | JavaScript | 44 | 2 | 14 | 60 |
| [docs/static/js/sidebar-toggler.js](/docs/static/js/sidebar-toggler.js) | JavaScript | 89 | 7 | 17 | 113 |
| [docs/static/js/theme-toggler.js](/docs/static/js/theme-toggler.js) | JavaScript | 17 | 0 | 6 | 23 |
| [docs/static/js/toggle-button.js](/docs/static/js/toggle-button.js) | JavaScript | 7 | 0 | 2 | 9 |
| [file\_transfer.py](/file_transfer.py) | Python | 44 | 2 | 17 | 63 |
| [main.py](/main.py) | Python | 9 | 0 | 3 | 12 |
| [requirements.txt](/requirements.txt) | pip requirements | 29 | 0 | 0 | 29 |

[Summary](results.md) / Details / [Diff Summary](diff.md) / [Diff Details](diff-details.md)