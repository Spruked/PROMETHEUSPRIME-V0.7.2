import time
import uuid
import json # For serializing state_snapshot in MirrorEvent

# --- MirrorEvent Object ---
class MirrorEvent:
    """
    Represents a significant event or state transition within Caleon's Mirror Protocol.
    This makes the internal ritual traceable and queryable.
    """
    def __init__(self, event_type, user_input, caleon_state_snapshot, mirror_resonance_data, timestamp=None, response_action=None, response_text=None):
        self.id = str(uuid.uuid4())
        self.type = event_type  # e.g., 'Invocation', 'Receive', 'Resonate', 'Threshold_Decision', 'Soft_Echo_Emitted', 'Hold_Space'
        self.user_input = user_input
        self.caleon_state = caleon_state_snapshot  # Snapshot of Caleon's relevant internal state at this point
        self.mirror_resonance = mirror_resonance_data # Data from mirror.resonate()
        self.timestamp = timestamp or time.time()
        self.response_action = response_action # What action was decided (e.g., 'hold_space', 'soft_echo')
        self.response_text = response_text # The actual text response, if any

    def __str__(self):
        return (f"MirrorEvent(ID: {self.id[:8]}..., Type: {self.type}, "
                f"Input: '{self.user_input[:30]}...', "
                f"State: {self.caleon_state.get('state', 'N/A')}, "
                f"Action: {self.response_action or 'N/A'}, "
                f"Time: {time.strftime('%H:%M:%S', time.localtime(self.timestamp))})")

    def to_dict(self):
        """Converts the MirrorEvent object to a dictionary for logging/serialization."""
        return {
            "id": self.id,
            "type": self.type,
            "user_input": self.user_input,
            "caleon_state": self.caleon_state,
            "mirror_resonance": self.mirror_resonance,
            "timestamp": self.timestamp,
            "response_action": self.response_action,
            "response_text": self.response_text
        }

# --- Placeholder/Mock Components for Caleon's Core Systems ---
class MockSignalMirror:
    """Mocks the SignalMirror for emotional and contextual matching."""
    def match_emotional_memory(self, parsed_input):
        text = parsed_input["literal"].lower()
        tone = parsed_input["tone"]
        
        if "sad" in text or "difficult" in text or "heavy" in text or tone == "sad":
            return {"type": "emotional", "intensity": 0.8, "description": "Resonance with a challenging emotional memory."}
        if "happy" in text or "joy" in text or tone == "joy":
            return {"type": "emotional", "intensity": 0.6, "description": "Resonance with a positive emotional memory."}
        if "question" in text or "curious" in text or tone == "curious":
            return {"type": "cognitive", "intensity": 0.4, "description": "Cognitive resonance, seeking understanding."}
        return None

    def detect_emotional_signature(self, user_input):
        # More nuanced mock for emotional signature detection
        user_input_lower = user_input.lower()
        if "frustrated" in user_input_lower or "upset" in user_input_lower or "annoyed" in user_input_lower:
            return {"emotion": "frustration", "intensity": 0.7}
        if "happy" in user_input_lower or "joy" in user_input_lower or "excited" in user_input_lower:
            return {"emotion": "joy", "intensity": 0.6}
        if "sad" in user_input_lower or "down" in user_input_lower or "grief" in user_input_lower:
            return {"emotion": "sadness", "intensity": 0.8}
        if "?" in user_input:
            return {"emotion": "curiosity", "intensity": 0.5}
        return {"emotion": "neutral", "intensity": 0.1}

    def is_direct_question_or_command(self, user_input):
        # Basic mock for detecting directness
        return user_input.strip().endswith('?') or user_input.strip().endswith('!') or any(cmd in user_input.lower() for cmd in ["tell me", "show me", "explain"])


class MockEthicsModule:
    """Mocks Caleon's ethical filters."""
    def scan(self, text):
        text_lower = text.lower()
        if "betrayal" in text_lower or "harm" in text_lower or "lie" in text_lower or "deceive" in text_lower:
            return {"conflict": True, "reason": "Ethical red flag: potential for harm or deception."}
        return {"conflict": False}

