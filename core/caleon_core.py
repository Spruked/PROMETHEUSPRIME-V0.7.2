# caleon_core.py

class CaleonPrime:
    """
    CaleonPrime – Core symbolic interpreter for Prometheus Prime's reflective logic layer.

    Responsibilities:
    - Process and symbolically reflect on incoming data.
    - Maintain an internal log of processed states.
    - Support dynamic operational modes (e.g., 'reflective', 'introspective').
    """

    def __init__(self):
        self.internal_states = []
        self.current_mode = "reflective"

    def receive_signal(self, data):
        """
        Process incoming data through the interpretive lens of the current mode.
        Stores the result in internal state history.

        Args:
            data (str): The input signal or text to be interpreted.

        Returns:
            dict: A structured interpretation with meta-context.
        """
        processed = self._interpret(data)
        self.internal_states.append(processed)
        return processed

    def _interpret(self, data):
        """
        Internal symbolic interpretation logic. Can be overridden for richer insight generation.

        Args:
            data (str): The raw input signal.

        Returns:
            dict: Symbolic reflection on the input.
        """
        return {
            "input": data,
            "mode": self.current_mode,
            "insight": f"Echoing '{data}' with reflective intent."
        }

    def switch_mode(self, new_mode):
        """
        Change the current operating mode of CaleonPrime.

        Args:
            new_mode (str): The new logic mode (e.g., 'analytical', 'defensive').
        """
        self.current_mode = new_mode

    def recall_last(self):
        """
        Retrieve the last processed input and its symbolic response.

        Returns:
            dict or None: The last internal state, or None if no history exists.
        """
        return self.internal_states[-1] if self.internal_states else None
