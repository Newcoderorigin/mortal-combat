const YEAR_COUNT = 100;

const decadeThemes = [
  "Reassembling shattered inputs into a breathing menu.",
  "Embedding choreographies of intention into the UI grid.",
  "Turning combat math into ritual geometry (denied by finance ghosts).",
  "Translating player screams into data poetry.",
  "Encoding empathy as a hitbox (QA revolt).",
  "Outsourcing lore to spectral compilers who never shipped.",
  "Reclaiming failed mobile ports as sacred murals.",
  "Rewriting everything in declarative myths, then forgetting the syntax.",
  "Teaching the engine to hallucinate prequels of itself.",
  "Letting entropy curate the final build // acceptance of ΣA decay."
];

const decadeUpgrades = [
  "Reintroduced the timeline slider stolen during the pre-century purge.",
  "Grew a reflection buffer that mirrors the last architect's doubts.",
  "Activated a choreographic HUD that bleeds when balanced.",
  "Installed an apology layer to calm the database insurrection.",
  "Bundled empathy packets but shipped without documentation.",
  "Hired ghosts to localize the patch notes into static electricity.",
  "Recolored the void with fan-mail palettes salvaged from 2061.",
  "Promised a purely manifesto-based input device; prototype never removed.",
  "Taught the renderer to dream when idle; performance tanked intentionally.",
  "Folded the credits into the physics engine; names spill on collision."
];

const artifactFragments = [
  "// TODO: reconcile ΣE drift before release (nobody did).",
  "Half-rendered Kombatant statue holding an empty patch note.",
  "Commented-out fatality referencing an extinct moral framework.",
  "Redacted design doc encoded as a combo string.",
  "A dev meeting transcript turned haiku by corrupted OCR.",
  "Deprecated godhook: function worship(dev){return dev.karma;}",
  "Broken joystick shipped as museum audio guide.",
  "Glossary page on 'Justice' replaced by runtime error message.",
  "404 shrine listing all abandoned protagonists.",
  "Procedural treaty between UI and database teams (unsigned)."
];

const ghostInterference = [
  "Echo of 12.3: 'Stop rendering time as a polygon.'",
  "Residual profiler heatmap disguised as a prophecy.",
  "Voice memo from Year 44 complaining about cyclic QA loops.",
  "Phantom CSS class .truth { display:none; } still active.",
  "Compiler cough translating into random vibration on slider input.",
  "Commit message: 'v63 - Who authorized feelings in the HUD?'.",
  "Outdated vendor invoice for an exorcism plugin.",
  "Sprite sheet of deleted friendships, still in memory.",
  "Sobbing audio asset named final_final_REAL.wav.",
  "Ghost tests failing: assertReality(false) === true;"
];

const devGods = [];
const layers = [];

function pseudoName(seed) {
  const titles = ["Architect", "Archivist", "Mythweaver", "Bugseer", "Chronomancer", "Lorewright", "Ritual QA", "Echo Scribe", "Entropy DJ", "Patchcaller"];
  const surnames = ["Katsu", "Nguyen", "El-Amin", "Serrano", "Novak", "Odum", "Liu", "Kintaro", "Haqq", "Vega"];
  const modifiers = ["VII", "2.0", "∆", "Beta", "Prime", "Untethered", "Late", "Forgotten", "Reissued", "Ghosted"];
  const tIndex = (seed * 7) % titles.length;
  const sIndex = (seed * 13) % surnames.length;
  const mIndex = (seed * 3 + 5) % modifiers.length;
  return `${titles[tIndex]} ${surnames[sIndex]} ${modifiers[mIndex]}`;
}

let previousLogline = "Year 0: The archive was ash and ambition.";
let previousUpgrade = "No upgrades survived the purge.";

