const query = (obj) =>
  Object.keys(obj)
    .map((k) => encodeURIComponent(k) + "=" + encodeURIComponent(obj[k]))
    .join("&");
const url_prefix = document
  .querySelector("body")
  .getAttribute("data-urlprefix");
const markdown = window.markdownit({
  html: true,
  linkify: true,
  typographer: true,
});
const message_box = document.getElementById(`messages`);
const message_input = document.getElementById(`message-input`);
const box_conversations = document.querySelector(`.top`);
const spinner = box_conversations.querySelector(".spinner");
const stop_generating = document.querySelector(`.stop-generating`);
const send_button = document.querySelector(`#send-button`);
const welcome_msg = document.getElementById("welcome-msg");
const user_image = `<img src="${url_prefix}/static/img/user.png" alt="User Avatar">`;
const gpt_image = `<img src="${url_prefix}/static/img/book.png" alt="Book Avatar">`;
let currentChatTitle = null;
let prompt_lock = false;

hljs.addPlugin(new CopyButtonPlugin());

message_input.addEventListener("blur", () => {
  window.scrollTo(0, 0);
});

message_input.addEventListener("focus", () => {
  document.documentElement.scrollTop = document.documentElement.scrollHeight;
});

const delete_conversations = async () => {
  localStorage.clear();
  await new_conversation();
};

const handle_ask = async () => {
  message_input.style.height = `80px`;
  window.scrollTo(0, 0);
  let message = message_input.value;

  if (message.length > 0) {
    document.getElementById("welcome-msg").classList.add("hide");
    document.getElementById("welcome-msg").style.display = "none";

    message_input.value = ``;
    message_input.dispatchEvent(new Event("input"));
    console.log("Users message : ", message);

    await ask_gpt(message);
  }
};

const remove_cancel_button = async () => {
  stop_generating.classList.add(`stop-generating-hiding`);

  setTimeout(() => {
    stop_generating.classList.remove(`stop-generating-hiding`);
    stop_generating.classList.add(`stop-generating-hidden`);
  }, 300);
};

