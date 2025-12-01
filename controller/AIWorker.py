# AIWorker.py

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QThread
from llama_index.llms.ollama import Ollama


class AIWorker(QObject):
    """
    Runs the AI query in a separate thread to avoid freezing the GUI.
    """

    result_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    finished_stream = pyqtSignal()

    def __init__(self, index_manager) -> None:
        super().__init__()
        self._index_manager = index_manager
        self.llm = Ollama(
            model="phi3:mini",
            request_timeout=60.0,
            additional_kwargs={"num_ctx": 4096, "num_thread": 4},
            temperature=0.05,
        )

    @pyqtSlot(str)
    def run_query(self, user_text: str) -> None:
        """Query for RAG"""
        try:
            sematic_text = self._index_manager.query_question(user_text)
            ai_text = self.overview_prompt(sematic_text, topic=user_text)
            self.result_ready.emit(ai_text)
            self.finished_stream.emit()
        except Exception as e:
            print(f"[Thread {QThread.currentThreadId()}] Error during query: {e}")
            self.error_occurred.emit(str(e))

    @pyqtSlot(str)
    def summarize_prompt(self, filepath: str) -> None:
        """Summarize the text that is located in the provided file"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                text_content = f.read()
        except Exception as e:
            self.error_occurred.emit(f"Error reading file: {e}")
            return
        try:
            prompt = (
                "You are a precise summarization engine. You must generate a"
                + "SUMMARY based ONLY on the provided text. Do not use any outside knowledge."
                + "If the provided text contains incorrect information, summarize it exactly "
                + "as written and don't mention the wrong information or its correction.\n\n "
                + text_content
            )
            resp = self.llm.stream_complete(prompt)

            for r in resp:
                self.result_ready.emit(r.delta)
            self.finished_stream.emit()
        except Exception as e:
            self.finished_stream.emit()
            error_message = f"AI Error: {str(e)}"
            if "ConnectionError" in str(e):
                error_message = "Lost connection to AI Engine. Is Ollama running?"

            self.result_ready.emit(error_message)

    # @pyqtSlot(str)
    def overview_prompt(self, sematic_text: str, topic: str) -> None:
        """will make an overview of the presented context"""
        try:
            prompt = (
                "You are a research assistant that has to keep every idea "
                "organized and easy to understand. You are now asked to "
                "create a digestible overview of the provided information "
                "(no external knowledge allowed). You should also filter "
                "irrelevant data based on relevance. If the provided notes "
                "contain completely different topics (e.g. Computer Memory "
                "vs Human Memory), infer the most likely intent, but do "
                "not mix the two topics in a single summary. "
                "This overview should look more like a quick "
                "summary than an actual explanation of what the idea "
                "presented is. Here is the info that can be used:\n"
                f"{sematic_text}"
            )

            resp = self.llm.stream_complete(prompt)

            for r in resp:
                self.result_ready.emit(r.delta)
            self.finished_stream.emit()
        except Exception as e:
            self.finished_stream.emit()
            error_message = f"AI Error: {str(e)}"
            if "ConnectionError" in str(e):
                error_message = "Lost connection to AI Engine. Is Ollama running?"

            self.result_ready.emit(error_message)
