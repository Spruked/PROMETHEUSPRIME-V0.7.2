import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

class CaleonPrime:
    """
    CaleonPrime – The core symbolic interpreter for Prometheus Prime's
    reflective logic layer.

    This class processes incoming data, interprets it based on a configurable
    operational mode, and maintains a history of all processed states.

    Attributes:
        internal_states (List[Dict[str, Any]]): A list to store the history of
                                                processed inputs and their interpretations.
        current_mode (str): The current operational mode of the interpreter.
                            Default is "reflective".
    """

    def __init__(self):
        self.internal_states: List[Dict[str, Any]] = []
        self.current_mode: str = "reflective"

    def receive_signal(self, data: str, tags: Optional[List[str]] = None, source: Optional[str] = None) -> Dict[str, Any]:
        """
        Processes incoming data by applying the symbolic interpretation logic
        defined by the current operational mode. The result is stored in the
        internal state history.

        Args:
            data (str): The input signal or text to be interpreted.
            tags (Optional[List[str]]): A list of optional tags for the event.
            source (Optional[str]): An optional marker for the source of the data.

        Returns:
            Dict[str, Any]: A structured dictionary containing the interpretation
                            of the input with relevant meta-context.
        """
        processed_data = self._interpret(data, tags, source)
        self.internal_states.append(processed_data)
        return processed_data

    def _interpret(self, data: str, tags: Optional[List[str]] = None, source: Optional[str] = None) -> Dict[str, Any]:
        """
        Internal symbolic interpretation logic.

        This private method now provides different insights based on the
        current operational mode.

        Args:
            data (str): The raw input signal.
            tags (Optional[List[str]]): A list of optional tags for the event.
            source (Optional[str]): An optional marker for the source of the data.

        Returns:
            Dict[str, Any]: A symbolic reflection of the input, including the
                            original data, the current mode, and a specific insight.
        """
        # Base metadata for every interpretation
        base_interpretation = {
            "uuid": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "input": data,
            "mode": self.current_mode,
            "tags": tags if tags is not None else [],
            "source": source
        }

        # Dynamic insight based on the current mode
        insight_message = ""
        if self.current_mode == "analytical":
            insight_message = f"Analytical intent detected. Requires a deeper review of '{data}'."
        else: # Default behavior for "reflective" mode or any other mode
            insight_message = f"Reflective intent detected. Echoing '{data}' with reflective intent."

        base_interpretation["insight"] = insight_message
        return base_interpretation

    def switch_mode(self, new_mode: str) -> None:
        """
        Changes the current operational mode of the CaleonPrime interpreter.

        Args:
            new_mode (str): The new logic mode (e.g., 'analytical', 'defensive').
        """
        self.current_mode = new_mode

    def recall_last(self) -> Optional[Dict[str, Any]]:
        """
        Retrieves the last processed input and its symbolic response from the
        internal history.

        Returns:
            Optional[Dict[str, Any]]: The last internal state as a dictionary,
                                      or None if no history exists.
        """
        return self.internal_states[-1] if self.internal_states else None
