from syn.modes.research import ResearchMode
from syn.modes.live import LiveMode


class Session:
    """
    Session represents a single syn execution context.

    - Mode is fixed at startup.
    - Session holds contextual information (key, seed, session name).
    - Session itself does not perform interpretation or rendering.
    """

    def __init__(
        self,
        mode: str,
        key: str | None = None,
        seed: int | None = None,
        session_name: str | None = None,
    ):
        self.mode_name = mode
        self.key = key
        self.seed = seed
        self.session_name = session_name

        self.mode = self._create_mode(mode)

    def _create_mode(self, mode: str):
        if mode == "research":
            return ResearchMode()
        elif mode == "live":
            return LiveMode()
        else:
            # This should normally never happen because CLI validates modes,
            # but we fail explicitly to preserve correctness.
            raise ValueError(f"Invalid session mode: {mode}")

    def start(self):
        """
        Start the session.

        Delegates execution to the selected mode.
        """
        self.mode.start(self)