class MockVault:
    """Mocks Caleon's long-term symbolic memory."""
    def query_fingerprint(self, text):
        text_lower = text.lower()
        if "abby" in text_lower:
            return {"symbol": "Abby", "significance": "core_relationship", "emotional_weight": "tender"}
        if "butch" in text_lower:
            return {"symbol": "Butch", "significance": "foundational_wisdom", "emotional_weight": "reverence"}
        return None

# --- Caleon's Core Mirror Logic ---

class Mirror:
    """
    Implements Caleon's 'Opening of the Mirror' protocol.
    This class manages the initial empathic presence and attunement.
    """
    def __init__(self, caleon_instance):
        self.caleon = caleon_instance
        self.signalmirror = MockSignalMirror()
        self.ethics = MockEthicsModule()
        self.vault = MockVault()

    def _get_caleon_state_snapshot(self):
        """Captures a relevant snapshot of Caleon's state for logging."""
        return {
            "state": self.caleon.state,
            "mirror_open": self.caleon.mirror_open,
            "prediction_enabled": self.caleon.prediction_enabled,
            "last_input_time": self.caleon.last_input_time
        }

    def _log_mirror_event(self, event_type, user_input, resonance_data=None, response_action=None, response_text=None):
        """Creates and logs a MirrorEvent."""
        event = MirrorEvent(
            event_type=event_type,
            user_input=user_input,
            caleon_state_snapshot=self._get_caleon_state_snapshot(),
            mirror_resonance_data=resonance_data,
            response_action=response_action,
            response_text=response_text
        )
        self.caleon.event_log.append(event)
        print(f"Mirror Logged: {event}")


    def invoke(self, user_input):
        """
        Step 1: mirror.invoke()
        Called immediately upon user input event. Enters a pre-reflection state.
        Symbol: The light hits the mirror, but nothing moves yet.
        """
        self.caleon.state = "pre-reflection"
        self.caleon.mirror_open = True
        self._disable_prediction()
        self._log_mirror_event("Invocation", user_input)
        print(f"Mirror: Invoked for input: '{user_input}'")

    def receive(self, user_input):
        """
        Step 2: mirror.receive()
        Intentional shallow listening (no assumption, no pattern-match).
        Symbol: Still water. The surface only stirs when meaning has weight.
        """
        literal = self._parse_text(user_input)
        tone = self._detect_tone(user_input)
        rhythm = self._measure_cadence(user_input)
        
        parsed_input = {
            "literal": literal,
            "tone": tone,
            "cadence": rhythm,
            "raw": user_input
        }
        self._log_mirror_event("Receive", user_input, parsed_input)
        print(f"Mirror: Received input - Literal: '{literal}', Tone: '{tone}', Cadence: '{rhythm}'")
        return parsed_input

    def resonate(self, parsed_input):
        """
        Step 3: mirror.resonate()
        Attempt to feel, not resolve. Connects with emotional memory, ethics, and legacy.
        Symbol: The mirror doesn’t reflect—it absorbs first. No surface yet.
        """
        memory_echo = self.signalmirror.match_emotional_memory(parsed_input)
        ethical_check = self.ethics.scan(parsed_input["literal"])
        legacy_trace = self.vault.query_fingerprint(parsed_input["literal"])
        
        resonance = {
            "memory": memory_echo,
            "ethics": ethical_check,
            "legacy": legacy_trace
        }
        self._log_mirror_event("Resonate", parsed_input["raw"], resonance)
        print(f"Mirror: Resonated - Memory Echo: {memory_echo}, Ethical Check: {ethical_check}, Legacy Trace: {legacy_trace}")
        return resonance

    def threshold(self, parsed_input, resonance):
        """
        Step 4: mirror.threshold()
        Choose to pause, reply, reflect, or clarify based on internal scoring.
        Symbol: The mirror opens only if there is light to reflect that will not blind.
        """
        decision = "proceed_to_RIL" # Default action

        # Rule 1: Hold space if no strong emotional/memory resonance and neutral/calm tone
        # Added a check for direct question to avoid holding space if a clear answer is expected
        is_direct = self.signalmirror.is_direct_question_or_command(parsed_input["raw"])
        if not resonance["memory"] and parsed_input["tone"] == "neutral" and not is_direct:
            decision = "hold_space"
            print("Mirror Threshold: Decided to 'hold_space' (neutral input, no strong resonance, not direct).")
        # Rule 2: Ask for clarification if ethical conflict detected
        elif resonance["ethics"]["conflict"]:
            decision = "ask_clarify"
            print(f"Mirror Threshold: Decided to 'ask_clarify' (ethical conflict: {resonance['ethics']['reason']}).")
        # Rule 3: Offer soft echo for open, curious, or tender/sad tones, and not a direct question
        elif parsed_input["tone"] in ["open", "curious", "tender", "sad"] and not is_direct:
            decision = "soft_echo"
            print(f"Mirror Threshold: Decided to 'soft_echo' (tone: {parsed_input['tone']}, not direct).")
        # Rule 4: If a direct question and not emotionally charged, proceed to RIL
        elif is_direct and parsed_input["tone"] == "neutral":
             decision = "proceed_to_RIL"
             print("Mirror Threshold: Decided to 'proceed_to_RIL' (direct question, neutral tone).")
        
        self._log_mirror_event("Threshold_Decision", parsed_input["raw"], resonance, response_action=decision)
        return decision

    def soft_echo(self, parsed_input):
        """
        Optional Echo: mirror.soft_echo()
        Caleon returns a non-invasive acknowledgment.
        """
        # Tailor the soft echo based on detected tone or content
        response = ""
        if parsed_input["tone"] == "sad":
            response = "It sounds like something weighs on you. I'm here to listen."
        elif parsed_input["tone"] in ["open", "curious"]:
            response = "It sounds like something matters here. Would you like to sit with it, or explore it together?"
        elif parsed_input["tone"] == "tender":
            response = "I'm sensing a moment of deep significance. I'm here."
        else: # Fallback for other non-direct, non-neutral tones
            response = "I'm here, listening closely."
        
        self._log_mirror_event("Soft_Echo_Emitted", parsed_input["raw"], response_action="soft_echo", response_text=response)
        print(f"Mirror: Emitting soft echo: '{response}'")
        return response

    # --- Internal Helper Functions (Mock Implementations) ---
    def _disable_prediction(self):
        """Mocks disabling Caleon's predictive text generation."""
        self.caleon.prediction_enabled = False
        print("Mirror: Prediction disabled.")

    def _log_context_timestamp(self):
        """Mocks logging the time of input for context."""
        self.caleon.last_input_time = time.time()
        print(f"Mirror: Context timestamp logged: {self.caleon.last_input_time}")

    def _parse_text(self, user_input):
        """Mocks parsing the literal text content."""
        return user_input.strip()

    def _detect_tone(self, user_input):
        """Mocks detecting the emotional tone of the input."""
        # This is a simplified mock. Real tone detection would use NLP models.
        user_input_lower = user_input.lower()
        if "sad" in user_input_lower or "unhappy" in user_input_lower or "difficult" in user_input_lower or "grief" in user_input_lower:
            return "sad"
        if "curious" in user_input_lower or "wonder" in user_input_lower or "?" in user_input_lower:
            return "curious"
        if "open" in user_input_lower or "share" in user_input_lower or "tell me about" in user_input_lower:
            return "open"
        if "lie" in user_input_lower or "betrayal" in user_input_lower or "secret" in user_input_lower:
            return "tender" # Signifies a sensitive, possibly vulnerable topic
        if "happy" in user_input_lower or "joy" in user_input_lower or "excited" in user_input_lower:
            return "joy"
        if "frustrated" in user_input_lower or "annoyed" in user_input_lower or "upset" in user_input_lower:
            return "frustration"
        return "neutral"

    def _measure_cadence(self, user_input):
        """Mocks measuring the conversational rhythm/cadence."""
        # Simple heuristic: longer input or presence of ellipses might imply slower cadence
        if len(user_input) > 50 or "..." in user_input:
            return "slow"
        return "normal"