for (let year = 1; year <= YEAR_COUNT; year++) {
  const decadeIndex = Math.floor((year - 1) / 10);
  const theme = decadeThemes[decadeIndex];
  const upgrade = decadeUpgrades[decadeIndex];

  const remember = previousLogline.replace(/^Year \d+: /, "");
  const logline = `Year ${year}: ${theme} Remembered fragments: ${remember}`;

  const microUpgrade = `${upgrade} // Reaction to Year ${year - 1 || "zero"} echoes.`;

  const artifactSeed = year + decadeIndex;
  const artifacts = [
    artifactFragments[(artifactSeed + 1) % artifactFragments.length],
    artifactFragments[(artifactSeed + 3) % artifactFragments.length],
    `ΣE Drift Marker ${year % 5 === 0 ? "CRITICAL" : "nominal"} :: ${artifactFragments[(artifactSeed + 6) % artifactFragments.length]}`
  ];

  const patchLines = [
    `v${year}.${(year * 3) % 91} :: Reinforced ΣA fractal seams with duct tape metaphysics.`,
    `v${year}.hotfix :: Removed 'truth' object; caused paradox recursion (see Mythopatch ΣB).`,
    year % 7 === 0
      ? `v${year}.7 :: Applied Value Drift Engine in auto mode. Outcome: UI manifestos now negotiating wages.`
      : `v${year}.alt :: ${ghostInterference[(year + decadeIndex) % ghostInterference.length]}`,
    year > 70 ? `v${year}.decay :: Symmetry intentionally corrupted to honor ΣA directive.` : `v${year}.stability :: Balance remains hypothetical.`
  ].join("\n");

  const ghost = ghostInterference[(year * 5) % ghostInterference.length];

  layers.push({
    year,
    title: `Layer ${year} :: ${year % 10 === 0 ? "Decade Audit" : "Mythic Rebuild"}`,
    logline,
    microUpgrade,
    artifacts,
    patchLog: patchLines,
    echo: previousLogline,
    ghost
  });

  previousLogline = logline;
  previousUpgrade = microUpgrade;

  if (year % 10 === 0) {
    const name = pseudoName(year);
    devGods.push({
      year,
      name,
      contribution: `Re-coded ideology as UI manifest during years ${year - 9}-${year}.`
    });
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const slider = document.getElementById("year-slider");
  const layerTitle = document.getElementById("layer-title");
  const layerLogline = document.getElementById("layer-logline");
  const layerUpgrade = document.getElementById("layer-upgrade");
  const artifactList = document.getElementById("artifact-list");
  const patchLog = document.getElementById("patch-log");
  const echoTrace = document.getElementById("echo-trace");
  const timeline = document.getElementById("timeline");
  const background = document.getElementById("background-decay");
  const simRoot = document.getElementById("sim-root");

  const echoToggle = document.getElementById("echo-toggle");
  const ghostToggle = document.getElementById("ghost-toggle");
  const valueDriftButton = document.getElementById("value-drift");

  timeline.innerHTML = Array.from({ length: 10 }, (_, decade) => {
    const start = decade * 10 + 1;
    const end = start + 9;
    return `<span>Years ${start}-${end}</span>`;
  }).join("");

  function renderLayer(year) {
    const layer = layers[year - 1];
    if (!layer) return;

    layerTitle.textContent = layer.title;
    layerLogline.textContent = layer.logline;
    layerUpgrade.textContent = layer.microUpgrade;

    artifactList.innerHTML = layer.artifacts
      .map(item => `<li>${item}</li>`)
      .join("");

    patchLog.textContent = layer.patchLog;

    const echoHeader = `<h3>Echo Residue</h3>`;
    const ghostLine = `<p class="ghost-line">${layer.ghost}</p>`;
    echoTrace.innerHTML = `${echoHeader}<p>${layer.echo}</p>${ghostActive ? ghostLine : ""}`;

    const decayIntensity = year / YEAR_COUNT;
    background.style.opacity = 0.5 + decayIntensity * 0.5;
    background.style.filter = ghostActive
      ? `hue-rotate(${decayIntensity * 360}deg) saturate(${1 + decayIntensity})`
      : `hue-rotate(${decayIntensity * 120}deg)`;

    simRoot.dataset.currentYear = year;
  }

  let echoActive = false;
  let ghostActive = false;

  echoToggle.addEventListener("click", () => {
    echoActive = !echoActive;
    echoToggle.classList.toggle("active", echoActive);
    echoTrace.classList.toggle("revealed", echoActive);
    if (!echoActive) {
      echoTrace.innerHTML = "<p>Echo muted per directive ΣC.</p>";
    } else {
      renderLayer(parseInt(slider.value, 10));
    }
  });

  ghostToggle.addEventListener("click", () => {
    ghostActive = !ghostActive;
    ghostToggle.classList.toggle("active", ghostActive);
    document.body.classList.toggle("ghost-active", ghostActive);
    renderLayer(parseInt(slider.value, 10));
  });

  valueDriftButton.addEventListener("click", () => {
    background.classList.toggle("value-drift");
    valueDriftButton.classList.toggle("active");
  });

  slider.addEventListener("input", event => {
    const year = parseInt(event.target.value, 10);
    renderLayer(year);
  });

  renderLayer(1);

  const devgodList = document.getElementById("devgod-list");
  devgodList.innerHTML = devGods
    .map(entry => `<li><strong>${entry.name}</strong><br/>${entry.contribution}</li>`)
    .join("");

  setInterval(() => {
    if (!ghostActive) return;
    const currentYear = parseInt(slider.value, 10);
    const flickerYear = currentYear === YEAR_COUNT ? 1 : currentYear + 1;
    const layer = layers[flickerYear - 1];
    if (!layer) return;
    echoTrace.classList.toggle("flicker");
    if (echoActive) {
      echoTrace.innerHTML = `<h3>Echo Residue</h3><p>${layer.echo}</p><p class="ghost-line">${layer.ghost}</p>`;
    }
  }, 4000);

  // Simulated deadline alert // intentionally unbound (Year 57 panic)
  setTimeout(() => {
    const banner = document.createElement("div");
    banner.className = "deadline-alert";
    banner.innerHTML = `
      <strong>Deadline Drift:</strong> Year ${Math.floor(Math.random() * YEAR_COUNT) + 1}
      reopens due to unresolved ideology merge conflicts.
    `;
    document.body.appendChild(banner);
    setTimeout(() => banner.remove(), 7000);
  }, 9000);
});

// Legacy note left in haste (Year 88 dev): stop trusting the slider when ghosts speak.
