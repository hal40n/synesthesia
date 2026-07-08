import threading

from syn.config import Config
from syn.core.prompt_loader import load_prompt
from syn.input.factory import create_input_source
from syn.input.static import StaticInputSource
from syn.llm.client import LLMClient
from syn.log.live import LiveLogger
from syn.render.renderer import Renderer
from syn.render.state import ColorState, ColorStateHolder, color_from_output, frame_state

# Neutral cold dim color shown until the first interpretation arrives.
INITIAL_STATE = ColorState(hue=220.0, saturation=0.3, brightness=0.25)


class LiveMode:
    def start(self, session):
        # ---- option validation ----
        if session.seed is not None:
            raise ValueError("[live] --seed is not allowed")

        if session.session_name is None:
            print("[live] unnamed session")

        # ---- init ----
        prompt = load_prompt(Config.PROMPT_LIVE)
        client = LLMClient(
            prompt,
            temperature=Config.LLM_TEMPERATURE_LIVE,
            provider=Config.SYN_LLM_PROVIDER,
            base_url=Config.SYN_LLM_BASE_URL,
            model=Config.SYN_LLM_MODEL,
        )
        source = create_input_source(Config.SYN_INPUT_SOURCE, key=session.key)
        capture = getattr(source, "capture", None)

        print("[live] mode initialized")
        print(f"[live] temperature={Config.LLM_TEMPERATURE_LIVE}")
        print(f"[live] key={session.key}, session={session.session_name}")
        print(f"[live] input source={Config.SYN_INPUT_SOURCE}")

        holder = ColorStateHolder(INITIAL_STATE)
        stop = threading.Event()

        thread = threading.Thread(
            target=self._interpret_loop,
            args=(session, client, source, holder, stop),
            daemon=True,
        )
        thread.start()

        try:
            renderer = Renderer()
            renderer.run(
                lambda: frame_state(
                    holder.get(), capture.rms_now() if capture else None
                )
            )
        finally:
            stop.set()
            thread.join(timeout=2.0)
            if capture is not None:
                capture.stop()
            print("[live] session ended")

    def _interpret_loop(self, session, client, source, holder, stop):
        interval = Config.SYN_AUDIO_WINDOW_SECONDS
        is_static = isinstance(source, StaticInputSource)

        # An audio window is only meaningful once the ring buffer holds
        # one full window of sound; a static observation is ready now.
        if not is_static and stop.wait(interval):
            return

        while not stop.is_set():
            interpreted = self._interpret_once(session, client, source, holder)
            if interpreted and is_static:
                # A fixed observation cannot change: one interpretation
                # defines this session's color.
                return
            if stop.wait(interval):
                return

    def _interpret_once(self, session, client, source, holder) -> bool:
        try:
            llm_input = source.read()
            output = client.interpret(llm_input)
        except Exception as e:
            # Presence over crash: keep the last color, report, move on.
            print(f"[live] interpretation failed, keeping last color: {e}")
            return False

        holder.set(color_from_output(output))

        try:
            logger = LiveLogger()
            logger.write({
                "timestamp": logger.timestamp,
                "mode": "live",
                "session": session.session_name,
                "key": session.key,
                "temperature": Config.LLM_TEMPERATURE_LIVE,
                "llm_output": output.__dict__,
            })
        except Exception as e:
            # The color is already on screen; a lost trace must not
            # kill the interpretation thread.
            print(f"[live] trace logging failed: {e}")
        return True
