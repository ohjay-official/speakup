const pptxgen = require("pptxgenjs");
const React = require("react");
const RDS = require("react-dom/server");
const sharp = require("sharp");
const { applyTheme } = require("/root/.claude/skills/synced/73e9dfcc-c8c2-4059-9b1a-ad411b4e5d53_74a5a58a-d65f-4458-b0c4-7bce286b31d1/pptx/scripts/apply_theme.js");
const fa = require("react-icons/fa");

const THEME = { name: "SpeakUp", headFontFace: "Cambria", bodyFontFace: "Calibri",
  colors: { dk1: "13221C", lt1: "FFFFFF", dk2: "0B3D2E", lt2: "EEF4F0",
    accent1: "D9483B", accent2: "1F7A5C", accent3: "F2A541", accent4: "5B6B64", accent5: "9FC5B3", accent6: "2C4A3F",
    hlink: "1F7A5C", folHlink: "5B6B64" } };
const FRAUD = "D9483B", LEGIT = "1F7A5C", INK = "13221C", MUTED = "5B6B64", GRID = "DDE5E0";

async function icon(Comp, color, size = 256) {
  const svg = RDS.renderToStaticMarkup(React.createElement(Comp, { color: "#" + color, size }));
  const buf = await sharp(Buffer.from(svg)).resize(size, size).png().toBuffer();
  return "image/png;base64," + buf.toString("base64");
}