const ask_gpt = async (message) => {
  try {
    message_input.value = ``;
    message_input.innerHTML = ``;
    message_input.innerText = ``;

    if (!window.conversation_id) {
      window.conversation_id = uuid();
    }
    console.log(`Current conversation id : ${window.conversation_id}`);

    await add_conversation(window.conversation_id, message);
    window.scrollTo(0, 0);
    window.controller = new AbortController();

    // jailbreak = document.getElementById("jailbreak");
    // model = document.getElementById("model");
    prompt_lock = true;
    window.text = ``;
    window.token = message_id();

    stop_generating.classList.remove(`stop-generating-hidden`);

    add_user_message_box(message);

    message_box.scrollTop = message_box.scrollHeight;
    window.scrollTo(0, 0);
    await new Promise((r) => setTimeout(r, 500));
    window.scrollTo(0, 0);

    message_box.innerHTML += `
            <div class="message chat-bot">
                <div class="avatar-container">
                    ${gpt_image}
                </div>
                <div class="content" id="gpt_${window.token}">
                    <div id="cursor"></div>
                </div>
            </div>
        `;

    message_box.scrollTop = message_box.scrollHeight;
    window.scrollTo(0, 0);
    await new Promise((r) => setTimeout(r, 1000));
    window.scrollTo(0, 0);

    const vectorBtn = document.getElementById("switch_book");
    const webBtn = document.getElementById("switch_web");
    let searchPath = "none";
    let searchLabel = "";

    if (vectorBtn.checked) {
      searchPath = "vector";
      searchLabel = `<div class="search-label">[ 📚 Vector Search ]</div>`;
    } else if (webBtn.checked) {
      searchPath = "web";
      searchLabel = `<div class="search-label">[ 🌐 Web Search ]</div>`;
    } else if (!webBtn.checked && !vectorBtn.checked) {
      searchPath = "none";
      searchLabel = "";
    } else {
      searchPath = "none";
      searchLabel = "";
    }

    const response = await fetch(
      `${url_prefix}/chat/${window.conversation_id}`,
      {
        method: `POST`,
        signal: window.controller.signal,
        headers: {
          "content-type": `application/json`,
          accept: `text/event-stream`,
        },
        body: JSON.stringify({
          conversation_id: window.conversation_id,
          searchPath: searchPath,
          action: `_ask`,
          // model: model.options[model.selectedIndex].value,
          // jailbreak: jailbreak.options[jailbreak.selectedIndex].value,
          meta: {
            id: window.token,
            content: {
              conversation: await get_conversation(window.conversation_id),
              // internet_access: document.getElementById("switch").checked,
              content_type: "text",
              parts: [
                {
                  content: message,
                  role: "user",
                },
              ],
            },
          },
        }),
      }
    );

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    const error = response.body.error;
    console.log(error);

    let text = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      // let chunk = decodeUnicode(new TextDecoder().decode(value));
      let chunk = decoder.decode(value, { stream: true });

      chunk.split("\n").forEach((line) => {
        if (line.startsWith("data: ")) {
          const cleaned = line.slice(6).trim(); // Remove "data: "
          text += `${cleaned}` + "\n";
        }
      });

      if (
        // chunk.includes(`<form id="challenge-form" action="${url_prefix}/backend-api/v2/conversation?`)
        chunk.includes(`<form id="challenge-form" action="${url_prefix}/chat?`)
      ) {
        chunk = `cloudflare token expired, please refresh the page.`;
      }

      // text += chunk;

      // if (text.startsWith("```markdown") && text.endsWith("```")) {
      //   text = text.replace(/^```markdown\s*\n?([\s\S]*?)\n?```$/, "$1");
      //   console.log("Stripped markdown fences:", text);
      // }
      // }



      document.getElementById(`gpt_${window.token}`).innerHTML =
        searchLabel + markdown.render(text);
      document.querySelectorAll(`code`).forEach((el) => {
        hljs.highlightElement(el);
      });

      window.scrollTo(0, 0);
      message_box.scrollTo({ top: message_box.scrollHeight, behavior: "auto" });
    }

    // if text contains :
    if (
      text.includes(
        `instead. Maintaining this website and API costs a lot of money`
      )
    ) {
      document.getElementById(`gpt_${window.token}`).innerHTML =
        "An error occurred, please reload / refresh cache and try again.";
    }

    let contextData = "";
    if (searchPath != "none") {
      let endpointContext = window.conversation_id
        ? `${url_prefix}/chat/${window.conversation_id}/context-data`
        : `${url_prefix}/chat/context-data`;

      try {
        const res = await fetch(endpointContext);
        const data = await res.json();
        contextData = data.context || "";
      } catch (e) {
        console.log(`Error while getting the contextData :  ${e}`);
        contextData = "";
      }
    }

    add_message(window.conversation_id, "user", message);
    add_message(window.conversation_id,"assistant",text,contextData,searchPath);
    console.log(`Asisstant's message : ${text}`);

    history.pushState({}, null, `${url_prefix}/chat/${conversation_id}`);

    message_box.scrollTop = message_box.scrollHeight;
    await remove_cancel_button();
    prompt_lock = false;

    await load_conversations(20, 0);
    window.scrollTo(0, 0);
  } catch (e) {
    add_message(window.conversation_id, "user", message);

    message_box.scrollTop = message_box.scrollHeight;
    await remove_cancel_button();
    prompt_lock = false;

    await load_conversations(20, 0);

    console.log(e);

    let cursorDiv = document.getElementById(`cursor`);
    if (cursorDiv) cursorDiv.parentNode.removeChild(cursorDiv);

    if (e.name != `AbortError`) {
      let error_message = `oops ! something went wrong, please try again / reload. [stacktrace in console]`;

      document.getElementById(`gpt_${window.token}`).innerHTML = error_message;
      add_message(window.conversation_id, "assistant", error_message);
      history.pushState({}, null, `${url_prefix}/chat/${conversation_id}`);
    } else {
      document.getElementById(`gpt_${window.token}`).innerHTML += ` [aborted]`;
      add_message(window.conversation_id, "assistant", text + `[aborted]`);
      history.pushState({}, null, `${url_prefix}/chat/${conversation_id}`);
    }

    window.scrollTo(0, 0);
  }
};

