from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QThread


# --- NEW WORKER CLASS ---
class AIWorker(QObject):
    """
    Runs the AI query in a separate thread to avoid freezing the GUI.
    """

    result_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, index_manager):
        super().__init__()
        self._index_manager = index_manager

    @pyqtSlot(str)
    def run_query(self, user_text):
        """This is the slot that will be triggered to start the work."""
        try:
            print(
                f"[Thread {QThread.currentThreadId()}] Worker started for query: '{user_text}'"
            )
            ai_text = self._index_manager.query_question(user_text)
            self.result_ready.emit(ai_text)
        except Exception as e:
            print(f"[Thread {QThread.currentThreadId()}] Error during query: {e}")
            self.error_occurred.emit(str(e))
        finally:
            print(f"[Thread {QThread.currentThreadId()}] Worker finished.")
