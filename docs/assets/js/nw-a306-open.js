/* SPDX-License-Identifier: GPL-2.0-or-later */
(() => {
  'use strict';
  document.documentElement.classList.add('js');
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));
  const repository = 'https://github.com/gblongiu/nw-a306-open';
  const doc = name => `${repository}/blob/main/docs/${name}`;
  const announce = message => { $('#liveStatus').textContent = message; };

  // All figures are transcription of recorded results, not a browser benchmark.
  const codecData = {
    wav: { result: 'Exact', unit: 'PCM', category: 'REFERENCE COMPARISON', rate: '44.1 kHz', frames: '99,226', description: 'Every captured music sample matches the WAV reference.', note: 'Exact fixture reproduction in the generic ARM64 guest does not establish physical output fidelity on the Sony.' },
    flac: { result: 'Exact', unit: 'PCM', category: 'REFERENCE COMPARISON', rate: '44.1 kHz', frames: '99,226', description: 'Lossless FLAC decoding matches the reference music samples.', note: 'This is a recorded software-path result in the generic ARM64 guest, not a measurement of Sony audio hardware.' },
    opus: { result: '68.79', unit: 'dB', category: 'REFERENCE SIGNAL-TO-NOISE RATIO', rate: '48 kHz', frames: '108,001', description: 'Native-rate Opus passes the recorded reference comparison.', note: 'Recorded peak error: 5 s16 units. Forced resampling failed a separate comparison; chained Opus remains unsupported.' }
  };
  // Presentation diagrams describe format mechanics, not the measured fixtures.
  const codecViews = {
    wav: {
      kind: 'UNCOMPRESSED PCM', title: 'Samples, directly.',
      input: 'PCM samples', process: 'Read samples', output: 'PCM output',
      summary: 'The PCM WAV fixture stores sample values directly. FLAC made from the same PCM can recover identical samples.'
    },
    flac: {
      kind: 'LOSSLESS CODING', title: 'Different storage. Same samples.',
      input: 'FLAC frames', process: 'Lossless decode', output: 'Identical PCM',
      summary: 'Prediction plus an exact residual is one FLAC coding method. This illustrative reconstruction preserves every sample; it is not a parsed FLAC bitstream.'
    },
    opus: {
      kind: 'LOSSY CODING', title: 'Packets into playback.',
      input: 'Opus packets', process: 'Lossy decode', output: 'PCM to compare',
      summary: 'The packet diagram explains the decoding path, not a measured waveform or bitrate. Fidelity is described by the recorded comparison, not this drawing.'
    }
  };
  const hardwareData = {
    soc: { category: 'APPLICATION PROCESSOR', name: 'QCS2290', description: 'A visible Qualcomm marking narrows the processor family. The generic ARM64 prototype exercises the software architecture, not this physical chip.', known: 'Marking visible on the FCC sample.', missing: 'Selected board configuration, boot handoff and peripheral bindings.' },
    pmic: { category: 'POWER-MANAGEMENT IC', name: 'PM4125', description: 'The visible PM4125 marking narrows the power-management research. A component identity does not reveal Sony’s regulator settings or protection policy.', known: 'Marking visible on the FCC sample.', missing: 'Genuine rail map, battery profile, charging limits and thermal/watchdog ownership.' },
    storage: { category: 'SAMSUNG STORAGE FAMILY', name: 'KLMBG2JETD', description: 'The photographed storage marking directs research toward eMMC and SDHCI. Android A/B slots are not the same as eMMC hardware boot regions.', known: 'Family marking on the FCC sample; exact variant and owner-board equivalence remain limited.', missing: 'Selected storage configuration, actual boot-region use and preservation of unique provisioning.' }
  };
  const architectures = {
    virtual: { badge: 'VERIFIED VIRTUAL PATH', lead: 'A minimal Linux guest starts Rockbox without Android userspace.', foot: 'No Android userspace, network, disk, USB or physical-device passthrough in the recorded guest.', nodes: [
      ['01 / ENTRY', 'QEMU virt', 'Generic AArch64 machine', 'Recorded', false],
      ['02 / KERNEL', 'ARM64 Linux', 'Alpine kernel + BusyBox initramfs', 'Recorded', false],
      ['03 / PLAYER', 'Rockbox', 'SDL application + codecs', 'Recorded', false],
      ['04 / INTERFACES', 'Virtual devices', 'ALSA · evdev · DRM/KMS', 'Recorded', false]
    ] },
    target: { badge: 'PROPOSED SONY PATH / NOT ESTABLISHED', lead: 'The stock-kernel direction is a research candidate, not a verified entry point.', foot: 'Non-Android init support does not establish accepted ramdisk/rootfs selection. Selected DT, firmware, calibration and restoration remain missing.', nodes: [
      ['01 / ENTRY', 'Accepted startup', 'An applicable Sony execution path', 'Unresolved', true],
      ['02 / KERNEL', 'Selected kernel + DT', 'Authentic image and board configuration', 'Unresolved', true],
      ['03 / PLAYER', 'Minimal userspace', 'Protection + firmware + Rockbox', 'Contract tested; target unverified', true],
      ['04 / INTERFACES', 'Physical hardware', 'Panel · input · storage · audio', 'Unvalidated', true]
    ] }
  };
  const failures = {
    android: { number: '01 / 06', depth: 'OPERATING-SYSTEM FAILURE', title: 'Android will not start.', description: 'Intact stock recovery is a possible remaining route, but applicable entry and accepted reinstall procedures are not established.', requirement: 'An authentic accepted package, independently reachable recovery and documented same-board restoration coverage.', fault: 4 },
    slots: { number: '02 / 06', depth: 'BOTH SOFTWARE BOOT SLOTS', title: 'Neither slot starts.', description: 'A/B partition names do not prove that an independent fallback survives both failed slots or shared metadata damage.', requirement: 'Actual recovery placement, surviving loader dependencies, permitted entry and a matching accepted image set.', fault: 3 },
    avb: { number: '03 / 06', depth: 'RECOVERY OR VERIFIED-BOOT METADATA', title: 'The trust chain breaks.', description: 'A reachable fastboot-like interface cannot be assumed to survive damaged recovery. Userspace fastboot may depend on it.', requirement: 'An entry independent of damaged recovery, accepted matching images and applicable rollback constraints.', fault: 2 },
    partition: { number: '04 / 06', depth: 'STORAGE METADATA FAILURE', title: 'The partition map fails.', description: 'A working storage component is not enough when GPT or dynamic-partition metadata no longer describes usable images.', requirement: 'An authenticated reconstruction method, exact layout and explicit exclusions for per-device data.', fault: 1 },
    loader: { number: '05 / 06', depth: 'EARLY-BOOT FAILURE', title: 'Linux never gets control.', description: 'Generic Qualcomm ROM/service behavior establishes no enabled, reachable or authenticated restoration route on this Walkman.', requirement: 'Device-applicable early entry, an accepted matching loader and genuine original-board restoration resources.', fault: 0 },
    unique: { number: '06 / 06', depth: 'CALIBRATION OR SECURITY PROVISIONING', title: 'Unique state is lost.', description: 'Another player’s calibration, keys or protected state cannot be treated as a replacement for this board’s own provisioning.', requirement: 'A verified preservation or regeneration method and objective criteria for restored stock behavior.', fault: 0 }
  };

  // Arrow, Home and End navigation is shared by each real tab interface.
  function bindTabs(selector, callback) {
    const buttons = $$(selector);
    const select = button => {
      buttons.forEach(item => {
        const selected = item === button;
        item.setAttribute('aria-selected', String(selected));
        item.tabIndex = selected ? 0 : -1;
      });
      callback(button);
    };
    buttons.forEach((button, index) => {
      button.addEventListener('click', () => select(button));
      button.addEventListener('keydown', event => {
        let target;
        if (event.key === 'ArrowRight' || event.key === 'ArrowDown') target = (index + 1) % buttons.length;
        if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') target = (index + buttons.length - 1) % buttons.length;
        if (event.key === 'Home') target = 0;
        if (event.key === 'End') target = buttons.length - 1;
        if (target === undefined) return;
        event.preventDefault();
        select(buttons[target]);
        buttons[target].focus();
      });
    });
  }
  let activeCodec = 'wav';
  bindTabs('[data-codec]', button => {
    activeCodec = button.dataset.codec;
    const data = codecData[activeCodec];
    const value = $('#codecResult');
    value.replaceChildren(document.createTextNode(data.result));
    const unit = document.createElement('span');
    unit.textContent = data.unit;
    value.append(unit);
    $('#codecCategory').textContent = data.category;
    $('#codecRate').textContent = data.rate;
    $('#codecFrames').textContent = data.frames;
    $('#codecDescription').textContent = data.description;
    $('#codecNote').textContent = data.note;
    $('#scopeFormat').textContent = activeCodec.toUpperCase();
    const view = codecViews[activeCodec];
    $('.codec-study').dataset.format = activeCodec;
    $('#scopeKind').textContent = view.kind;
    $('#scopeTitle').textContent = view.title;
    $('#scopeInput').textContent = view.input;
    $('#scopeProcess').textContent = view.process;
    $('#scopeOutput').textContent = view.output;
    $('#scopeSummary').textContent = view.summary;
    $('#codecFormatLink').hidden = activeCodec !== 'flac';
    $('#codecPanel').setAttribute('aria-labelledby', button.id);
    renderScope(0);
    announce(`${activeCodec.toUpperCase()}: ${view.title} ${data.result} ${data.unit}. ${data.rate}. ${data.frames} music frames. ${view.summary}`);
  });
  bindTabs('[data-hardware]', button => {
    const id = button.dataset.hardware;
    const data = hardwareData[id];
    $('#hardwareCategory').textContent = data.category;
    $('#hardwareName').textContent = data.name;
    $('#hardwareDescription').textContent = data.description;
    $('#hardwareKnown').textContent = data.known;
    $('#hardwareMissing').textContent = data.missing;
    $('#hardwarePanel').setAttribute('aria-labelledby', button.id);
    $$('[data-hardware-art]').forEach(node => node.classList.toggle('active', node.dataset.hardwareArt === id));
    announce(`${data.name}. ${data.known} Still needed: ${data.missing}`);
  });
  bindTabs('[data-architecture]', button => {
    const mode = button.dataset.architecture;
    const data = architectures[mode];
    $('#architecturePanel').dataset.mode = mode;
    $('#architecturePanel').setAttribute('aria-labelledby', button.id);
    $('#architectureBadge').textContent = data.badge;
    $('#architectureLead').textContent = data.lead;
    $('#architectureFoot').textContent = data.foot;
    const nodes = data.nodes.map(([label, title, description, state, unknown]) => {
      const node = document.createElement('div');
      node.className = `flow-node${unknown ? ' unknown' : ''}`;
      [['span', label], ['b', title], ['small', description], ['em', state]].forEach(([tag, text]) => {
        const element = document.createElement(tag); element.textContent = text; node.append(element);
      });
      return node;
    });
    $('#systemFlow').replaceChildren(...nodes);
    announce(data.lead);
  });
  bindTabs('[data-failure]', button => {
    const data = failures[button.dataset.failure];
    $('#failureNumber').textContent = data.number;
    $('#failureDepth').textContent = data.depth;
    $('#failureTitle').textContent = data.title;
    $('#failureDescription').textContent = data.description;
    $('#failureRequirement').textContent = data.requirement;
    $('#failurePanel').setAttribute('aria-labelledby', button.id);
    $$('.failure-visual i').forEach((node, index) => node.classList.toggle('fault', index >= data.fault));
    announce(`${data.title} ${data.requirement} Original-board recovery is not established.`);
  });

  // The illustration explores layers, never presents an invented circuit layout.
  $('#explodeButton').addEventListener('click', event => {
    const button = event.currentTarget;
    const state = button.getAttribute('aria-pressed') !== 'true';
    button.setAttribute('aria-pressed', String(state));
    button.firstChild.textContent = state ? 'Reassemble ' : 'Separate layers ';
    $('#heroObject').classList.toggle('exploded', state);
    $('#objectCaption').textContent = state ? 'Concept layers. Not a Sony assembly drawing.' : 'Interface concept. Not a running Sony device.';
    announce(state ? 'Concept layers separated. This is not a Sony assembly drawing.' : 'Concept reassembled.');
  });

  const sources = [
    { id: 'prototype', category: 'virtual', label: 'Virtual-machine evidence', title: 'Rockbox on ARM64 Linux', text: 'Recorded generic guest with Alpine Linux, BusyBox and Rockbox. Actual Sony boot and hardware compatibility were not demonstrated.', links: [['M5 · Linux prototype', 'm5-linux-prototype.md'], ['M6 · Display integration', 'm6-linux-display-integration.md']] },
    { id: 'playback', category: 'virtual', label: 'Recorded fixture results', title: 'Playback and scanout', text: 'WAV/FLAC match reference music samples. Native-rate Opus produces 108,001 frames at 48 kHz with approximately 68.79 dB reference SNR. The format diagrams are illustrative, not captured PCM or file-size measurements. WAV and FLAC from the same PCM source decode to identical samples; their storage representations differ.', links: [['M4 · Playback validation', 'm4-playback-validation.md'], ['M6 · Display and PCM results', 'm6-linux-display-integration.md']] },
    { id: 'codecs', category: 'virtual', label: 'Test scope and limitations', title: 'Regression and reproducibility', text: '38 codec checks and 42 repeated-build output hashes are recorded in the pinned environments. Native ASan had leak detection disabled; ARM64 sanitizer limitations remain unresolved.', links: [['M3 · Codec validation', 'm3-codec-validation.md'], ['M6 · Rebuilds and limitations', 'm6-linux-display-integration.md']] },
    { id: 'hardware', category: 'sample', label: 'Certification sample only', title: 'Photographed component markings', text: 'SODAGREEN M/B revision 1.03, QCS2290, PM4125 and Samsung KLMBG2JETD are reported from FCC photographs. The owner’s board revision and exact selected configuration are not thereby established.', links: [['M7 · FCC photographic evidence', 'm7-fcc-evidence.md'], ['M7 · Hardware convergence', 'm7-hardware-convergence.md']] },
    { id: 'provenance', category: 'sample', label: 'Artifact provenance', title: '43 PDFs. Corrected classifications.', text: '594 pages passed structural traversal. All 31 available catalog SHA-256 values match, including 29 documents with two-byte size discrepancies. Twelve documents lack published hashes. A catalog match is not independent publisher authentication.', links: [['M7 · Inventory and provenance audit', 'm7-fcc-evidence.md']] },
    { id: 'architecture', category: 'unknown', label: 'Proposed target architecture', title: 'A kernel is not an entry point', text: 'Stock-kernel support for non-Android init does not prove accepted selection of an alternate ramdisk or root filesystem. No selected Sony boot/DT/AVB bundle has been obtained.', links: [['M9 · Authentication boundaries', 'm9-authentication-boundaries.md'], ['M9 · Boot-artifact inventory', 'm9-boot-artifact-inventory.md']] },
    { id: 'userspace', category: 'unknown', label: 'Contract tested; hardware unverified', title: 'Initialization needs an owner', text: 'The 13-role minimum-userspace model tests ordering and failure propagation. Explicit module readiness, firmware delivery, device nodes, deferred probes and safety initialization still require the selected system’s configuration.', links: [['M9 · Stock-kernel userspace', 'm9-stock-kernel-userspace.md']] },
    { id: 'storage', category: 'sample', label: 'Platform versus configuration', title: 'eMMC regions are not Android slots', text: 'The storage model distinguishes the user area, hardware boot regions and RPMB from GPT entries and Android A/B slots. Component capabilities do not establish Sony’s actual region use or provisioning.', links: [['M8 · Boot and storage architecture', 'm8-boot-storage-architecture.md']] },
    { id: 'recovery', category: 'unknown', label: 'Requirements, not a restore procedure', title: 'Original-board recovery', text: 'Six failure states remain without a demonstrated applicable restoration path. Factory reset, routine update, service reinstall and board replacement have different survival requirements.', links: [['M9 · Recovery readiness', 'm9-recovery-readiness.md'], ['M8 · Recovery assessment', 'm8-recovery-assessment.md']] },
    { id: 'roadmap', category: 'unknown', label: 'Next work, not completed behavior', title: 'The physical integration gap', text: 'Independent acquisition and a bounded characterization workflow are planned. The normal ADB shell cannot be assumed to read the raw FDT; a live tree is not necessarily the stored DTB/DTBO.', links: [['M9 · Userspace and FDT findings', 'm9-stock-kernel-userspace.md'], ['Project roadmap', 'roadmap.md']] }
  ];
  const drawer = $('#evidenceDrawer');
  const evidenceButton = $('#evidenceToggle');
  let evidenceMode = false;
  let returnFocus = evidenceButton;
  sources.forEach((source, index) => {
    const article = document.createElement('article');
    article.className = 'evidence-record'; article.id = `record-${source.id}`; article.dataset.category = source.category;
    const meta = document.createElement('div'); meta.className = 'record-meta';
    const number = document.createElement('span'); number.textContent = String(index + 1).padStart(2, '0');
    const label = document.createElement('span'); label.textContent = source.label;
    meta.append(number, label);
    const title = document.createElement('h3'); title.textContent = source.title;
    const description = document.createElement('p'); description.textContent = source.text;
    article.append(meta, title, description);
    source.links.forEach(([name, filename]) => {
      const link = document.createElement('a'); link.className = 'record-source';
      link.href = doc(filename); link.textContent = `${name} ↗`; link.target = '_blank'; link.rel = 'noopener noreferrer';
      article.append(link);
    });
    $('#evidenceRecords').append(article);
  });
  function filterSources(category) {
    let visible = 0;
    $$('.evidence-record').forEach(record => {
      record.hidden = category !== 'all' && category !== record.dataset.category;
      if (!record.hidden) visible += 1;
    });
    $$('[data-filter]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.filter === category)));
    $('#evidenceCount').textContent = `${visible} of ${sources.length} source records`;
  }
  function setEvidenceMode(state) {
    evidenceMode = state;
    document.body.classList.toggle('evidence-active', state);
    evidenceButton.setAttribute('aria-pressed', String(state));
    $('#evidenceToggleLabel').textContent = state ? 'Evidence on' : 'Evidence mode';
    $('#evidenceRibbon').hidden = !state;
    if (!state && drawer.open) drawer.close();
    announce(state ? 'Evidence mode on. Source notes are visible throughout the presentation.' : 'Evidence mode off.');
  }
  function openEvidence(sourceId = null, trigger = evidenceButton) {
    returnFocus = trigger;
    setEvidenceMode(true);
    filterSources('all');
    $$('.evidence-record').forEach(record => record.classList.remove('focused'));
    if (!drawer.open) drawer.showModal();
    document.body.classList.add('drawer-open');
    if (sourceId) {
      const record = $(`#record-${sourceId}`);
      if (record) {
        record.classList.add('focused');
        requestAnimationFrame(() => {
          drawer.scrollTop = record.offsetTop - 20;
          const link = $('.record-source', record);
          if (link) link.focus({ preventScroll: true });
        });
      }
    } else {
      drawer.scrollTop = 0;
      $('#closeEvidence').focus({ preventScroll: true });
    }
  }
  filterSources('all');
  evidenceButton.addEventListener('click', () => {
    if (evidenceMode) setEvidenceMode(false); else openEvidence();
  });
  $('#reopenEvidence').addEventListener('click', event => openEvidence(null, event.currentTarget));
  $('#closeEvidence').addEventListener('click', () => drawer.close());
  $('#exitEvidence').addEventListener('click', () => setEvidenceMode(false));
  drawer.addEventListener('close', () => {
    document.body.classList.remove('drawer-open');
    if (returnFocus && returnFocus.isConnected) returnFocus.focus({ preventScroll: true });
  });
  drawer.addEventListener('click', event => {
    if (event.target !== drawer) return;
    const rect = drawer.getBoundingClientRect();
    if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) drawer.close();
  });
  $$('[data-source]').forEach(button => button.addEventListener('click', () => openEvidence(button.dataset.source, button)));
  $$('[data-filter]').forEach(button => button.addEventListener('click', () => filterSources(button.dataset.filter)));

  // Single animation loop, stopped offscreen, on hidden tabs and on reduced motion.
  const motionPreference = window.matchMedia('(prefers-reduced-motion: reduce)');
  let motionPaused = motionPreference.matches;
  let frameId = null;
  let scopeVisible = false;
  const canvas = $('#scopeCanvas');
  const context = canvas.getContext('2d');
  let canvasWidth = 1;
  let canvasHeight = 1;
  function resizeScope() {
    const rect = canvas.getBoundingClientRect();
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvasWidth = Math.max(rect.width, 1); canvasHeight = Math.max(rect.height, 1);
    canvas.width = Math.round(canvasWidth * dpr); canvas.height = Math.round(canvasHeight * dpr);
    if (context) { context.setTransform(dpr, 0, 0, dpr, 0, 0); renderScope(0); }
  }
  // One deterministic integer signal is shared by the PCM and lossless examples.
  // This is not a FLAC encoder: only a first-order predictor/residual identity
  // is illustrated. No compression ratio or test-fixture samples are implied.
  const examplePCM = Object.freeze(Array.from({ length: 96 }, (_, i) => {
    const t = i / 95;
    const envelope = Math.sin(t * Math.PI) ** 2;
    return Math.round(11000 * envelope * (
      0.65 * Math.sin(t * 11 * Math.PI) + 0.3 * Math.sin(t * 5 * Math.PI)
    ));
  }));
  const exampleResiduals = Object.freeze(examplePCM.map((value, i) => value - (i ? examplePCM[i - 1] : 0)));
  let previous = 0;
  const exampleReconstructed = Object.freeze(exampleResiduals.map(residual => (previous += residual)));
  const losslessExampleMatches = examplePCM.every((value, i) => value === exampleReconstructed[i]);

  function scopeLine(x1, y1, x2, y2, color, width = 1) {
    context.strokeStyle = color;
    context.lineWidth = width;
    context.beginPath(); context.moveTo(x1, y1); context.lineTo(x2, y2); context.stroke();
  }
  function scopeLabel(text, x, y, color, align = 'left', size = 9) {
    context.font = `${size}px ui-monospace, SFMono-Regular, Consolas, monospace`;
    context.textAlign = align;
    context.textBaseline = 'middle';
    context.fillStyle = color;
    context.fillText(text, x, y);
  }
  function scopeArrow(x1, y, x2, color) {
    scopeLine(x1, y, x2, y, color);
    scopeLine(x2 - 5, y - 4, x2, y, color);
    scopeLine(x2 - 5, y + 4, x2, y, color);
  }
  function scopeGrid(w, h) {
    for (let x = 0; x <= w; x += 28) scopeLine(x, 0, x, h, '#9abe7512', 0.6);
    for (let y = 0; y <= h; y += 24) scopeLine(0, y, w, y, '#9abe7512', 0.6);
  }
  function sampleTrace(samples, x, y, width, amplitude, color, withStems, scan) {
    if (withStems) {
      samples.forEach((sample, i) => {
        const px = x + (i / (samples.length - 1)) * width;
        const py = y - sample / 11000 * amplitude;
        const near = Math.abs(i / samples.length - scan) < 0.045;
        scopeLine(px, y, px, py, near ? color : `${color}4d`, near ? 1.4 : 0.8);
        context.fillStyle = near ? '#f3ffdc' : color;
        context.beginPath(); context.arc(px, py, near ? 2.4 : 1.35, 0, Math.PI * 2); context.fill();
      });
    }
    context.lineWidth = withStems ? 1.1 : 1.7;
    context.strokeStyle = color;
    context.beginPath();
    samples.forEach((sample, i) => {
      const px = x + i / (samples.length - 1) * width;
      const py = y - sample / 11000 * amplitude;
      if (i) context.lineTo(px, py); else context.moveTo(px, py);
    });
    context.stroke();
  }
  function drawPCM(w, h, scan) {
    const pad = w < 400 ? 14 : 26;
    const color = '#d6f797';
    scopeLabel('DISCRETE SAMPLE VALUES', pad, 14, '#8eaa78', 'left', w < 350 ? 8 : 9);
    const mid = h * 0.49;
    scopeLine(pad, mid, w - pad, mid, '#a8c2864d', 0.8);
    // Every marker uses an integer from the same synthetic PCM array.
    sampleTrace(examplePCM, pad, mid, w - 2 * pad, h * 0.40, color, true, scan);
    const marker = pad + scan * (w - 2 * pad);
    scopeLine(marker, 29, marker, h - 32, '#d6f79745', 0.8);
    for (let i = 0; i < 8; i += 1) {
      const x = pad + i * (w - 2 * pad) / 8;
      const width = (w - 2 * pad) / 8 - 4;
      context.fillStyle = '#d6f79712'; context.fillRect(x, h - 27, width, 9);
      scopeLine(x, h - 27, x, h - 18, '#d6f79766');
    }
    scopeLabel('SAMPLES STORED DIRECTLY', pad, h - 4, '#b4c59f', 'left', 8);
    if (w > 350) scopeLabel('TIME →', w - pad, h - 4, '#8eaa78', 'right', 8);
  }
  function drawLossless(w, h, scan) {
    const pad = w < 400 ? 14 : 26;
    const color = '#b1eed6';
    const blocks = w < 470 ? 4 : 6;
    const gap = w < 400 ? 7 : 10;
    const bw = (w - pad * 2 - gap * (blocks - 1)) / blocks;
    const top = 33, bh = h * 0.31;
    scopeLabel('PREDICTION + EXACT RESIDUAL', pad, 14, '#9ac7b1', 'left', w < 350 ? 8 : 9);
    for (let block = 0; block < blocks; block += 1) {
      const x = pad + block * (bw + gap);
      const active = Math.floor(scan * blocks) === block;
      context.fillStyle = active ? '#b1eed615' : '#b1eed608'; context.fillRect(x, top, bw, bh);
      context.lineWidth = 0.9; context.strokeStyle = active ? '#b1eed6bb' : '#b1eed644';
      context.strokeRect(x + 0.5, top + 0.5, bw - 1, bh - 1);
      scopeLabel(`B${String(block + 1).padStart(2, '0')}`, x + 7, top + 12, active ? '#dfffee' : '#8eb9a2', 'left', 8);
      // Residuals are drawn on a symbolic, independent scale, never as PCM error.
      const from = Math.floor(block * examplePCM.length / blocks);
      const to = Math.floor((block + 1) * examplePCM.length / blocks);
      const residuals = exampleResiduals.slice(from, to);
      const baseline = top + bh * 0.64;
      scopeLine(x + 6, baseline, x + bw - 6, baseline, '#b1eed628', 0.6);
      residuals.forEach((r, i) => {
        const px = x + 7 + i / Math.max(1, residuals.length - 1) * (bw - 14);
        const extent = Math.max(-bh * 0.22, Math.min(bh * 0.22, r / 3600 * bh * 0.22));
        scopeLine(px, baseline, px, baseline - extent, active ? color : '#b1eed699', 1.1);
      });
      const center = x + bw / 2;
      scopeLine(center, top + bh + 4, center, top + bh + 15, '#b1eed644');
      scopeLine(center - 3, top + bh + 12, center, top + bh + 15, '#b1eed644');
      scopeLine(center + 3, top + bh + 12, center, top + bh + 15, '#b1eed644');
    }
    const labelY = top + bh + 31;
    scopeLabel('RECONSTRUCTED PCM', pad, labelY, '#c7e5d0', 'left', 8);
    const outputY = h - 43;
    scopeLine(pad, outputY, w - pad, outputY, '#b1eed633', 0.8);
    sampleTrace(exampleReconstructed, pad, outputY, w - pad * 2, Math.max(22, h * 0.16), color, false, scan);
    const marker = pad + scan * (w - 2 * pad);
    scopeLine(marker, top, marker, h - 16, '#b1eed638', 0.8);
    const index = Math.round(scan * (exampleReconstructed.length - 1));
    const sampleY = outputY - exampleReconstructed[index] / 11000 * Math.max(22, h * 0.16);
    context.fillStyle = '#e8fff3'; context.beginPath(); context.arc(marker, sampleY, 2.4, 0, Math.PI * 2); context.fill();
    scopeLabel(losslessExampleMatches ? 'SAME SOURCE. EVERY SAMPLE PRESERVED.' : 'EXAMPLE RECONSTRUCTION FAILED', pad, h - 4, '#b1eed6', 'left', w < 350 ? 7.6 : 8);
  }
  function drawPackets(w, h, scan) {
    const pad = w < 400 ? 14 : 26;
    const color = '#a5c9ef';
    scopeLabel('COMPRESSED PACKETS → PCM', pad, 14, '#96afc6', 'left', w < 350 ? 8 : 9);
    const leftW = (w - pad * 2) * 0.26;
    const middleX = w * 0.53;
    const middleW = Math.max(62, Math.min(108, w * 0.17));
    const middleY = h * 0.50;
    const packetW = Math.min(leftW - 18, 72);
    for (let n = 0; n < 4; n += 1) {
      const px = pad + n * 5;
      const py = middleY - 47 + n * 17;
      context.fillStyle = '#101c21'; context.fillRect(px, py, packetW, 46);
      context.lineWidth = 0.9; context.strokeStyle = n === Math.floor(scan * 4) ? color : '#a5c9ef66';
      context.strokeRect(px + 0.5, py + 0.5, packetW, 46);
      scopeLabel(`P${n + 1}`, px + 6, py + 9, '#a5c9ef', 'left', 8);
      for (let i = 0; i < 6; i += 1) {
        context.fillStyle = i % 2 ? '#a5c9ef33' : '#a5c9ef66';
        context.fillRect(px + 7 + i * (packetW - 14) / 6, py + 24, Math.max(2, (packetW - 24) / 6), 13);
      }
    }
    const decoderLeft = middleX - middleW / 2;
    scopeArrow(pad + packetW + 20, middleY, decoderLeft - 10, '#a5c9ef88');
    context.fillStyle = '#a5c9ef0c'; context.fillRect(decoderLeft, middleY - 36, middleW, 72);
    context.strokeStyle = '#a5c9efaa'; context.lineWidth = 1; context.strokeRect(decoderLeft, middleY - 36, middleW, 72);
    scopeLabel('OPUS', middleX, middleY - 5, '#dbeaff', 'center', 14);
    scopeLabel('DECODE', middleX, middleY + 13, '#a5c9ef', 'center', 8);
    const outputX = w - pad - (w - pad * 2) * 0.21;
    scopeArrow(middleX + middleW / 2 + 9, middleY, outputX - 8, '#a5c9ef88');
    const glyphs = [14, 29, 48, 36, 16, 34, 43, 24, 12];
    const outputW = w - pad - outputX;
    glyphs.forEach((height, i) => {
      const x = outputX + i / (glyphs.length - 1) * outputW;
      scopeLine(x, middleY - height / 2, x, middleY + height / 2, color, Math.max(1.5, outputW / 35));
    });
    scopeLabel('PCM', outputX + outputW / 2, middleY + 47, '#b4cfe6', 'center', 9);
    scopeLine(pad, h - 38, w - pad, h - 38, '#a5c9ef33');
    scopeLabel('LOSSY CODING', pad, h - 19, '#c1d9f2', 'left', 8);
    if (w > 350) scopeLabel('SEE RECORDED SNR', w - pad, h - 19, '#96afc6', 'right', 8);
    scopeLabel('DIAGRAM DOES NOT DEPICT AUDIO ERROR', pad, h - 4, '#96afc6', 'left', w < 350 ? 7.6 : 8);
  }
  function renderScope(timestamp) {
    if (!context) return;
    const w = canvasWidth, h = canvasHeight;
    context.clearRect(0, 0, w, h);
    scopeGrid(w, h);
    const scan = motionPaused || timestamp === 0 ? 0.55 : (timestamp % 7000) / 7000;
    if (activeCodec === 'wav') drawPCM(w, h, scan);
    else if (activeCodec === 'flac') drawLossless(w, h, scan);
    else drawPackets(w, h, scan);
    // The attribute exposes the representation, not a device or decoding result.
    canvas.dataset.view = activeCodec;
    canvas.dataset.exampleLosslessMatch = String(losslessExampleMatches);
  }
  function syncAnimation() {
    if (frameId !== null) { cancelAnimationFrame(frameId); frameId = null; }
    if (motionPaused || document.hidden || !scopeVisible || !context) { renderScope(0); return; }
    let last = -Infinity;
    const tick = timestamp => {
      if (timestamp - last >= 32) { renderScope(timestamp); last = timestamp; }
      frameId = requestAnimationFrame(tick);
    };
    frameId = requestAnimationFrame(tick);
  }
  function updateMotion(state) {
    motionPaused = state;
    document.body.classList.toggle('motion-paused', state);
    $('#motionToggle').setAttribute('aria-pressed', String(state));
    $('#motionToggle').textContent = state ? 'Resume motion' : 'Pause motion';
    syncAnimation();
  }
  $('#motionToggle').addEventListener('click', () => updateMotion(!motionPaused));
  motionPreference.addEventListener('change', event => updateMotion(event.matches));
  document.addEventListener('visibilitychange', syncAnimation);
  new ResizeObserver(resizeScope).observe(canvas);
  new IntersectionObserver(entries => { scopeVisible = entries[0].isIntersecting; syncAnimation(); }, { threshold: .03 }).observe(canvas);
  updateMotion(motionPaused);

  // Pointer response is deliberately restrained and disabled for touch/reduced motion.
  const hero = $('#heroObject');
  hero.addEventListener('pointermove', event => {
    if (event.pointerType === 'touch' || motionPaused || hero.classList.contains('exploded')) return;
    const rect = hero.getBoundingClientRect();
    const x = (event.clientX - rect.left) / rect.width - .5;
    const y = (event.clientY - rect.top) / rect.height - .5;
    $('#devicePivot').style.transform = `rotateX(${8 - y * 4}deg) rotateY(${-20 + x * 7}deg) rotateZ(11deg)`;
  });
  hero.addEventListener('pointerleave', () => { $('#devicePivot').style.transform = ''; });
  $('#explodeButton').addEventListener('click', () => { $('#devicePivot').style.transform = ''; });

  let progressScheduled = false;
  function updateProgress() {
    const max = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
    $('#readingProgress').style.width = `${Math.max(0, Math.min(100, window.scrollY / max * 100))}%`;
    progressScheduled = false;
  }
  window.addEventListener('scroll', () => { if (!progressScheduled) { progressScheduled = true; requestAnimationFrame(updateProgress); } }, { passive: true });
  window.addEventListener('resize', updateProgress);
  updateProgress();
})();
