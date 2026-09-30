import os

from dotenv import load_dotenv

load_dotenv(override=True)

from app import create_app  # noqa: E402
from app.config import Config, detect_lan_ip  # noqa: E402

app = create_app()

if __name__ == "__main__":
    cfg = Config()
    port = int(os.getenv("PORT", "5000"))
    print(f"[ViabilizA+] LAN IP: {detect_lan_ip()}")
    print(f"[ViabilizA+] QR / Frontend: {cfg.FRONTEND_BASE_URL}")
    print(f"[ViabilizA+] CORS: {', '.join(cfg.CORS_ORIGINS)}")
    use_reloader = os.getenv("FLASK_USE_RELOADER", "0") == "1"
    app.run(
        host="0.0.0.0",
        port=port,
        debug=app.config["DEBUG"],
        use_reloader=use_reloader,
        threaded=True,
    )
