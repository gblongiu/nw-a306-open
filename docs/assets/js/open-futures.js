/* SPDX-License-Identifier: GPL-2.0-or-later */
(() => {
  'use strict';
  // Concept-mode controls are separate from the evidence and implementation claims.
  const studio = document.getElementById('futureStudio');
  const scene = document.getElementById('futures');
  const tabs = Array.from(document.querySelectorAll('[data-future-select]'));
  const quick = Array.from(document.querySelectorAll('[data-future-action]'));
  const panels = Array.from(document.querySelectorAll('[data-future-panel]'));
  const detail = {
    rockbox: {
      kind: 'ROCKBOX / DEDICATED PLAYER', title: 'Pure listening.',
      description: 'A local collection, tactile playback, familiar formats and an interface built around albums instead of accounts.',
      tags: ['LOCAL AUDIO', 'PHYSICAL CONTROLS', 'FOCUSED UI']
    },
    linux: {
      kind: 'LINUX / GENERAL-PURPOSE HANDHELD', title: 'Everything else.',
      description: 'A pocket-scale Linux workspace for compatible ARM64 programs, a local terminal and projects that go beyond audio.',
      tags: ['ARM64 LINUX', 'TERMINAL', 'OWNER CONTROL']
    }
  };
  if (!studio || tabs.length !== 2 || panels.length !== 2) return;
  let mode = 'rockbox';
  const set = (next, announce = false) => {
    if (!detail[next]) return;
    mode = next;
    document.body.dataset.future = mode;
    scene.dataset.future = mode;
    tabs.forEach(tab => {
      const selected = tab.dataset.futureSelect === mode;
      tab.setAttribute('aria-selected', String(selected));
      tab.tabIndex = selected ? 0 : -1;
    });
    quick.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.futureAction === mode)));
    panels.forEach(panel => { panel.hidden = panel.dataset.futurePanel !== mode; });
    document.getElementById('futureDetailKind').textContent = detail[mode].kind;
    document.getElementById('futureDetailTitle').textContent = detail[mode].title;
    document.getElementById('futureDetailDescription').textContent = detail[mode].description;
    const tags = document.getElementById('futureDetailTags');
    tags.replaceChildren(...detail[mode].tags.map(label => {
      const span = document.createElement('span');
      span.textContent = label;
      return span;
    }));
    if (announce) {
      const status = document.getElementById('liveStatus');
      if (status) status.textContent = `${mode === 'rockbox' ? 'Rockbox' : 'Linux'} concept preview selected. Not a verified Sony hardware interface.`;
    }
  };
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => set(tab.dataset.futureSelect, true));
    tab.addEventListener('keydown', event => {
      let next = null;
      if (event.key === 'ArrowRight' || event.key === 'ArrowDown') next = (index + 1) % tabs.length;
      if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') next = (index + tabs.length - 1) % tabs.length;
      if (event.key === 'Home') next = 0;
      if (event.key === 'End') next = tabs.length - 1;
      if (next === null) return;
      event.preventDefault();
      set(tabs[next].dataset.futureSelect, true);
      tabs[next].focus();
    });
  });
  quick.forEach(button => button.addEventListener('click', () => set(button.dataset.futureAction, true)));
  set('rockbox');
})();