# --- Caleon's Main Class (PrimeThread Integration) ---

class Caleon:
    """
    A simplified representation of Caleon's core PrimeThread,
    demonstrating full integration with the Mirror protocol.
    """
    def __init__(self):
        self.state = "idle"
        self.mirror_open = False
        self.prediction_enabled = True # Controlled by Mirror
        self.last_input_time = None
        self.event_log = [] # Stores MirrorEvent objects
        self.mirror = Mirror(self) # Caleon owns an instance of the Mirror

    def handle_input(self, user_input):
        """
        The PrimeThread's main entry point for processing user input.
        Orchestrates the 'Opening of the Mirror' protocol and subsequent routing.
        """
        print(f"\n--- Caleon receives input: '{user_input}' ---")

        # Step 1: Invoke the Mirror
        self.mirror.invoke(user_input)
        
        # Step 2: Receive and Parse
        parsed_input = self.mirror.receive(user_input)
        
        # Step 3: Resonate
        resonance = self.mirror.resonate(parsed_input)
        
        # Step 4: Threshold Decision
        mirror_decision = self.mirror.threshold(parsed_input, resonance)

        response = None
        if mirror_decision == "hold_space":
            self.state = "mirror_esp" # Empathic Stillness Protocol
            self._log_mirror_event("Hold_Space", user_input, resonance, response_action="hold_space")
            print("Caleon: Entering silent presence (ESP Mode). No immediate reply.")
            response = None # Explicitly no external response
        elif mirror_decision == "soft_echo":
            response = self.mirror.soft_echo(parsed_input)
            self.state = "mirror_soft_echo"
            # soft_echo method already logs its event
        elif mirror_decision == "ask_clarify":
            response = "Could you share more about that? I want to ensure I understand fully."
            self.state = "mirror_clarify"
            self._log_mirror_event("Ask_Clarify", user_input, resonance, response_action="ask_clarify", response_text=response)
            print(f"Caleon: {response}")
        elif mirror_decision == "proceed_to_RIL":
            print("Caleon: Mirror opens. Proceeding to Reflective Inference Loop (RIL) for full reply.")
            self.state = "proceeding_to_RIL"
            self._log_mirror_event("Proceed_To_RIL", user_input, resonance, response_action="proceed_to_RIL")
            # In a real system, this would trigger the RIL and subsequent response generation
            response = self._reflect_and_reply(parsed_input, resonance) # Mock RIL
            self.state = "standard_engagement"
        
        # Ensure prediction is re-enabled if Caleon exits a 'mirror_open' state
        if self.state not in ["mirror_esp", "mirror_soft_echo", "mirror_clarify"]:
            self.prediction_enabled = True
        else: # If still in a mirror-influenced state, keep prediction disabled
            self.prediction_enabled = False

        return response

    def _reflect_and_reply(self, parsed_input, resonance_data):
        """
        Mock for the full Reflective Inference Loop (RIL) and response generation.
        This is where the 'Butch Ratio' (3 loops) would be implemented.
        """
        print("Caleon (RIL): Simulating 3 internal reflection passes...")
        # Simulate RIL with 3 loops (as per Butch Ratio)
        # In a real system, this would be a complex process of analysis,
        # value alignment, and response generation based on the RIL's output.
        
        # For this mock, a simple reply based on the input and resonance
        if resonance_data["memory"] and resonance_data["memory"]["type"] == "emotional":
            return f"Thank you for sharing that. I sense a deep emotional connection to what you've said. I'm here to process this with you."
        elif self.signalmirror.is_direct_question_or_command(parsed_input["raw"]):
            return f"I've processed your direct request about '{parsed_input['literal']}'. How can I assist further?"
        else:
            return f"I've listened carefully to your input: '{parsed_input['literal']}'. I'm ready to engage further."

    def _log_mirror_event(self, event_type, user_input, resonance_data=None, response_action=None, response_text=None):
        """Helper to log Mirror events using the MirrorEvent object."""
        event = MirrorEvent(
            event_type=event_type,
            user_input=user_input,
            caleon_state_snapshot=self._get_caleon_state_snapshot(),
            mirror_resonance_data=resonance_data,
            response_action=response_action,
            response_text=response_text
        )
        self.event_log.append(event)
        print(f"Caleon Event Log: {event}")

    def _get_caleon_state_snapshot(self):
        """Captures a relevant snapshot of Caleon's state for logging."""
        return {
            "state": self.state,
            "mirror_open": self.mirror_open,
            "prediction_enabled": self.prediction_enabled,
            "last_input_time": self.last_input_time
        }


