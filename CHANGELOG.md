# Changelog

## 0.1.0 — 2026-10-08 (preview)

- Import SDL2 headers 2.33.0 and library source from bdgscotland's AmigaOS3
  port at `1eefa8f35c5ad4b63fa835e251e801a9315dff5c`.
- Remove the invalid Picasso96API-to-CyberGraphX library-base fallback.
- Use clipped, client-relative WritePixelArray updates through the window's
  layered RastPort; remove direct RTG bitmap writes and implicit RTG scaling.
- Package the 68030+ static libraries, headers, source patch, small window
  example, pinned build wrapper, checksums and A4000TX acceptance evidence.
- Disable upstream file-debug logging in the release build. Library remains
  `-O0`; ARM offloading is application-owned and not part of this SDL build.
- Rebuild archives from scratch to prevent duplicate C2P assembly members;
  both relinked diagnostics are byte-identical to the hardware-tested programs.
