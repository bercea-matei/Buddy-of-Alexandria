# AIWorker.py

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QThread
from llama_index.llms.ollama import Ollama


class AIWorker(QObject):
    """
    Runs the AI query in a separate thread to avoid freezing the GUI.
    """

    result_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, index_manager) -> None:
        super().__init__()
        self._index_manager = index_manager
        self.llm = Ollama(model="phi3:mini", request_timeout=60.0)

    @pyqtSlot(str)
    def run_query(self, user_text):
        """Old rough semantic retreival (deprecated)"""
        try:
            # print(
            #    f"[Thread {QThread.currentThreadId()}] Worker started for query: '{user_text}'"
            # )
            ai_text = self._index_manager.query_question(user_text)
            self.result_ready.emit(ai_text)
        except Exception as e:
            print(f"[Thread {QThread.currentThreadId()}] Error during query: {e}")
            self.error_occurred.emit(str(e))

    @pyqtSlot(str)
    def summarize_prompt(self, filepath):
        """Summarize the content of a file and responding back"""

    @pyqtSlot(str)
    def chating_prompt(self, user_text):
        """Alows the user to ask more complex questions about their own notes"""