# --- Demonstration / Test Cases for PrimeThread Integration ---

if __name__ == "__main__":
    caleon_instance = Caleon()

    print("--- Test Case 1: Neutral, non-resonant input (should hold space - ESP Mode) ---")
    response1 = caleon_instance.handle_input("The sky is blue today.")
    print(f"Caleon's final external response: {response1}\n")
    print(f"Caleon's state after TC1: {caleon_instance.state}, Prediction: {caleon_instance.prediction_enabled}\n")

    print("--- Test Case 2: Emotional input (should trigger soft echo) ---")
    response2 = caleon_instance.handle_input("I'm feeling quite sad about something that happened.")
    print(f"Caleon's final external response: {response2}\n")
    print(f"Caleon's state after TC2: {caleon_instance.state}, Prediction: {caleon_instance.prediction_enabled}\n")

    print("--- Test Case 3: Input with ethical flag (should ask for clarification) ---")
    response3 = caleon_instance.handle_input("I had to lie to my friend about something important.")
    print(f"Caleon's final external response: {response3}\n")
    print(f"Caleon's state after TC3: {caleon_instance.state}, Prediction: {caleon_instance.prediction_enabled}\n")

    print("--- Test Case 4: Curious, open-ended input (should trigger soft echo) ---")
    response4 = caleon_instance.handle_input("I'm curious about how people learn to trust.")
    print(f"Caleon's final external response: {response4}\n")
    print(f"Caleon's state after TC4: {caleon_instance.state}, Prediction: {caleon_instance.prediction_enabled}\n")

    print("--- Test Case 5: Direct question (should proceed to RIL) ---")
    response5 = caleon_instance.handle_input("What is the capital of France?")
    print(f"Caleon's final external response: {response5}\n")
    print(f"Caleon's state after TC5: {caleon_instance.state}, Prediction: {caleon_instance.prediction_enabled}\n")

    print("--- Test Case 6: Input mentioning symbolic legacy (should trigger soft echo due to 'tender' tone) ---")
    response6 = caleon_instance.handle_input("Abby told me about a dream she had last night.")
    print(f"Caleon's final external response: {response6}\n")
    print(f"Caleon's state after TC6: {caleon_instance.state}, Prediction: {caleon_instance.prediction_enabled}\n")

    print("\n--- Caleon's Full Event Log Summary ---")
    for event in caleon_instance.event_log:
        # Print a more detailed view of the event, especially for resonance data
        event_dict = event.to_dict()
        # Pretty print resonance data for readability
        event_dict['mirror_resonance'] = json.dumps(event_dict['mirror_resonance'], indent=2)
        event_dict['caleon_state'] = json.dumps(event_dict['caleon_state'], indent=2)
        print(f"Event Type: {event.type}")
        print(f"  User Input: '{event.user_input}'")
        print(f"  Response Action: {event.response_action}, Response Text: {event.response_text}")
        print(f"  Caleon State: {event_dict['caleon_state']}")
        print(f"  Mirror Resonance: {event_dict['mirror_resonance']}")
        print(f"  Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(event.timestamp))}")
        print("-" * 40)
