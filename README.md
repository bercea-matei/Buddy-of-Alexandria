# Buddy of Alexandria
**🧠Your intelligent second brain, turning scattered notes into structured knowledge.**

This application is a dedicated learning companion that bridges the gap between note-taking and studying, empowering you to learn smarter not harder:
- **Boost Engagement:** Visualize your progress and discover new topics with dynamic roadmaps and intelligent suggestions.   
- **Maximize Retention:** Transform passive notes into active knowledge using fully customizable quizzes and testing frameworks.

### ⚠️ This Project is a Work in Progress
Welcome! This app is currently being built as a learning experience to explore AI integration in productivity tools. As a **prototype**, its primary goal is to showcase concepts rather than to be polished, full-featured application.

Feel free to explore, but please be aware that features may change.

### 🔧 How to run
1) install ollama
	- Linux
		```
			run: curl -fsSL https://ollama.com/install.sh | sh
		```
	- Windows
		```
			https://ollama.com/download/windows
		```
	- Mac
		```
			https://ollama.com/download/mac
		```
2) make sure server is running
	- Linux
		```
		ollama serve &
		```
	- Windows
		Should start automatically but you can manually **Ollama** launch it if you search for the app.
	- Mac
		Open the **Ollama** application from your Applications folder.
			
3) run app
	```
	python3 main.py
	```

In case the ai model did not download automatically run:
```
ollama pull phi3:mini
```
To verify if **Ollama** is running type the following into a terminal:
```
ollama list
```


### 🗺️ Roadmap
- [x] Vector Database & embedding process (search based on meaning not keywords)
- [ ] Add AI summarization of notes (RAG)
    - [x] summarize current open note
    - [X] summarize an idea (checks all notes)
    - [ ] agentic RAG?
- [ ] Tags
    - [ ] tags suggestion
- [ ] Suggestions
	- [ ] suggest ares of improvements (where to fill gaps and not how to fill them)
	- [ ] suggest further exploration topic (gives direction)
- [ ] Customizable tests
	- [ ] duration slider
	- [ ] difficulty slider
	- [ ] style preference slider
	- [ ] diversity of questions slider
- [ ] Custom right-click menu
	- [ ] find parallel / analogy 
	- [ ] quick definition (foreign word)
	- [ ] expansion (go more in depth)
- [ ] Check notes integrity
- [ ] Generate Roadmap / Course

### 🖼️ Current Status
- We have a summarize button at the top of the taskbar that will make a resume of the current open file (the one the user is focused on).
- Also the the chat window will be able to summarize your concepts across multiple notes as opposed to simple data retrieval like in previous versions.
- Next in line are tags as they help elevate the quality of those summaries.

### ⚙️ Current editor features
- Left side file tree
- Markdown editor (simulated) for:
	- Headline (1 to 6 #'s)
	- Italic
	- Bold
	- Strike-through 
	- Bullet points (kinda)
    - Text Block
- Tabs for multiple files open at the same time
- Font size and style changes (requires restart to take effect)