const add_user_message_box = (message) => {
  const messageDiv = createElement("div", { classNames: ["message", "user"] });
  const avatarContainer = createElement("div", {
    classNames: ["avatar-container"],
    innerHTML: user_image,
  });
  const contentDiv = createElement("div", {
    classNames: ["content"],
    id: `user_${token}`,
    textContent: message,
  });

  messageDiv.append(avatarContainer, contentDiv);
  message_box.appendChild(messageDiv);
};

const decodeUnicode = (str) => {
  return str.replace(/\\u([a-fA-F0-9]{4})/g, function (match, grp) {
    return String.fromCharCode(parseInt(grp, 16));
  });
};

const clear_conversations = async () => {
  const elements = box_conversations.childNodes;
  let index = elements.length;

  if (index > 0) {
    while (index--) {
      const element = elements[index];
      if (
        element.nodeType === Node.ELEMENT_NODE &&
        element.tagName.toLowerCase() !== `button`
      ) {
        box_conversations.removeChild(element);
      }
    }
  }
};

const clear_conversation = async () => {
  let messages = Array.from(message_box.children).filter(
    (el) => el.id !== "welcome-msg"
  );

  for (let msg of messages) {
    message_box.removeChild(msg);
  }
  welcome_msg.classList.remove("hide");
};

const delete_conversation = async (conversation_id) => {
  localStorage.removeItem(`conversation:${conversation_id}`);

  if (window.conversation_id == conversation_id) {
    await new_conversation();
  }

  await load_conversations(20, 0, true);
};

const set_conversation = async (conversation_id) => {
  history.pushState({}, null, `${url_prefix}/chat/${conversation_id}`);
  // history.pushState({}, '','static_index.html' )
  window.conversation_id = conversation_id;

  welcome_msg.classList.add("hide");
  await clear_conversation();
  await load_conversation(conversation_id);
  await load_conversations(20, 0, true);
};

const new_conversation = async () => {
  history.pushState({}, null, `${url_prefix}/chat`);
  // history.pushState({}, '','static_index.html' )
  window.conversation_id = uuid();

  await clear_conversation();
  await load_conversations(20, 0, true);
  document.getElementById("welcome-msg").classList.remove("hide");
  document.getElementById("welcome-msg").style.display = "unset";
};

const load_conversation = async (conversation_id) => {
  let conversation = await JSON.parse(
    localStorage.getItem(`conversation:${conversation_id}`)
  );
  console.log(conversation, conversation_id);

  if (!conversation || !conversation.items) {
    document.getElementById("welcome-msg").classList.add("hide");
    const fallback = document.createElement("p");
    fallback.textContent = "No conversation found. Start a new chat!";
    fallback.style.padding = "1rem";
    fallback.style.color = "#888";
    message_box.appendChild(fallback);
    return;
  }

  document.getElementById("welcome-msg").classList.add("hide");
  document.getElementById("welcome-msg").style.display = "none";

  for (item of conversation.items) {
    if (is_assistant(item.role)) {
      message_box.innerHTML += load_gpt_message_box(item);
    } else {
      message_box.innerHTML += load_user_message_box(item.content);
    }
  }

  document.querySelectorAll(`code`).forEach((el) => {
    hljs.highlightElement(el);
  });

  message_box.scrollTo({ top: message_box.scrollHeight, behavior: "smooth" });

  setTimeout(() => {
    message_box.scrollTop = message_box.scrollHeight;
  }, 500);
};

const load_user_message_box = (content) => {
  const messageDiv = createElement("div", { classNames: ["message", "user"] });
  const avatarContainer = createElement("div", {
    classNames: ["avatar-container"],
    innerHTML: user_image,
  });
  const contentDiv = createElement("div", { classNames: ["content"] });
  const preElement = document.createElement("pre");
  preElement.textContent = content;
  contentDiv.appendChild(preElement);

  messageDiv.append(avatarContainer, contentDiv);

  return messageDiv.outerHTML;
};

