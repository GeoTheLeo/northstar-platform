BASE_DIR = Path(__file__).resolve().parents[2]

css = (
    BASE_DIR / "assets" / "styles.css"
).read_text(encoding="utf-8")

st.markdown(
    f"<style>{css}</style>",
    unsafe_allow_html=True,
)