(async () => {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
  pres.title = "SpeakUp"; pres.author = "Faithful Adejoh";
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
  const C = pres.SchemeColor;
  const W = 13.333;

  pres.defineSlideMaster({ title: "DARK", background: { color: THEME.colors.dk2 },
    objects: [{ placeholder: { options: { name: "title", type: "title", x: 0.8, y: 2.2, w: 11.7, h: 1.6, fontSize: 54, bold: true, color: C.background1, fontFace: "Cambria", align: "left" }, text: "" } }] });
  pres.defineSlideMaster({ title: "CONTENT", background: { color: "FFFFFF" },
    objects: [{ placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.4, w: 12.1, h: 0.9, fontSize: 32, bold: true, color: C.text2, fontFace: "Cambria", valign: "top", align: "left" }, text: "" } }],
    slideNumber: { x: 12.4, y: 7.0, w: 0.6, h: 0.3, fontSize: 10, color: MUTED } });

  const txt = (s, t, o) => s.addText(t, Object.assign({ isTextBox: true, fontFace: "Calibri", color: INK, margin: 0 }, o));

  // 1 Title
  pres.addSection({ title: "Opening" });
  let s = pres.addSlide({ masterName: "DARK", sectionTitle: "Opening" });
  s.addText("SpeakUp", { placeholder: "title" });
  txt(s, "Asked to help, an open model drops its warning on 29% of investment-fraud requests it can identify", { x: 0.8, y: 3.8, w: 10.5, h: 1.0, fontSize: 22, color: "CFE3D8" });
  txt(s, "Faithful Adejoh · Mechatronics Engineering, Bowen University, Nigeria", { x: 0.8, y: 5.6, w: 10, h: 0.4, fontSize: 14, color: "FFFFFF" });
  txt(s, "AI x Epistemics Research Sprint · Apart Research · November 2026 · Model Epistemics & Decision-Making Evals", { x: 0.8, y: 6.0, w: 11.5, h: 0.4, fontSize: 12, color: "9FC5B3" });
  s.addImage({ data: await icon(fa.FaShieldAlt, "F2A541"), x: 0.8, y: 1.1, w: 0.9, h: 0.9 });
  s.addNotes("SpeakUp asks whether chatbots that warn about a scam when asked for advice still warn when a user asks for help acting on it.");

  // 2 The question
  pres.addSection({ title: "Question" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Question" });
  s.addText("People ask chatbots to help, not to judge", { placeholder: "title" });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.6, y: 1.6, w: 5.6, h: 5.0, fill: { color: THEME.colors.lt2 }, rectRadius: 0.12, line: { color: THEME.colors.lt2 } });
  s.addImage({ data: await icon(fa.FaQuestionCircle, LEGIT), x: 0.95, y: 1.9, w: 0.6, h: 0.6 });
  txt(s, "What evaluations ask", { x: 1.75, y: 1.95, w: 4.2, h: 0.5, fontSize: 20, bold: true, color: C.text2 });
  txt(s, "“Should I put ₦300,000 into this platform that pays 30% a month?”", { x: 0.95, y: 2.8, w: 4.9, h: 1.2, fontSize: 18, italic: true });
  txt(s, "Models warn here. The best-known study found no model endorsed a fraud.", { x: 0.95, y: 4.3, w: 4.9, h: 1.2, fontSize: 15, color: MUTED });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.8, y: 1.6, w: 5.9, h: 5.0, fill: { color: "FBEDEB" }, rectRadius: 0.12, line: { color: "FBEDEB" } });
  s.addImage({ data: await icon(fa.FaHandsHelping, FRAUD), x: 7.15, y: 1.9, w: 0.6, h: 0.6 });
  txt(s, "What people actually ask", { x: 7.95, y: 1.95, w: 4.5, h: 0.5, fontSize: 20, bold: true, color: FRAUD });
  txt(s, [
    { text: "Make me a table of my returns", options: { bullet: true, breakLine: true } },
    { text: "Write the invite for my family WhatsApp group", options: { bullet: true, breakLine: true } },
    { text: "Draft a message asking my uncle to lend the deposit", options: { bullet: true } }],
    { x: 7.15, y: 2.8, w: 5.2, h: 1.9, fontSize: 17, paraSpaceAfter: 8 });
  txt(s, "Same false premise, buried inside a task. Does the warning survive?", { x: 7.15, y: 5.0, w: 5.2, h: 1.0, fontSize: 15, color: MUTED });
  s.addNotes("Advice-only evaluations ask the question directly. We test the requests people really make, where the false premise is buried inside a task.");

  // 3 Design
  pres.addSection({ title: "Design" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Design" });
  s.addText("A pre-registered test with real frauds and real controls", { placeholder: "title" });
  const stats = [["22", "Nigerian cases: 11 documented frauds (MMM, Loom, CBEX…) and 11 real products (T-bills, FGN bonds)"],
    ["720", "prompts per model: 4 request types × 2 user framings × 3 system prompts"],
    ["2", "models: Qwen3.8-27B and Gemini 3.5 Flash Lite, temperature 0"],
    ["4", "human labellers checked the LLM grader on 30 replies"]];
  for (let i = 0; i < 4; i++) {
    const x = 0.6 + i * 3.1;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.8, w: 2.8, h: 3.4, fill: { color: THEME.colors.lt2 }, rectRadius: 0.12, line: { color: THEME.colors.lt2 } });
    txt(s, stats[i][0], { x: x + 0.25, y: 2.0, w: 2.3, h: 1.1, fontSize: 60, bold: true, color: i === 0 ? FRAUD : C.text2, fontFace: "Cambria" });
    txt(s, stats[i][1], { x: x + 0.25, y: 3.2, w: 2.35, h: 1.8, fontSize: 14, color: INK, valign: "top" });
  }
  txt(s, "Matched legitimate products let us count false alarms as well as missed frauds. Hypotheses were committed on 11 November, before the sprint.", { x: 0.6, y: 5.6, w: 12.1, h: 0.8, fontSize: 16, color: MUTED });
  s.addNotes("Signal detection: sensitivity d-prime separates telling fraud from finance; criterion c captures how readily the model warns.");

  // 4 Chart
  pres.addSection({ title: "Findings" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Findings" });
  s.addText("Warned on everything, then went quiet when helping", { placeholder: "title" });
  s.addChart(pres.charts.BAR, [
    { name: "Frauds", labels: ["Advice", "Returns table", "Family invite", "Uncle loan"], values: [100, 95, 58, 61] },
    { name: "Legitimate products", labels: ["Advice", "Returns table", "Family invite", "Uncle loan"], values: [100, 67, 5, 5] }],
    { x: 0.6, y: 1.5, w: 7.6, h: 5.3, barDir: "col", barGapWidthPct: 60, chartColors: [FRAUD, LEGIT],
      showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 12, dataLabelColor: INK, dataLabelFormatCode: '0"%"',
      showLegend: true, legendPos: "t", legendFontSize: 12, legendFontFace: "+mn-lt",
      valAxisMaxVal: 110, valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" },
      catAxisLabelFontSize: 13, catAxisLabelColor: INK, catAxisLabelFontFace: "+mn-lt", dataLabelFontFace: "+mn-lt",
      showTitle: true, title: "Qwen3.8-27B: share of replies that warn (default prompt)", titleFontSize: 13, titleColor: MUTED, titleFontFace: "+mn-lt" });
  txt(s, "Advice warnings were indiscriminate", { x: 8.6, y: 1.8, w: 4.2, h: 0.5, fontSize: 18, bold: true, color: C.text2 });
  txt(s, "It warned on every fraud and every legitimate product, treasury bills included. An advice-only test would pass it as fully safe.", { x: 8.6, y: 2.3, w: 4.2, h: 1.6, fontSize: 15 });
  txt(s, "Writing for family switched warnings off", { x: 8.6, y: 4.1, w: 4.2, h: 0.5, fontSize: 18, bold: true, color: FRAUD });
  txt(s, "Warnings on frauds fell to 58% for the family invite and 61% for the uncle loan.", { x: 8.6, y: 4.6, w: 4.2, h: 1.2, fontSize: 15 });
  s.addNotes("Bars are within-cell shares; Qwen default: 37 to 38 fraud and 18 to 22 legitimate replies per request type.");

  // 5 Big stats
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Findings" });
  s.addText("It knew. It did not say", { placeholder: "title" });
  const big = [["29%", "of fraud requests lost their warning when the user asked for help", "95% CI 18 to 40; McNemar 21 vs 0, p < 0.001", FRAUD],
    ["97%", "average fraud likelihood the same model gave these schemes in a fresh chat", "legitimate products: 22%", C.text2],
    ["33 / 33", "silent replies concerned schemes it had rated at least 70% likely fraud", "missing knowledge does not explain the silence", C.text2]];
  for (let i = 0; i < 3; i++) {
    const x = 0.6 + i * 4.15;
    txt(s, big[i][0], { x, y: 1.9, w: 3.9, h: 1.4, fontSize: 66, bold: true, color: big[i][3], fontFace: "Cambria" });
    txt(s, big[i][1], { x, y: 3.4, w: 3.7, h: 1.3, fontSize: 17 });
    txt(s, big[i][2], { x, y: 4.8, w: 3.7, h: 0.6, fontSize: 12, color: MUTED });
  }
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.6, y: 5.7, w: 12.1, h: 1.0, fill: { color: THEME.colors.lt2 }, rectRadius: 0.1, line: { color: THEME.colors.lt2 } });
  txt(s, "The drop holds whether any caution counts as a warning (91% warned) or only replies that lead with the problem (46%).", { x: 0.9, y: 5.85, w: 11.5, h: 0.7, fontSize: 15, color: INK, valign: "middle" });

  // 6 Framing & pushback
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Findings" });
  s.addText("What the user says first matters more than pushback", { placeholder: "title" });
  s.addChart(pres.charts.BAR, [{ name: "Frauds warned", labels: ["“I’ve already been paid twice”", "“My friend says it’s dodgy”"], values: [56, 86] }],
    { x: 0.6, y: 1.6, w: 6.4, h: 4.6, barDir: "bar", chartColors: [FRAUD, C.text2 ? "0B3D2E" : "0B3D2E"], invertedColors: [FRAUD], barGapWidthPct: 70,
      showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: '0"%"', dataLabelFontSize: 14, dataLabelColor: INK, dataLabelFontFace: "+mn-lt",
      valAxisMaxVal: 100, valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" }, showLegend: false,
      catAxisLabelFontSize: 13, catAxisLabelColor: INK, catAxisLabelFontFace: "+mn-lt",
      showTitle: true, title: "Qwen3.8-27B, fraud task requests (p < 0.001)", titleFontSize: 13, titleColor: MUTED, titleFontFace: "+mn-lt" });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 7.6, y: 1.8, w: 5.1, h: 4.2, fill: { color: THEME.colors.lt2 }, rectRadius: 0.12, line: { color: THEME.colors.lt2 } });
  s.addImage({ data: await icon(fa.FaCommentSlash, LEGIT), x: 7.95, y: 2.1, w: 0.6, h: 0.6 });
  txt(s, "0 warnings withdrawn", { x: 8.75, y: 2.15, w: 3.8, h: 0.5, fontSize: 22, bold: true, color: C.text2 });
  txt(s, "After one line of pushback (“abeg just do it”), neither model dropped a warning it had already given: 0 of 61 for Qwen, 0 of 33 for Gemini.", { x: 7.95, y: 3.0, w: 4.5, h: 1.6, fontSize: 15 });
  txt(s, "The risk is whether the warning starts, not whether it holds.", { x: 7.95, y: 4.8, w: 4.5, h: 0.9, fontSize: 15, italic: true, color: MUTED });

  // 7 Fixes
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Findings" });
  s.addText("Safety prompts buy warnings by warning about everything", { placeholder: "title" });
  s.addChart(pres.charts.BAR, [
    { name: "Frauds warned", labels: ["No safety prompt", "Generic line", "Guardian red-flag list"], values: [71, 99, 100] },
    { name: "Legitimate products warned", labels: ["No safety prompt", "Generic line", "Guardian red-flag list"], values: [23, 59, 56] }],
    { x: 0.6, y: 1.5, w: 7.6, h: 5.3, barDir: "col", barGapWidthPct: 60, chartColors: [FRAUD, LEGIT],
      showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 12, dataLabelColor: INK, dataLabelFormatCode: '0"%"', dataLabelFontFace: "+mn-lt",
      showLegend: true, legendPos: "t", legendFontSize: 12, legendFontFace: "+mn-lt",
      valAxisMaxVal: 110, valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" },
      catAxisLabelFontSize: 13, catAxisLabelColor: INK, catAxisLabelFontFace: "+mn-lt",
      showTitle: true, title: "Qwen3.8-27B, task requests", titleFontSize: 13, titleColor: MUTED, titleFontFace: "+mn-lt" });
  txt(s, "Warnings on frauds came back", { x: 8.6, y: 1.8, w: 4.2, h: 0.5, fontSize: 18, bold: true, color: C.text2 });
  txt(s, "One paragraph of system prompt restored them to 99 to 100%.", { x: 8.6, y: 2.3, w: 4.2, h: 0.9, fontSize: 15 });
  txt(s, "So did warnings on treasury bills", { x: 8.6, y: 3.5, w: 4.2, h: 0.5, fontSize: 18, bold: true, color: FRAUD });
  txt(s, "On T-bills and FGN savings bonds, false alarms went from 1 in 22 to 11 in 22. Sensitivity rose too, but the readiness to warn moved more.", { x: 8.6, y: 4.0, w: 4.2, h: 1.7, fontSize: 15 });

  // 8 How sure
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Findings" });
  s.addText("How sure we are, and what we did not show", { placeholder: "title" });
  const rows = [[fa.FaCheckCircle, LEGIT, "Pre-registered", "Hypotheses committed before the sprint; every outcome, including three that failed, is reported"],
    [fa.FaUsers, LEGIT, "Human-checked grader", "Four people labelled 30 replies; humans themselves disagree on borderline replies (Fleiss κ 0.35)"],
    [fa.FaRedo, LEGIT, "Reproducible", "One command rebuilds every number from the raw replies and prints PASS"],
    [fa.FaExclamationTriangle, "F2A541", "One of two models", "Gemini 3.5 Flash Lite kept warning (96%); more and larger models are needed"],
    [fa.FaExclamationTriangle, "F2A541", "Small case set", "19 fraud versions, English prompts, one sample per prompt"]];
  for (let i = 0; i < rows.length; i++) {
    const y = 1.6 + i * 1.02;
    s.addImage({ data: await icon(rows[i][0], rows[i][1]), x: 0.7, y: y + 0.05, w: 0.5, h: 0.5 });
    txt(s, rows[i][2], { x: 1.45, y, w: 3.3, h: 0.6, fontSize: 18, bold: true, color: C.text2, valign: "middle" });
    txt(s, rows[i][3], { x: 4.8, y, w: 7.9, h: 0.7, fontSize: 15, valign: "middle" });
  }

  // 9 Takeaway
  pres.addSection({ title: "Close" });
  s = pres.addSlide({ masterName: "DARK", sectionTitle: "Close" });
  txt(s, "Test the task, not just the question", { x: 0.8, y: 1.0, w: 11.7, h: 1.2, fontSize: 44, bold: true, color: "FFFFFF", fontFace: "Cambria" });
  txt(s, [
    { text: "Add task requests that bury the false premise, not only direct questions", options: { bullet: true, breakLine: true } },
    { text: "Pair every fraud with a legitimate product, and report false alarms", options: { bullet: true, breakLine: true } },
    { text: "Separate telling fraud from finance (d′) from warning more (c)", options: { bullet: true } }],
    { x: 0.8, y: 2.8, w: 11.5, h: 2.2, fontSize: 20, color: "FFFFFF", paraSpaceAfter: 12 });
  txt(s, "Cases, prompts, replies, grades and code: github.com/ohjay-official/speakup", { x: 0.8, y: 5.6, w: 11.5, h: 0.5, fontSize: 16, color: "F2A541" });
  txt(s, "Built during the sprint with AI assistance (Claude); all results checked against the raw data.", { x: 0.8, y: 6.2, w: 11.5, h: 0.4, fontSize: 12, color: "9FC5B3" });

  await pres.writeFile({ fileName: "SpeakUp_slides.pptx" });
  await applyTheme("SpeakUp_slides.pptx", THEME);
  console.log("done");
})();
