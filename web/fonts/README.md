# Embedded fonts

`wave-calculator.html` embeds its two typefaces as base64 `@font-face` rules, so
the file renders the same offline with **no network request** — which is what
lets it be deposited as a self-contained research artifact.

| Font | Use | Weights | License | © |
|---|---|---|---|---|
| **IBM Plex Mono** | body / UI / canvas labels | 400, 500, 600 | SIL OFL 1.1 | 2017 IBM Corp. |
| **Fraunces** | the `h1` display title | 600 | SIL OFL 1.1 | 2020 The Fraunces Project Authors |

Only the **Latin** subset is embedded. Non-Latin glyphs used in the UI (the
Greek `ω`, sub/superscripts, and math/UI symbols) fall back to a system font, as
they did with the original webfont.

The SIL Open Font License 1.1 permits embedding and redistribution; its full
text and the reserved font names are included here as required:

- `IBMPlexMono-OFL.txt`
- `Fraunces-OFL.txt`

woff2 sources: the `@fontsource/ibm-plex-mono` and `@fontsource/fraunces`
packages (Latin subsets).