const load_gpt_message_box = (item) => {
  const searchType = item.searchType || "";
  let itemSearchLabel = "";

  if (searchType === "vector") {
    itemSearchLabel = `<div class="search-label">[ 📚 Vector Search ]</div> `;
  } else if (searchType === "web") {
    itemSearchLabel = `<div class="search-label">[ 🌐 Web Search ]</div> `;
  }

  return `
            <div class="message chat-bot">
                <div class="avatar-container">
                    ${gpt_image}
                </div>
                <div class="content">
                    ${itemSearchLabel}
                    ${markdown.render(item.content)}
                </div>
            </div>
        `;
};

const is_assistant = (role) => {
  return role == "assistant";
};

const get_conversation = async (conversation_id) => {
  console.log("addding conversation id:" ,conversation_id)
  let conversation = await JSON.parse(
    localStorage.getItem(`conversation:${conversation_id}`)
  );
  return conversation.items;
};

const add_conversation = async (conversation_id, message) => {
  if (localStorage.getItem(`conversation:${conversation_id}`) == null) {
    let endpoint = conversation_id
      ? `${url_prefix}/chat/${conversation_id}/generate-title`
      : `${url_prefix}/chat/generate-title`;

    let chatTitle = "";

    try {
      const res = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message }),
      });
      const data = await res.json();
      chatTitle = data.title || message.substr(0, 16);
      currentChatTitle = data.title || message.substr(0, 16);
    } catch (err) {
      console.error("Failed to generate title", err);
    } finally {
      console.log("conversation adding id :",conversation_id)
      localStorage.setItem(
        `conversation:${conversation_id}`,
        JSON.stringify({
          id: conversation_id,
          title: chatTitle,
          items: [],
        })
      );
    }
  }
};

const add_message = async (
  conversation_id,
  role,
  content,
  context,
  searchType
) => {
  before_adding = JSON.parse(
    localStorage.getItem(`conversation:${conversation_id}`)
  );

  console.log("add message id :  ", conversation_id)

  const message = {
    role: role,
    content: content,
  };

  if (role == "assistant" && context && searchType) {
    message.used_context = context;
    message.searchType = searchType;
  }

  if (!before_adding){
    console.warn("Conversation is missing, Creating a new one...")
    before_adding={
      id : conversation_id,
      title : currentChatTitle,
      items : []
    }
  }

  if (!before_adding.items){
    before_adding.items = [];
  }

  before_adding.items.push(message);

  localStorage.setItem(
    `conversation:${conversation_id}`,
    JSON.stringify(before_adding)
  ); // update conversation
};

const load_conversations = async (limit, offset, loader) => {
  //console.log(loader);
  //if (loader === undefined) box_conversations.appendChild(spinner);
  let conversations = [];
  for (let i = 0; i < localStorage.length; i++) {
    if (localStorage.key(i).startsWith("conversation:")) {
      let conversation = localStorage.getItem(localStorage.key(i));
      conversations.push(JSON.parse(conversation));
    }
  }

  //if (loader === undefined) spinner.parentNode.removeChild(spinner)
  await clear_conversations();

  for (conversation of conversations) {
    box_conversations.innerHTML += `
            <div class="conversation-sidebar">
                <div class="left" onclick="set_conversation('${conversation.id}')">
                    <i class="fa-regular fa-comments"></i>
                    <span class="conversation-title" style="text-overflow:ellipsis;">${conversation.title}</span>
                </div>
                <i onclick="delete_conversation('${conversation.id}')" class="fa-solid fa-trash"></i>
            </div>
        `;
  }

  document.querySelectorAll(`code`).forEach((el) => {
    hljs.highlightElement(el);
  });
};

document.getElementById(`cancelButton`).addEventListener(`click`, async () => {
  window.controller.abort();
  console.log(`aborted ${window.conversation_id}`);
});

