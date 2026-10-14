# Licensing and third-party attribution

## Original project contributions

Original NW-A306 Open source code, tests, tools, configuration and documentation
are offered under the GNU General Public License, version 2 or, at your option,
any later version (`GPL-2.0-or-later`). The complete GPL v2 text is in
[LICENSE](../LICENSE), copied verbatim from the
[Free Software Foundation's GNU site](https://www.gnu.org/licenses/old-licenses/gpl-2.0.txt).
The choice of version 2 or later is the project's grant; the license text itself
is the published version 2, including its application guidance.

This policy covers the original contributions in `README.md`, the public
Markdown reports in `docs/`, the Python files in `tools/` and `tests/`, the
standalone `tests/asan_runtime_probe.c` and `tests/hosted_sdl_smoke.c` helpers,
and `.gitignore`. Source files carry SPDX notices. This central notice covers
the original documentation without repeating a license block in every report.

The policy also covers the original configuration in
`tools/m3-toolchain.lock.json`, `tools/m5-linux.lock.json` and
`tools/m9-userspace-contract.json`. These remain strict JSON; their license
notice is recorded here rather than added as an unsupported schema field.
Package names, URLs, checksums and source-derived register facts identify inputs;
they do not grant rights to those packages or sources.

The grant applies to original project contributions for which the maintainer
holds the necessary rights. It does not relicense attributed quotations,
third-party excerpts, upstream code or external artifacts. Their existing
notices and terms continue to apply. No new copyright holder or ownership
history is asserted by these notices.

## Rockbox changes

The three patches in `tools/` modify
[Rockbox revision afe91f1dfb1c9d90da928bb2bf8a0fbc6957ff09](https://github.com/Rockbox/rockbox/tree/afe91f1dfb1c9d90da928bb2bf8a0fbc6957ff09).
They carry GPL-2.0-or-later declarations. Apply them in this order:

1. `rockbox-opus-correctness.patch`
2. `rockbox-playback-integration.patch`
3. `rockbox-hosted-decoder-error.patch`

The upstream notices in the affected files remain intact after patching.
Their copyright attributions are:

| Upstream file | Copyright notice in the pinned source |
| --- | --- |
| `lib/rbcodec/codecs/opus.c` | 2012 Frederik M.J. Vestre; based on the 2006 Speex interface by Frederik M.J. Vestre and the 2002 Vorbis interface by Björn Stenberg |
| `lib/rbcodec/test/warble.c` | 2011 Sean Bartell |
| `lib/rbcodec/metadata/ogg.c` | 2005 Dave Chapman |
| `apps/playback.c` | 2005-2007 Miika Pekkarinen; 2007-2008 Nicolas Pennequin; 2011 Michael Sevakis |
| `apps/playback.h` | 2005 Miika Pekkarinen |
| `apps/action.c` | 2006 Jonathan Gordon; 2017 William Wilgus |

`lib/rbcodec/test/warble.make` and `firmware/export/config/sdlapp.h` have no
individual copyright/license block in the pinned files. They remain part of
the Rockbox source distribution; no independent permissive license is inferred.

`tests/hosted_playback.c`, `tests/linux_evdev_touch.c` and
`tests/linux_drm_scanout.c` retain their GPL-2.0-or-later declarations. The
original standalone helpers listed above now carry the same SPDX identifier
under the project policy.

`COPYING` is retained unchanged as a verbatim copy of the pinned Rockbox
`docs/COPYING`, SHA-256
`a45932c79317d15116eadbf1c9c6fc59117ec3c4621db3a876066defa723963b`.
It contains the same GPL v2 terms; its historical formatting/address and omission
of the application-guidance appendix do not create a separate project license.
`LICENSE` supplies the complete current GNU-published text. Rockbox's
`docs/LICENSES` and individual component notices also apply to a full
build. This repository distributes patches and test sources, not a complete
Rockbox source or binary release. Any later binary distribution needs the
corresponding source, license notices and other obligations for its actual
components, including statically linked libraries.

## Referenced sources and private inputs

Sony's shared GPL archive is a research input. Its components retain their
own notices; its availability grants no general right to redistribute Sony
firmware, DSP payloads, calibration, APKs, effects or services. The reports
distinguish source interfaces from proprietary implementations and unresolved
provisioning rights. Sony source and binary artifacts are excluded here.

The generic prototype uses Linux, QEMU, BusyBox, glibc, musl, ALSA and SDL.
Their pinned inputs and licensing families are recorded in the
[Linux prototype report](m5-linux-prototype.md#exact-system-and-dependency-provenance).
Downloaded packages, extracted DRM UAPI headers, generated media and compiled
outputs are private build inputs or results, not publication candidates.
Books, training material, FCC PDFs and private device evidence are cited as
references rather than redistributed. Historical third-party Walkman decoder
source was inspected for comparison and has not been imported.

Contributions must identify their origin and license and retain applicable
notices. Do not contribute proprietary firmware, private logs, identifiers or
material whose redistribution rights are unresolved.
