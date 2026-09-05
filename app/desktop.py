"""Native desktop shell for video2text.

Runs the FastAPI server in a background thread and opens it in a native
macOS window via pywebview (WKWebView), so the app behaves like a normal
double-clickable desktop app instead of "open a browser tab".
"""
import socket
import threading

import uvicorn


class Api:
    """Exposed to the page as `window.pywebview.api.*`. Lets the frontend
    trigger a native macOS "Open" dialog, which — unlike a browser
    <input type=file> or drag-and-drop — hands back a real filesystem path.
    That lets a conversion job read the video directly from wherever it
    already lives instead of first copying its (often 100s of MB) contents
    into our own upload folder just to immediately delete them again."""

    def pick_video(self):
        import webview

        result = webview.windows[0].create_file_dialog(
            webview.OPEN_DIALOG,
            allow_multiple=False,
            file_types=("동영상 오디오 (*.mp4;*.mov;*.m4v;*.mkv;*.wav;*.m4a;*.mp3)", "모든 파일 (*.*)"),
        )
        return result[0] if result else None


def _find_free_port(default: int = 8765) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", default))
            return default
        except OSError:
            s.bind(("127.0.0.1", 0))
            return s.getsockname()[1]


def main():
    from .main import app  # noqa: WPS433 (local import keeps startup snappy)

    port = _find_free_port()

    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config)

    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    import time

    for _ in range(100):
        if server.started:
            break
        time.sleep(0.05)

    import webview

    # Explicitly target whichever display the user is actually looking at —
    # left to its own defaults, pywebview can place the window on a
    # different monitor than the user's current focus, which looks like
    # "nothing opened" or "can't get back to the app" (e.g. after a native
    # file-picker sheet closes on a screen the window isn't on).
    #
    # AppKit's NSScreen.mainScreen() is "the screen with the current
    # keyboard focus / mouse", which is a better proxy for "what the user
    # is looking at" than NSScreen.screens()[0] (the hardware-designated
    # primary display, which can be a different monitor).
    screen = None
    try:
        import AppKit

        main = AppKit.NSScreen.mainScreen()
        if main is not None:
            mx, my = main.frame().origin.x, main.frame().origin.y
            screen = next(
                (s for s in webview.screens if s.x == mx and s.y == my),
                None,
            )
    except Exception:
        pass
    if screen is None:
        try:
            screen = webview.screens[0]
        except Exception:
            pass

    window = webview.create_window(
        "video2text",
        f"http://127.0.0.1:{port}",
        width=980,
        height=880,
        min_size=(720, 600),
        x=80,
        y=60,
        screen=screen,
        js_api=Api(),
    )
    webview.start()

    server.should_exit = True
    thread.join(timeout=5)


if __name__ == "__main__":
    main()