function h2a(str1) {
  var hex = str1.toString();
  var str = "";

  for (var n = 0; n < hex.length; n += 2) {
    str += String.fromCharCode(parseInt(hex.substr(n, 2), 16));
  }

  return str;
}

const uuid = () => {
  return `xxxxxxxx-xxxx-4xxx-yxxx-${Date.now().toString(16)}`.replace(
    /[xy]/g,
    function (c) {
      var r = (Math.random() * 16) | 0,
        v = c == "x" ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    }
  );
};

const message_id = () => {
  random_bytes = (Math.floor(Math.random() * 1338377565) + 2956589730).toString(
    2
  );
  unix = Math.floor(Date.now() / 1000).toString(2);

  return BigInt(`0b${unix}${random_bytes}`).toString();
};

window.onload = async () => {
  // load_settings_localstorage();

  conversations = 0;
  for (let i = 0; i < localStorage.length; i++) {
    if (localStorage.key(i).startsWith("conversation:")) {
      conversations += 1;
    }
  }

  if (conversations == 0) localStorage.clear();

  await setTimeout(() => {
    load_conversations(20, 0);
  }, 1);

  if (!window.location.href.endsWith(`#`)) {
    if (/\/chat\/.+/.test(window.location.href.slice(url_prefix.length))) {
      await load_conversation(window.conversation_id);
    }
  }

  message_input.addEventListener("keydown", async (evt) => {
    if (prompt_lock) return;

    if (evt.key === "Enter" && !evt.shiftKey) {
      evt.preventDefault();
      await handle_ask();
    }
  });

  send_button.addEventListener("click", async (event) => {
    event.preventDefault();
    if (prompt_lock) return;
    message_input.blur();
    await handle_ask();
  });

  // register_settings_localstorage();
};

window.addEventListener("DOMContentLoaded", () => {
  const path = window.location.pathname;
  const uuidRegex =
    /^\/chat\/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

  if (path === `${url_prefix}/chat` || path === `${url_prefix}/`) {
    document.getElementById("welcome-msg").style.display = "unset";
  }

  if (!uuidRegex.test(window.location.pathname)) {
    document.getElementById("welcome-msg").classList.remove("hide");
    // document.getElementById('welcome-msg').style.display = 'unset';
  }
});

const register_settings_localstorage = async () => {
  settings_ids = ["switch", "model", "jailbreak"];
  settings_elements = settings_ids.map((id) => document.getElementById(id));
  settings_elements.map((element) =>
    element.addEventListener(`change`, async (event) => {
      switch (event.target.type) {
        case "checkbox":
          localStorage.setItem(event.target.id, event.target.checked);
          break;
        case "select-one":
          localStorage.setItem(event.target.id, event.target.selectedIndex);
          break;
        default:
          console.warn("Unresolved element type");
      }
    })
  );
};

const load_settings_localstorage = async () => {
  settings_ids = ["switch", "model", "jailbreak"];
  settings_elements = settings_ids.map((id) => document.getElementById(id));
  settings_elements.map((element) => {
    if (localStorage.getItem(element.id)) {
      switch (element.type) {
        case "checkbox":
          element.checked = localStorage.getItem(element.id) === "true";
          break;
        case "select-one":
          element.selectedIndex = parseInt(localStorage.getItem(element.id));
          break;
        default:
          console.warn("Unresolved element type");
      }
    }
  });
};

function clearTextarea(textarea) {
  textarea.style.removeProperty("height");
  textarea.style.height = `${textarea.scrollHeight + 4}px`;
  if (textarea.value.trim() === "" && textarea.value.includes("\n")) {
    textarea.value = "";
  }
}

function createElement(tag, { classNames, id, innerHTML, textContent } = {}) {
  const el = document.createElement(tag);
  if (classNames) {
    el.classList.add(...classNames);
  }
  if (id) {
    el.id = id;
  }
  if (innerHTML) {
    el.innerHTML = innerHTML;
  }
  if (textContent) {
    const preElement = document.createElement("pre");
    preElement.textContent = textContent;
    el.appendChild(preElement);
  }
  return el;
}
