/* VOLTEX web app – UI, login, routing, offline/PWA glue.
   Calculations run in engine.worker.js (Python engine via Pyodide). */
(function () {
  "use strict";

  /* ---------- helpers ---------- */
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const LS = { lang: "voltex.lang", theme: "voltex.theme", session: "voltex.session", history: "voltex.history" };
  const SESSION_MS = 30 * 24 * 3600 * 1000;
  const FA_DIGITS = "۰۱۲۳۴۵۶۷۸۹";
  const AR_DIGITS = "٠١٢٣٤٥٦٧٨٩";

  const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const toFaDigits = (s) => String(s).replace(/[0-9]/g, (d) => FA_DIGITS[+d]);
  const normalizeNum = (s) => String(s == null ? "" : s)
    .replace(/[۰-۹]/g, (d) => String(FA_DIGITS.indexOf(d)))
    .replace(/[٠-٩]/g, (d) => String(AR_DIGITS.indexOf(d)))
    .replace(/٫/g, ".")
    .trim();

  /* ---------- i18n ---------- */
  const I18N = {
    en: {
      tagline: "Offline electrical engineering suite",
      engine_loading: "Loading engine…",
      engine_ready: "Engine ready",
      engine_error: "Engine error",
      download_app: "Download app",
      install_title: "Install VOLTEX",
      install_intro: "Install VOLTEX as an app. After installing, it opens from your home screen and works offline.",
      install_ios: "On iPhone or iPad (Safari): tap the Share button, then “Add to Home Screen”.",
      install_android: "On Android (Chrome): open the ⋮ menu, then “Install app” or “Add to Home screen”.",
      install_desktop: "On Chrome or Edge: click the install icon at the right end of the address bar.",
      installed_ok: "VOLTEX is installed. It now works offline.",
      close: "Close",
      login_title: "Sign in",
      login_sub: "Access is by existing accounts only.",
      username: "Username",
      password: "Password",
      show: "Show",
      hide: "Hide",
      sign_in: "Sign in",
      signing_in: "Checking…",
      no_signup: "Accounts are managed by the administrator (login.json). There is no sign-up.",
      err_required: "Enter your username and password.",
      err_invalid: "Incorrect username or password.",
      err_locked: "Too many attempts. Wait {s} seconds.",
      err_login_file: "Could not load login.json.",
      err_crypto: "Hashed passwords need a secure connection (HTTPS).",
      nav_dashboard: "Dashboard",
      nav_navigator: "Navigator",
      nav_library: "Model library",
      nav_formulas: "Formulas",
      nav_history: "History",
      nav_settings: "Settings",
      logout: "Sign out",
      signed_in_as: "Signed in as {name}",
      footer_powered: "Powered by TahaGhasemi",
      dash_title: "Welcome, {name}",
      dash_sub: "Offline engineering calculators. Every calculation runs on this device.",
      hero_cta_nav: "Start navigator",
      hero_cta_lib: "Browse models",
      stat_models: "Calculation models",
      stat_series: "Model series",
      stat_offline: "Offline calculation",
      stat_history: "Saved results",
      quick_start: "Start by voltage level",
      recent: "Recent results",
      no_recent: "No saved results yet. Run a calculation and press “Save”.",
      view_all: "View all",
      step_group: "1 · Voltage level",
      step_system: "2 · System type",
      step_topic: "3 · Topic",
      step_model: "4 · Calculation",
      ac: "AC",
      dc: "DC",
      ac_only: "AC only at this voltage level",
      models_count: "{n} models",
      back: "Back",
      home: "Home",
      navigator_title: "Navigator",
      navigator_sub: "Choose a voltage level, system and topic to find the right calculator.",
      search: "Search by name, formula or ID…",
      all: "All",
      library_title: "Model library",
      library_sub: "{n} calculators across three series, all offline.",
      no_results: "No models match your search.",
      calculate: "Calculate",
      reset: "Reset",
      which_missing: "Which values do you not have?",
      hide_alt: "Hide alternatives",
      save_result: "Save result",
      copy_results: "Copy results",
      hint_solve: "Leave exactly one field blank and it will be solved for you.",
      optional_inputs: "Optional alternative inputs",
      alt_title: "Alternative formulas",
      alt_hint: "Each relation is evaluated with the values you have entered. Missing values are listed.",
      alt_ready: "Ready",
      alt_needs: "Needs",
      alt_err: "Error",
      results: "Results",
      solved_for: "Solved for {field}",
      guidance_title: "Engineering guidance",
      saved: "Saved to history",
      copied: "Copied to clipboard",
      copy_failed: "Could not copy",
      filled_defaults: "Default values restored",
      formulas_title: "Formulas & relations",
      formulas_sub: "Primary formula of every model, plus alternative relations.",
      history_title: "History",
      history_sub: "Results you saved on this device.",
      history_empty: "No saved results yet.",
      export_csv: "Export CSV",
      export_json: "Export JSON",
      clear_history: "Clear history",
      confirm_clear: "Delete all saved results on this device?",
      open: "Open",
      delete: "Delete",
      settings_title: "Settings",
      settings_sub: "Language, appearance, installation and account.",
      lang_label: "Language",
      theme_label: "Appearance",
      theme_dark: "Dark",
      theme_light: "Light",
      install_label: "Install as app",
      install_status_yes: "Installed or ready to install. Works offline.",
      install_btn: "Download app",
      engine_label: "Calculation engine",
      engine_desc: "Python 3 engine (Pyodide) running locally in a background worker.",
      about: "About",
      version: "Version",
      models_total: "Models",
      offline_mode: "Offline",
      account: "Account",
      topics_all: "All topics",
      loading_catalog: "Loading models…",
      invalid_num: "Enter valid numbers only (e.g. 12.5).",
      unit: "Unit",
      update_ready: "A new version is ready.",
      update_btn: "Update",
      guidance_note: "This model gives guidance rather than a number, because a safe generic formula would be misleading.",
      topics: {
        transformers: "Transformers", motors: "Motors", cables: "Cables & conductors", circuits: "Circuits & electronics",
        power: "Power & power systems", protection: "Protection & short circuit", high_voltage: "Insulation & high voltage",
        energy: "Battery & energy", general: "Other calculations", extra: "Web extras (TG.WX)"
      },
      series_names: { "TG.VL": "TG.VL · 100 profiles", "TG.VX": "TG.VX · extended", "TG.WX": "TG.WX · web extras" },
    },
    fa: {
      tagline: "مجموعه محاسبات مهندسی برق، کاملاً آفلاین",
      engine_loading: "در حال بارگذاری موتور…",
      engine_ready: "موتور آماده است",
      engine_error: "خطای موتور",
      download_app: "دانلود برنامه",
      install_title: "نصب VOLTEX",
      install_intro: "VOLTEX را مانند یک برنامه نصب کنید. پس از نصب از صفحه اصلی باز می‌شود و آفلاین کار می‌کند.",
      install_ios: "در iPhone یا iPad (Safari): دکمه اشتراک‌گذاری را بزنید و «Add to Home Screen» (افزودن به صفحه اصلی) را انتخاب کنید.",
      install_android: "در Android (Chrome): منوی ⋮ را باز کنید و «نصب برنامه» یا «افزودن به صفحه اصلی» را بزنید.",
      install_desktop: "در Chrome یا Edge: روی آیکون نصب در انتهای نوار آدرس کلیک کنید.",
      installed_ok: "VOLTEX نصب شد و اکنون آفلاین کار می‌کند.",
      close: "بستن",
      login_title: "ورود",
      login_sub: "ورود فقط با حساب‌های موجود امکان‌پذیر است.",
      username: "نام کاربری",
      password: "رمز عبور",
      show: "نمایش",
      hide: "پنهان",
      sign_in: "ورود",
      signing_in: "در حال بررسی…",
      no_signup: "حساب‌ها توسط مدیر در فایل login.json مدیریت می‌شوند. ثبت‌نام وجود ندارد.",
      err_required: "نام کاربری و رمز عبور را وارد کنید.",
      err_invalid: "نام کاربری یا رمز عبور نادرست است.",
      err_locked: "تلاش‌های زیاد. {s} ثانیه صبر کنید.",
      err_login_file: "فایل login.json بارگذاری نشد.",
      err_crypto: "رمز هش‌شده نیاز به اتصال امن (HTTPS) دارد.",
      nav_dashboard: "داشبورد",
      nav_navigator: "ناوبری",
      nav_library: "کتابخانه مدل‌ها",
      nav_formulas: "فرمول‌ها",
      nav_history: "تاریخچه",
      nav_settings: "تنظیمات",
      logout: "خروج",
      signed_in_as: "ورود با حساب {name}",
      footer_powered: "قدرت گرفته از طاها قاسمی",
      dash_title: "خوش آمدید، {name}",
      dash_sub: "ماشین‌حساب‌های مهندسی آفلاین. همه محاسبات روی همین دستگاه انجام می‌شود.",
      hero_cta_nav: "شروع ناوبری",
      hero_cta_lib: "مرور مدل‌ها",
      stat_models: "مدل محاسباتی",
      stat_series: "سری مدل",
      stat_offline: "محاسبه آفلاین",
      stat_history: "نتیجه ذخیره‌شده",
      quick_start: "شروع از سطح ولتاژ",
      recent: "نتایج اخیر",
      no_recent: "هنوز نتیجه‌ای ذخیره نشده. یک محاسبه انجام دهید و «ذخیره» را بزنید.",
      view_all: "مشاهده همه",
      step_group: "۱ · سطح ولتاژ",
      step_system: "۲ · نوع سیستم",
      step_topic: "۳ · مبحث",
      step_model: "۴ · محاسبه",
      ac: "AC",
      dc: "DC",
      ac_only: "در این سطح ولتاژ فقط AC",
      models_count: "{n} مدل",
      back: "بازگشت",
      home: "خانه",
      navigator_title: "ناوبری",
      navigator_sub: "سطح ولتاژ، نوع سیستم و مبحث را انتخاب کنید تا محاسبه مناسب پیدا شود.",
      search: "جستجوی نام، فرمول یا شناسه…",
      all: "همه",
      library_title: "کتابخانه مدل‌ها",
      library_sub: "{n} ماشین‌حساب در سه سری، همه آفلاین.",
      no_results: "موردی با این جستجو پیدا نشد.",
      calculate: "محاسبه",
      reset: "بازنشانی",
      which_missing: "کدام مقادیر را ندارید؟",
      hide_alt: "پنهان‌کردن جایگزین‌ها",
      save_result: "ذخیره نتیجه",
      copy_results: "کپی نتایج",
      hint_solve: "فقط یک فیلد را خالی بگذارید تا خودکار محاسبه شود.",
      optional_inputs: "ورودی‌های اختیاری جایگزین",
      alt_title: "فرمول‌های جایگزین",
      alt_hint: "هر رابطه با مقادیری که وارد کرده‌اید محاسبه می‌شود. مقادیر ناقص فهرست شده‌اند.",
      alt_ready: "آماده",
      alt_needs: "نیاز به",
      alt_err: "خطا",
      results: "نتایج",
      solved_for: "محاسبه‌شده: {field}",
      guidance_title: "راهنمای مهندسی",
      saved: "در تاریخچه ذخیره شد",
      copied: "در کلیپ‌بورد کپی شد",
      copy_failed: "کپی انجام نشد",
      filled_defaults: "مقادیر پیش‌فرض بازگردانده شد",
      formulas_title: "فرمول‌ها و روابط",
      formulas_sub: "فرمول اصلی هر مدل به‌همراه روابط جایگزین.",
      history_title: "تاریخچه",
      history_sub: "نتایجی که روی این دستگاه ذخیره کرده‌اید.",
      history_empty: "هنوز نتیجه‌ای ذخیره نشده.",
      export_csv: "خروجی CSV",
      export_json: "خروجی JSON",
      clear_history: "پاک‌کردن تاریخچه",
      confirm_clear: "همه نتایج ذخیره‌شده روی این دستگاه حذف شوند؟",
      open: "باز کردن",
      delete: "حذف",
      settings_title: "تنظیمات",
      settings_sub: "زبان، ظاهر، نصب برنامه و حساب کاربری.",
      lang_label: "زبان",
      theme_label: "ظاهر",
      theme_dark: "تیره",
      theme_light: "روشن",
      install_label: "نصب به‌عنوان برنامه",
      install_status_yes: "قابل نصب است و آفلاین کار می‌کند.",
      install_btn: "دانلود برنامه",
      engine_label: "موتور محاسباتی",
      engine_desc: "موتور Python 3 (Pyodide) که به‌صورت محلی و در پس‌زمینه اجرا می‌شود.",
      about: "درباره",
      version: "نسخه",
      models_total: "تعداد مدل‌ها",
      offline_mode: "آفلاین",
      account: "حساب کاربری",
      topics_all: "همه مباحث",
      loading_catalog: "در حال بارگذاری مدل‌ها…",
      invalid_num: "فقط عدد معتبر وارد کنید (مثلاً 12.5).",
      unit: "واحد",
      update_ready: "نسخه جدید آماده است.",
      update_btn: "به‌روزرسانی",
      guidance_note: "این مدل به‌جای عدد، راهنمای مهندسی می‌دهد چون یک فرمول عمومی می‌توانست گمراه‌کننده باشد.",
      topics: {
        transformers: "ترانسفورماتورها", motors: "موتورها", cables: "کابل و هادی", circuits: "مدارها و الکترونیک",
        power: "توان و سیستم قدرت", protection: "حفاظت و اتصال کوتاه", high_voltage: "عایقی و فشار قوی",
        energy: "باتری و انرژی", general: "سایر محاسبات", extra: "افزونه‌های وب (TG.WX)"
      },
      series_names: { "TG.VL": "TG.VL · ۱۰۰ پروفایل", "TG.VX": "TG.VX · توسعه‌یافته", "TG.WX": "TG.WX · افزونه وب" },
    },
  };

  const TOPIC_ORDER = ["transformers", "motors", "cables", "circuits", "power", "protection", "high_voltage", "energy", "general", "extra"];
  const TOPIC_ICON = { transformers: "TR", motors: "M", cables: "CB", circuits: "Ω", power: "P", protection: "SC", high_voltage: "HV", energy: "E", general: "GN", extra: "+" };
  const GROUP_ICON = { lv: "LV", mv: "MV", hv: "HV", ehv: "EHV" };

  let lang = localStorage.getItem(LS.lang) === "fa" ? "fa" : "en";
  let theme = localStorage.getItem(LS.theme) === "light" ? "light" : "dark";
  const isFa = () => lang === "fa";
  const t = (key, vars) => {
    let s = I18N[lang][key];
    if (s === undefined) s = I18N.en[key];
    if (s === undefined) s = key;
    if (vars) for (const k of Object.keys(vars)) s = s.split("{" + k + "}").join(String(vars[k]));
    return s;
  };
  const nameOf = (m) => (isFa() ? m.name_fa : m.name_en);
  const labelOf = (f) => (isFa() ? f[1] : f[2]);
  const topicName = (k) => I18N[lang].topics[k] || k;

  function fmt(v) {
    if (typeof v === "string") return v; // "∞", "NaN"
    if (typeof v !== "number") return String(v);
    const a = Math.abs(v);
    let s;
    if (v !== 0 && (a >= 1e7 || a < 1e-4)) s = v.toExponential(4);
    else s = new Intl.NumberFormat("en-US", { maximumSignificantDigits: 6, useGrouping: false }).format(v);
    return isFa() ? toFaDigits(s) : s;
  }

  /* ---------- state ---------- */
  const state = {
    catalog: null,           // parsed catalog from the engine
    byId: {},
    engineStatus: "loading", // loading | ready | error
    engineError: "",
    nav: { group: null, system: null, topic: null },
    lib: { series: "all", topic: null, q: "" },
    fmQuery: "",
    cur: null,               // current calculator state
    deferredPrompt: null,
    user: null,
  };

  /* ---------- engine (Pyodide worker) ---------- */
  const engine = (function () {
    let worker = null, seq = 0, readyResolve, readyReject;
    const pending = new Map();
    const ready = new Promise((res, rej) => { readyResolve = res; readyReject = rej; });
    ready.catch(() => {});
    function start() {
      try {
        worker = new Worker("engine.worker.js", { type: "module" });
      } catch (e) {
        readyReject(e);
        return;
      }
      worker.onmessage = (e) => {
        const m = e.data;
        if (m.type === "ready") return readyResolve();
        if (m.type === "error") return readyReject(new Error(m.error));
        const p = pending.get(m.id);
        if (!p) return;
        pending.delete(m.id);
        if (m.ok) p.res(m.data); else p.rej(new Error(m.error));
      };
      worker.onerror = (e) => readyReject(new Error(e.message || "worker failed"));
    }
    async function call(payload) {
      await ready;
      const id = ++seq;
      const raw = await new Promise((res, rej) => {
        pending.set(id, { res, rej });
        worker.postMessage({ id, payload });
      });
      return JSON.parse(raw);
    }
    return { start, call, ready };
  })();

  /* ---------- session & auth ---------- */
  function getSession() {
    try {
      const s = JSON.parse(localStorage.getItem(LS.session) || "null");
      if (s && s.u && s.exp > Date.now()) return s;
    } catch (_) { /* ignore */ }
    localStorage.removeItem(LS.session);
    return null;
  }
  function saveSession(user) {
    localStorage.setItem(LS.session, JSON.stringify({ u: user.u, name: user.name, exp: Date.now() + SESSION_MS }));
  }
  async function sha256Hex(text) {
    const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
    return Array.from(new Uint8Array(buf)).map((b) => b.toString(16).padStart(2, "0")).join("");
  }
  async function authenticate(username, password) {
    const res = await fetch("login.json", { cache: "no-cache" });
    if (!res.ok) throw new Error(t("err_login_file"));
    const data = await res.json();
    const users = Array.isArray(data.users) ? data.users : [];
    const rec = users.find((x) => String(x.username || "").trim().toLowerCase() === username.toLowerCase());
    if (!rec) return null;
    const stored = String(rec.password || "");
    let ok;
    if (/^[a-f0-9]{64}$/i.test(stored)) {
      if (!window.crypto || !crypto.subtle) throw new Error(t("err_crypto"));
      ok = (await sha256Hex(password)) === stored.toLowerCase();
    } else {
      ok = password === stored;
    }
    return ok ? { u: String(rec.username).trim(), name: rec.name || rec.username } : null;
  }

  let failCount = 0, lockedUntil = 0, lockTimer = null;
  async function onLogin(e) {
    e.preventDefault();
    const err = $("#login-error");
    const btn = $("#login-submit");
    const remain = Math.ceil((lockedUntil - Date.now()) / 1000);
    if (remain > 0) { err.textContent = t("err_locked", { s: remain }); return; }
    const u = $("#login-user").value.trim();
    const p = $("#login-pass").value;
    if (!u || !p) { err.textContent = t("err_required"); return; }
    btn.disabled = true;
    btn.textContent = t("signing_in");
    err.textContent = "";
    try {
      const user = await authenticate(u, p);
      if (user) {
        failCount = 0;
        saveSession(user);
        $("#login-pass").value = "";
        state.user = user;
        showApp();
        toast(t("signed_in_as", { name: user.name }));
      } else {
        failCount += 1;
        if (failCount >= 5) {
          failCount = 0;
          lockedUntil = Date.now() + 30000;
          err.textContent = t("err_locked", { s: 30 });
        } else {
          err.textContent = t("err_invalid");
        }
        $("#login-pass").select();
      }
    } catch (ex) {
      err.textContent = ex.message || t("err_login_file");
    } finally {
      btn.disabled = false;
      btn.textContent = t("sign_in");
    }
  }
  function logout() {
    localStorage.removeItem(LS.session);
    state.user = null;
    location.hash = "#/dashboard";
    showLogin();
  }

  /* ---------- toasts ---------- */
  function toast(msg, type, action) {
    const wrap = $("#toast");
    const el = document.createElement("div");
    el.className = "toast" + (type === "err" ? " err" : "");
    el.textContent = msg;
    if (action) {
      const b = document.createElement("button");
      b.className = "btn btn-primary";
      b.style.padding = "4px 10px";
      b.textContent = action.label;
      b.addEventListener("click", () => { action.run(); el.remove(); });
      el.appendChild(b);
    }
    wrap.appendChild(el);
    setTimeout(() => el.remove(), action ? 9000 : 2800);
  }

  /* ---------- theming & language ---------- */
  function applyTheme() {
    document.documentElement.setAttribute("data-theme", theme);
    document.querySelector('meta[name="theme-color"]').setAttribute("content", theme === "light" ? "#eef2f9" : "#070b14");
    $("#btn-theme").textContent = theme === "dark" ? "☀" : "🌙";
  }
  function applyLang() {
    document.documentElement.lang = lang;
    document.documentElement.dir = isFa() ? "rtl" : "ltr";
    document.documentElement.setAttribute("data-lang", lang);
    $("#btn-lang").textContent = isFa() ? "EN" : "فا";
    $$("[data-i18n]").forEach((el) => { el.textContent = t(el.dataset.i18n); });
    $$("[data-i18n-ph]").forEach((el) => { el.placeholder = t(el.dataset.i18nPh); });
    updatePwButton();
    setEnginePill();
    $("#user-chip").textContent = state.user ? t("signed_in_as", { name: state.user.name }) : "";
  }
  function setLang(l) { lang = l; localStorage.setItem(LS.lang, l); applyLang(); render(); }
  function setTheme(th) { theme = th; localStorage.setItem(LS.theme, th); applyTheme(); }
  function updatePwButton() {
    const btn = $("#btn-pw");
    const shown = $("#login-pass").type === "text";
    btn.textContent = shown ? t("hide") : t("show");
  }
  function setEnginePill() {
    const pill = $("#engine-pill");
    pill.classList.remove("pill-muted", "pill-ok", "pill-err");
    if (state.engineStatus === "ready") { pill.textContent = t("engine_ready"); pill.classList.add("pill-ok"); }
    else if (state.engineStatus === "error") { pill.textContent = t("engine_error"); pill.classList.add("pill-err"); pill.title = state.engineError; }
    else { pill.textContent = t("engine_loading"); pill.classList.add("pill-muted"); }
  }

  /* ---------- install / PWA ---------- */
  function isStandalone() {
    return window.matchMedia("(display-mode: standalone)").matches || window.navigator.standalone === true;
  }
  function isIOS() {
    const ua = navigator.userAgent;
    return /iPhone|iPad|iPod/i.test(ua) || (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
  }
  function setupInstall() {
    const btn = $("#btn-install");
    if (isStandalone()) { btn.classList.add("hidden"); return; }
    btn.classList.remove("hidden");
    window.addEventListener("beforeinstallprompt", (e) => { e.preventDefault(); state.deferredPrompt = e; });
    window.addEventListener("appinstalled", () => {
      state.deferredPrompt = null;
      btn.classList.add("hidden");
      toast(t("installed_ok"));
    });
    btn.addEventListener("click", async () => {
      if (state.deferredPrompt) {
        const p = state.deferredPrompt;
        p.prompt();
        const choice = await p.userChoice;
        state.deferredPrompt = null;
        if (choice && choice.outcome === "accepted") btn.classList.add("hidden");
        return;
      }
      openInstallModal();
    });
  }
  function openInstallModal() {
    const steps = isIOS() ? t("install_ios") : /Android/i.test(navigator.userAgent) ? t("install_android") : t("install_desktop");
    $("#modal-body").innerHTML = `<p>${esc(t("install_intro"))}</p><ol><li>${esc(steps)}</li></ol>`;
    $("#modal").classList.remove("hidden");
  }
  function registerSW() {
    if (!("serviceWorker" in navigator)) return;
    navigator.serviceWorker.register("sw.js").then((reg) => {
      reg.addEventListener("updatefound", () => {
        const nw = reg.installing;
        if (!nw) return;
        nw.addEventListener("statechange", () => {
          if (nw.state === "installed" && navigator.serviceWorker.controller) {
            toast(t("update_ready"), null, { label: t("update_btn"), run: () => nw.postMessage({ type: "SKIP_WAITING" }) });
          }
        });
      });
    }).catch(() => { /* offline support needs https or localhost */ });
    // Reload only when an update replaces an older controller (not on the first install).
    const hadController = !!navigator.serviceWorker.controller;
    let reloaded = false;
    navigator.serviceWorker.addEventListener("controllerchange", () => {
      if (hadController && !reloaded) { reloaded = true; location.reload(); }
    });
  }

  /* ---------- catalog ---------- */
  async function loadCatalog() {
    const r = await engine.call({ op: "catalog" });
    if (!r.ok) throw new Error(r.error || "catalog");
    state.catalog = r;
    state.byId = {};
    r.models.forEach((m) => { state.byId[m.id] = m; });
  }
  const DCO = () => new Set(state.catalog.dc_only);
  const DCM = () => new Set(state.catalog.dc_models);
  function allowed(m, system, groupId) {
    if (m.series === "TG.WX") return true;
    if (system === "dc" && !DCM().has(m.key)) return false;
    if (system === "ac" && DCO().has(m.key)) return false;
    if (["mv", "hv", "ehv"].includes(groupId) && ["motors", "circuits", "energy"].includes(m.topic)) return false;
    return true;
  }
  function modelsOf(series) {
    return state.catalog.models.filter((m) => series === "all" || m.series === series);
  }
  const groupName = (g) => (isFa() ? g.fa : g.en);

  /* ---------- views ---------- */
  const view = () => $("#view");
  function setView(html) {
    view().innerHTML = html;
    view().scrollTop = 0;
    window.scrollTo(0, 0);
  }
  function loadingView() {
    setView(`<div class="empty glass">${esc(t("loading_catalog"))}</div>`);
  }
  function setActiveNav(route) {
    $$(".sidebar a").forEach((a) => a.classList.toggle("active", a.dataset.route === route));
  }

  function render() {
    if ($("#app").classList.contains("hidden")) return;
    if (state.cur && $("#fields")) collect(); // keep what the user typed across re-renders
    const h = location.hash.replace(/^#\/?/, "");
    const [path] = h.split("?");
    const parts = path.split("/").filter(Boolean);
    if (!state.catalog) {
      setActiveNav(parts[0] || "dashboard");
      if (state.engineStatus === "error") {
        setView(`<div class="error-box" role="alert">${esc(t("engine_error"))}: ${esc(state.engineError)}</div>`);
      } else {
        loadingView();
      }
      return;
    }
    if (parts[0] === "m" && parts[1]) {
      setActiveNav("library");
      return renderModel(decodeURIComponent(parts[1]));
    }
    const route = parts[0] || "dashboard";
    setActiveNav(route);
    switch (route) {
      case "navigator": return renderNavigator();
      case "library": return renderLibrary();
      case "formulas": return renderFormulas();
      case "history": return renderHistory();
      case "settings": return renderSettings();
      default: return renderDashboard();
    }
  }

  function histList() {
    try { return JSON.parse(localStorage.getItem(LS.history) || "[]"); } catch (_) { return []; }
  }
  function saveHist(list) {
    localStorage.setItem(LS.history, JSON.stringify(list.slice(0, 300)));
  }

  /* dashboard */
  function renderDashboard() {
    const name = state.user ? state.user.name : "";
    const groups = state.catalog.groups;
    const hist = histList();
    setView(`
      <section class="glass hero">
        <h1>${esc(t("dash_title", { name }))}</h1>
        <p>${esc(t("dash_sub"))}</p>
        <div class="toolbar">
          <a class="btn btn-primary" href="#/navigator">⚡ ${esc(t("hero_cta_nav"))}</a>
          <a class="btn" href="#/library">▦ ${esc(t("hero_cta_lib"))}</a>
        </div>
      </section>
      <div class="stats">
        <div class="glass stat"><b>${fmt(state.catalog.models.length)}</b><span>${esc(t("stat_models"))}</span></div>
        <div class="glass stat"><b>3</b><span>${esc(t("stat_series"))}</span></div>
        <div class="glass stat"><b>100%</b><span>${esc(t("stat_offline"))}</span></div>
        <div class="glass stat"><b>${fmt(hist.length)}</b><span>${esc(t("stat_history"))}</span></div>
      </div>
      <div class="step-title">${esc(t("quick_start"))}</div>
      <div class="grid">
        ${groups.map((g) => `
          <button class="glass tile" type="button" data-group="${esc(g.id)}">
            <span class="t-ico">${GROUP_ICON[g.id] || "⚡"}</span>
            <h3>${esc(groupName(g))}</h3>
            <p>${g.systems.map((s) => (s === "dc" ? t("dc") : t("ac"))).join(" · ")}</p>
            <span class="meta">→</span>
          </button>`).join("")}
      </div>
      <div class="step-title">${esc(t("recent"))}</div>
      ${hist.length ? `<div class="grid">${hist.slice(0, 3).map(historyCard).join("")}</div>
        <div class="toolbar"><a class="link-btn" href="#/history">${esc(t("view_all"))} →</a></div>`
        : `<div class="glass empty">${esc(t("no_recent"))}</div>`}
    `);
    $$("[data-group]").forEach((b) => b.addEventListener("click", () => {
      state.nav = { group: b.dataset.group, system: null, topic: null };
      location.hash = "#/navigator";
    }));
  }

  /* navigator */
  function renderNavigator() {
    const nav = state.nav;
    const group = nav.group ? state.catalog.groups.find((g) => g.id === nav.group) : null;
    const crumbs = [];
    crumbs.push(`<button type="button" data-crumb="0">${esc(t("home"))}</button>`);
    if (group) crumbs.push(`<button type="button" data-crumb="1">${esc(groupName(group))}</button>`);
    if (nav.system) crumbs.push(`<button type="button" data-crumb="2">${esc(nav.system === "dc" ? t("dc") : t("ac"))}</button>`);
    if (nav.topic) crumbs.push(`<span>${esc(topicName(nav.topic))}</span>`);

    let body = "";
    if (!group) {
      body = `<div class="step-title">${esc(t("step_group"))}</div>
        <div class="grid">${state.catalog.groups.map((g) => `
          <button class="glass tile" type="button" data-pick-group="${esc(g.id)}">
            <span class="t-ico">${GROUP_ICON[g.id] || "⚡"}</span>
            <h3>${esc(groupName(g))}</h3>
            <p>${g.systems.length > 1 ? "AC · DC" : esc(t("ac_only"))}</p>
          </button>`).join("")}</div>`;
    } else if (group.systems.length > 1 && !nav.system) {
      body = `<div class="step-title">${esc(t("step_system"))}</div>
        <div class="grid grid-lg">
          <button class="glass tile" type="button" data-pick-system="ac"><span class="t-ico">AC</span><h3>${esc(t("ac"))}</h3><p>~ 50 / 60 Hz</p></button>
          <button class="glass tile" type="button" data-pick-system="dc"><span class="t-ico">DC</span><h3>${esc(t("dc"))}</h3><p>—</p></button>
        </div>`;
    } else if (!nav.system) {
      nav.system = "ac";
    }

    if (group && (nav.system || group.systems.length === 1) && !nav.topic) {
      const sys = nav.system || "ac";
      const counts = {};
      state.catalog.models.forEach((m) => { if (allowed(m, sys, group.id)) counts[m.topic] = (counts[m.topic] || 0) + 1; });
      body = `<div class="step-title">${esc(t("step_topic"))}</div>
        <div class="grid">${TOPIC_ORDER.filter((k) => counts[k]).map((k) => `
          <button class="glass tile" type="button" data-pick-topic="${k}">
            <span class="t-ico">${TOPIC_ICON[k]}</span>
            <h3>${esc(topicName(k))}</h3>
            <span class="meta">${esc(t("models_count", { n: fmt(counts[k]) }))}</span>
          </button>`).join("")}</div>`;
    } else if (group && nav.topic) {
      const sys = nav.system || "ac";
      const list = state.catalog.models.filter((m) => m.topic === nav.topic && allowed(m, sys, group.id));
      body = `<div class="step-title">${esc(t("step_model"))}</div>
        <div class="grid">${list.map(modelCard).join("")}</div>`;
    }

    setView(`
      <div class="page-head"><div>
        <div class="crumbs">${crumbs.join(" / ")}</div>
        <h1>${esc(t("navigator_title"))}</h1>
        <p>${esc(t("navigator_sub"))}</p>
      </div></div>
      ${body}`);

    $$("[data-crumb]").forEach((b) => b.addEventListener("click", () => {
      const lvl = +b.dataset.crumb;
      if (lvl === 0) state.nav = { group: null, system: null, topic: null };
      if (lvl === 1) state.nav = { group: nav.group, system: null, topic: null };
      if (lvl === 2) state.nav = { group: nav.group, system: nav.system, topic: null };
      renderNavigator();
    }));
    $$("[data-pick-group]").forEach((b) => b.addEventListener("click", () => {
      const g = state.catalog.groups.find((x) => x.id === b.dataset.pickGroup);
      state.nav = { group: g.id, system: g.systems.length === 1 ? g.systems[0] : null, topic: null };
      renderNavigator();
    }));
    $$("[data-pick-system]").forEach((b) => b.addEventListener("click", () => {
      state.nav.system = b.dataset.pickSystem; state.nav.topic = null; renderNavigator();
    }));
    $$("[data-pick-topic]").forEach((b) => b.addEventListener("click", () => {
      state.nav.topic = b.dataset.pickTopic; renderNavigator();
    }));
    bindModelCards(view());
  }

  function modelCard(m) {
    return `<button class="glass model-card" type="button" data-model="${esc(m.id)}">
      <span class="id">${esc(m.id)}</span>
      <h3>${esc(nameOf(m))}</h3>
      <code>${esc(m.formula)}</code>
    </button>`;
  }
  function bindModelCards(root) {
    $$("[data-model]", root).forEach((b) => b.addEventListener("click", () => {
      location.hash = "#/m/" + encodeURIComponent(b.dataset.model);
    }));
  }

  /* library */
  function renderLibrary() {
    const lib = state.lib;
    const series = ["all", "TG.VL", "TG.VX", "TG.WX"];
    setView(`
      <div class="page-head">
        <div>
          <h1>${esc(t("library_title"))}</h1>
          <p>${esc(t("library_sub", { n: fmt(state.catalog.models.length) }))}</p>
        </div>
        <div class="searchbar"><input id="lib-q" type="search" placeholder="${esc(t("search"))}" value="${esc(lib.q)}" autocomplete="off" spellcheck="false"></div>
      </div>
      <div class="chips" id="lib-series">${series.map((s) => `<button class="chip ${lib.series === s ? "active" : ""}" type="button" data-series="${s}">${s === "all" ? esc(t("all")) : esc(t("series_names")[s] || s)}</button>`).join("")}</div>
      <div class="chips" id="lib-topics"></div>
      <div class="grid" id="lib-list"></div>`);
    $$("[data-series]").forEach((b) => b.addEventListener("click", () => {
      lib.series = b.dataset.series; lib.topic = null; renderLibrary();
    }));
    $("#lib-q").addEventListener("input", (e) => { lib.q = e.target.value; renderLibList(); });
    renderLibTopics();
    renderLibList();
  }
  function renderLibTopics() {
    const lib = state.lib;
    const present = new Set(modelsOf(lib.series).map((m) => m.topic));
    const html = [`<button class="chip ${!lib.topic ? "active" : ""}" type="button" data-topic="">${esc(t("topics_all"))}</button>`]
      .concat(TOPIC_ORDER.filter((k) => present.has(k)).map((k) => `<button class="chip ${lib.topic === k ? "active" : ""}" type="button" data-topic="${k}">${esc(topicName(k))}</button>`));
    $("#lib-topics").innerHTML = html.join("");
    $$("[data-topic]", $("#lib-topics")).forEach((b) => b.addEventListener("click", () => {
      lib.topic = b.dataset.topic || null; renderLibTopics(); renderLibList();
    }));
  }
  function renderLibList() {
    const lib = state.lib;
    const q = lib.q.trim().toLowerCase();
    const list = modelsOf(lib.series).filter((m) => {
      if (lib.topic && m.topic !== lib.topic) return false;
      if (!q) return true;
      return (m.id + " " + m.name_en + " " + m.name_fa + " " + m.formula + " " + m.key).toLowerCase().includes(q);
    });
    const box = $("#lib-list");
    box.innerHTML = list.length ? list.map(modelCard).join("") : `<div class="glass empty">${esc(t("no_results"))}</div>`;
    bindModelCards(box);
  }

  /* model calculator */
  function fieldHTML(m, f, defaults) {
    const key = f[0];
    const val = defaults && defaults[key] != null ? defaults[key] : f[4];
    return `<label class="field" for="f-${esc(key)}">
      <span>${esc(labelOf(f))}</span>
      <div class="unit-wrap">
        <input id="f-${esc(key)}" data-key="${esc(key)}" inputmode="decimal" dir="ltr" autocomplete="off" spellcheck="false" value="${esc(val)}">
        <span class="unit">${esc(f[3] || "")}</span>
      </div>
    </label>`;
  }

  function renderModel(id) {
    const m = state.byId[id];
    if (!m) { setView(`<div class="glass empty">Not found</div>`); return; }
    const opt = new Set(m.optional || []);
    const main = m.fields.filter((f) => !opt.has(f[0]));
    const extra = m.fields.filter((f) => opt.has(f[0]));
    const prev = state.cur && state.cur.m.id === m.id ? state.cur : null;
    state.cur = { m, values: prev ? prev.values : null, last: prev ? prev.last : null, altOpen: prev ? prev.altOpen : false };
    const formula = m.formula;
    setView(`
      <div class="crumbs"><a class="link-btn" href="#/library">← ${esc(t("back"))}</a> <span>·</span> <span>${esc(m.series)}</span></div>
      <div class="calc">
        <section class="glass calc-form">
          <div class="calc-meta">
            <div class="id">${esc(m.id)}</div>
            <h1>${esc(nameOf(m))}</h1>
          </div>
          <div class="formula-box">${esc(formula)}</div>
          <div class="fields" id="fields">
            ${main.map((f) => fieldHTML(m, f, state.cur.values)).join("")}
            ${extra.length ? `<div class="divider">${esc(t("optional_inputs"))}</div>${extra.map((f) => fieldHTML(m, f, state.cur.values)).join("")}` : ""}
          </div>
          <p class="hint">${esc(t("hint_solve"))}</p>
          <div class="actions">
            <button class="btn btn-primary" type="button" id="btn-calc">${esc(t("calculate"))}</button>
            <button class="btn" type="button" id="btn-alt">${esc(t("which_missing"))}</button>
            <button class="btn btn-ghost" type="button" id="btn-reset">${esc(t("reset"))}</button>
          </div>
        </section>
        <section class="glass calc-out">
          <div id="out"><div class="empty">${esc(state.engineStatus === "ready" ? "⚡" : t("engine_loading"))}</div></div>
          <div id="alt" class="hidden"></div>
        </section>
      </div>`);
    const btnCalc = $("#btn-calc");
    btnCalc.addEventListener("click", runCalc);
    if (state.cur.last) renderResults();
    if (state.cur.altOpen) {
      $("#alt").classList.remove("hidden");
      $("#btn-alt").textContent = t("hide_alt");
      runAlt();
    }
    $("#btn-alt").addEventListener("click", toggleAlt);
    $("#btn-reset").addEventListener("click", () => {
      $$("#fields input").forEach((inp) => {
        const f = m.fields.find((x) => x[0] === inp.dataset.key);
        inp.value = f ? f[4] : "";
      });
      state.cur.last = null;
      $("#out").innerHTML = `<div class="empty">⚡</div>`;
      toast(t("filled_defaults"));
    });
    $("#fields").addEventListener("keydown", (e) => { if (e.key === "Enter") { e.preventDefault(); runCalc(); } });
    if (state.engineStatus !== "ready") {
      engine.ready.then(() => { if (state.cur && state.cur.m.id === m.id) $("#out").innerHTML = `<div class="empty">⚡</div>`; }).catch(() => {});
    }
  }

  function collect() {
    const data = {};
    $$("#fields input").forEach((inp) => { data[inp.dataset.key] = normalizeNum(inp.value); });
    if (state.cur) state.cur.values = data;
    return data;
  }
  function fieldLabelFor(m, key) {
    const f = m.fields.find((x) => x[0] === key);
    return f ? labelOf(f) : key;
  }

  function showOutError(msg) {
    const out = $("#out");
    if (out) out.innerHTML = `<div class="error-box" role="alert">${esc(msg)}</div>`;
    else toast(msg, "err");
  }

  async function runCalc() {
    const cur = state.cur;
    if (!cur) return;
    const m = cur.m;
    const data = collect();
    cur.values = data;
    const btn = $("#btn-calc");
    btn.disabled = true;
    try {
      const r = await engine.call({ op: "calc", key: m.key, data });
      if (!r.ok) { cur.last = null; showOutError(r.error); return; }
      if (r.status === "guidance") {
        cur.last = null;
        $("#out").innerHTML = `<div class="notice"><b>${esc(t("guidance_title"))}</b><p style="margin:8px 0 0">${esc(r.message)}</p><p class="tiny muted" style="margin:8px 0 0">${esc(t("guidance_note"))}</p></div>`;
        return;
      }
      cur.last = { results: r.results, solved: r.solved, data };
      renderResults();
      if (cur.altOpen) runAlt();
    } catch (e) {
      cur.last = null;
      showOutError(e.message || "Error");
    } finally {
      btn.disabled = false;
    }
  }

  function renderResults() {
    const cur = state.cur;
    const last = cur.last;
    if (!last) return;
    const m = cur.m;
    const entries = Object.entries(last.results);
    let html = `<div class="step-title" style="margin-top:0">${esc(t("results"))}</div><div class="results">`;
    entries.forEach(([k, v], i) => {
      html += `<div class="result ${i === 0 ? "big" : ""}"><span class="k">${esc(k)}</span><span class="v">${esc(fmt(v))}</span></div>`;
    });
    html += `</div>`;
    if (last.solved) {
      html += `<p class="solved-note">✓ ${esc(t("solved_for", { field: fieldLabelFor(m, last.solved.key) }))}: <b dir="ltr">${esc(fmt(last.solved.value))}</b></p>`;
    }
    html += `<div class="toolbar">
      <button class="btn" type="button" id="btn-save">💾 ${esc(t("save_result"))}</button>
      <button class="btn btn-ghost" type="button" id="btn-copy">⧉ ${esc(t("copy_results"))}</button>
    </div>`;
    $("#out").innerHTML = html;
    $("#btn-save").addEventListener("click", saveCurrent);
    $("#btn-copy").addEventListener("click", copyCurrent);
  }

  function saveCurrent() {
    const cur = state.cur;
    if (!cur || !cur.last) return;
    const list = histList();
    list.unshift({ id: cur.m.id, name_en: cur.m.name_en, name_fa: cur.m.name_fa, at: new Date().toISOString(), inputs: cur.last.data, results: cur.last.results });
    saveHist(list);
    toast(t("saved"));
  }
  async function copyCurrent() {
    const cur = state.cur;
    if (!cur || !cur.last) return;
    const text = Object.entries(cur.last.results).map(([k, v]) => `${k}: ${v}`).join("\n");
    try {
      await navigator.clipboard.writeText(text);
      toast(t("copied"));
    } catch (_) {
      toast(t("copy_failed"), "err");
    }
  }

  function toggleAlt() {
    const cur = state.cur;
    cur.altOpen = !cur.altOpen;
    $("#alt").classList.toggle("hidden", !cur.altOpen);
    $("#btn-alt").textContent = cur.altOpen ? t("hide_alt") : t("which_missing");
    if (cur.altOpen) runAlt();
  }

  async function runAlt() {
    const cur = state.cur;
    const m = cur.m;
    const box = $("#alt");
    if (!m.variants || !m.variants.length) {
      box.innerHTML = `<div class="alt-list"><div class="alt"><span class="muted">—</span></div></div>`;
      return;
    }
    const data = collect();
    try {
      const r = await engine.call({ op: "alt", key: m.key, data });
      if (!r.ok) { box.innerHTML = `<div class="error-box">${esc(r.error)}</div>`; return; }
      box.innerHTML = `<div class="step-title">${esc(t("alt_title"))}</div>
        <p class="tiny muted" style="margin:0 0 4px">${esc(t("alt_hint"))}</p>
        <div class="alt-list">${r.rows.map((row) => altRow(m, row)).join("")}</div>`;
    } catch (e) {
      box.innerHTML = `<div class="error-box">${esc(e.message)}</div>`;
    }
  }
  function altRow(m, row) {
    let tag;
    if (row.error) tag = `<span class="tag tag-err">${esc(t("alt_err"))}</span>`;
    else if (row.ready) tag = `<span class="tag tag-ok">${esc(t("alt_ready"))} · ${esc(fmt(row.result))} ${esc(row.unit)}</span>`;
    else tag = `<span class="tag tag-need">${esc(t("alt_needs"))}: ${esc(row.missing.map((k) => fieldLabelFor(m, k)).join(", "))}</span>`;
    const name = isFa() ? row.out_fa : row.out_en;
    return `<div class="alt">
      <div class="alt-head"><b>${esc(name)}</b>${tag}</div>
      <div class="f">${esc(row.formula)}</div>
      ${row.ready && row.substituted ? `<div class="sub">${esc(row.substituted)}</div>` : ""}
      ${row.error ? `<div class="sub" style="color:var(--danger)">${esc(row.error)}</div>` : ""}
    </div>`;
  }

  /* formulas */
  function renderFormulas() {
    setView(`
      <div class="page-head">
        <div><h1>${esc(t("formulas_title"))}</h1><p>${esc(t("formulas_sub"))}</p></div>
        <div class="searchbar"><input id="fm-q" type="search" placeholder="${esc(t("search"))}" value="${esc(state.fmQuery)}" autocomplete="off" spellcheck="false"></div>
      </div>
      <div class="grid" id="fm-list" style="grid-template-columns:1fr"></div>`);
    $("#fm-q").addEventListener("input", (e) => { state.fmQuery = e.target.value; drawFormulas(); });
    drawFormulas();
  }
  function drawFormulas() {
    const q = state.fmQuery.trim().toLowerCase();
    const rows = state.catalog.models.filter((m) => {
      if (!q) return true;
      const alts = (m.variants || []).map((v) => v.formula + " " + (isFa() ? v.out_fa : v.out_en)).join(" ");
      return (m.id + " " + m.name_en + " " + m.name_fa + " " + m.formula + " " + alts).toLowerCase().includes(q);
    });
    $("#fm-list").innerHTML = rows.length ? rows.map((m) => `
      <a class="glass formula-row" href="#/m/${encodeURIComponent(m.id)}" style="text-decoration:none;color:inherit">
        <span class="tiny" style="color:var(--accent);font-weight:800">${esc(m.id)} · ${esc(nameOf(m))}</span>
        <span class="f">${esc(m.formula)}</span>
        ${(m.variants || []).slice(0, 4).map((v) => `<span class="tiny muted">${esc(isFa() ? v.out_fa : v.out_en)}: <span dir="ltr">${esc(v.formula)}</span></span>`).join("")}
      </a>`).join("") : `<div class="glass empty">${esc(t("no_results"))}</div>`;
  }

  /* history */
  function historyCard(h) {
    const m = state.byId[h.id];
    const name = isFa() ? h.name_fa : h.name_en;
    const when = new Date(h.at).toLocaleString(isFa() ? "fa-IR" : "en-US");
    const res = Object.entries(h.results || {}).map(([k, v]) => `${k} = ${fmt(v)}`).join("\n");
    return `<div class="glass history-item">
      <span class="when">${esc(h.id)} · ${esc(when)}</span>
      <b>${esc(name)}</b>
      <pre>${esc(res)}</pre>
      ${m ? `<a class="link-btn" href="#/m/${encodeURIComponent(h.id)}">${esc(t("open"))} →</a>` : ""}
    </div>`;
  }
  function renderHistory() {
    const list = histList();
    setView(`
      <div class="page-head">
        <div><h1>${esc(t("history_title"))}</h1><p>${esc(t("history_sub"))}</p></div>
      </div>
      <div class="toolbar">
        <button class="btn" type="button" id="h-csv" ${list.length ? "" : "disabled"}>⇩ ${esc(t("export_csv"))}</button>
        <button class="btn" type="button" id="h-json" ${list.length ? "" : "disabled"}>⇩ ${esc(t("export_json"))}</button>
        <button class="btn btn-ghost" type="button" id="h-clear" ${list.length ? "" : "disabled"}>🗑 ${esc(t("clear_history"))}</button>
      </div>
      ${list.length ? `<div class="grid" style="grid-template-columns:1fr">${list.map(historyCard).join("")}</div>`
        : `<div class="glass empty">${esc(t("history_empty"))}</div>`}`);
    $("#h-csv").addEventListener("click", () => download("voltex-history.csv", toCSV(list), "text/csv"));
    $("#h-json").addEventListener("click", () => download("voltex-history.json", JSON.stringify(list, null, 2), "application/json"));
    $("#h-clear").addEventListener("click", () => {
      if (confirm(t("confirm_clear"))) { localStorage.removeItem(LS.history); renderHistory(); }
    });
  }
  function toCSV(list) {
    const q = (s) => '"' + String(s).replace(/"/g, '""') + '"';
    const rows = [["time", "model_id", "model_name", "inputs", "results"].join(",")];
    list.forEach((h) => {
      const inputs = Object.entries(h.inputs || {}).map(([k, v]) => `${k}=${v}`).join("; ");
      const results = Object.entries(h.results || {}).map(([k, v]) => `${k}=${v}`).join("; ");
      rows.push([h.at, h.id, h.name_en, inputs, results].map(q).join(","));
    });
    return "\ufeff" + rows.join("\n");
  }
  function download(name, text, type) {
    const blob = new Blob([text], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = name;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  /* settings */
  function renderSettings() {
    const cat = state.catalog;
    const u = state.user || getSession() || { name: "—", u: "—" };
    const installed = isStandalone();
    setView(`
      <div class="page-head"><div><h1>${esc(t("settings_title"))}</h1><p>${esc(t("settings_sub"))}</p></div></div>
      <div class="settings">
        <div class="glass setting">
          <div><b>${esc(t("lang_label"))}</b></div>
          <div class="seg" role="group">
            <button type="button" data-lang="en" class="${lang === "en" ? "active" : ""}">English</button>
            <button type="button" data-lang="fa" class="${lang === "fa" ? "active" : ""}">فارسی</button>
          </div>
        </div>
        <div class="glass setting">
          <div><b>${esc(t("theme_label"))}</b></div>
          <div class="seg" role="group">
            <button type="button" data-theme="dark" class="${theme === "dark" ? "active" : ""}">${esc(t("theme_dark"))}</button>
            <button type="button" data-theme="light" class="${theme === "light" ? "active" : ""}">${esc(t("theme_light"))}</button>
          </div>
        </div>
        <div class="glass setting">
          <div><b>${esc(t("install_label"))}</b><div class="tiny muted">${installed ? "✓" : esc(t("install_status_yes"))}</div></div>
          ${installed ? "" : `<button class="btn btn-install" type="button" id="s-install">⬇ ${esc(t("install_btn"))}</button>`}
        </div>
        <div class="glass setting">
          <div><b>${esc(t("engine_label"))}</b><div class="tiny muted">${esc(t("engine_desc"))}</div></div>
          <span class="pill ${state.engineStatus === "ready" ? "pill-ok" : state.engineStatus === "error" ? "pill-err" : "pill-muted"}">${esc(state.engineStatus === "ready" ? t("engine_ready") : state.engineStatus === "error" ? t("engine_error") : t("engine_loading"))}</span>
        </div>
        <div class="glass setting" style="align-items:flex-start">
          <div class="kv">
            <span>${esc(t("version"))}</span><span>1.0.0 (web)</span>
            <span>${esc(t("models_total"))}</span><span>${esc(fmt(cat.models.length))}</span>
            <span>${esc(t("offline_mode"))}</span><span>✓</span>
            <span>${esc(t("account"))}</span><span>${esc(u.name || u.u)}</span>
          </div>
        </div>
        <div><button class="btn" type="button" id="s-logout">⎋ ${esc(t("logout"))}</button></div>
      </div>`);
    $$("[data-lang]").forEach((b) => b.addEventListener("click", () => setLang(b.dataset.lang)));
    $$("[data-theme]").forEach((b) => b.addEventListener("click", () => { setTheme(b.dataset.theme); render(); }));
    const si = $("#s-install");
    if (si) si.addEventListener("click", () => $("#btn-install").click());
    $("#s-logout").addEventListener("click", logout);
  }

  /* ---------- screens ---------- */
  function showLogin() {
    document.body.classList.remove("in-app");
    $("#app").classList.add("hidden");
    $("#login-screen").classList.remove("hidden");
    $("#user-chip").textContent = "";
    $("#login-user").focus();
  }
  function showApp() {
    document.body.classList.add("in-app");
    $("#login-screen").classList.add("hidden");
    $("#app").classList.remove("hidden");
    const s = state.user || getSession();
    state.user = s;
    $("#user-chip").textContent = s ? t("signed_in_as", { name: s.name }) : "";
    if (!location.hash || location.hash === "#" || location.hash.startsWith("#/login")) location.hash = "#/dashboard";
    render();
  }

  /* ---------- wiring ---------- */
  function setupEvents() {
    $("#login-form").addEventListener("submit", onLogin);
    $("#btn-pw").addEventListener("click", () => {
      const inp = $("#login-pass");
      inp.type = inp.type === "password" ? "text" : "password";
      updatePwButton();
    });
    $("#btn-lang").addEventListener("click", () => setLang(isFa() ? "en" : "fa"));
    $("#btn-theme").addEventListener("click", () => { setTheme(theme === "dark" ? "light" : "dark"); });
    $("#btn-logout").addEventListener("click", logout);
    $("#modal-close").addEventListener("click", () => $("#modal").classList.add("hidden"));
    $("#modal").addEventListener("click", (e) => { if (e.target.id === "modal") $("#modal").classList.add("hidden"); });
    document.addEventListener("keydown", (e) => { if (e.key === "Escape") $("#modal").classList.add("hidden"); });
    window.addEventListener("hashchange", render);
  }

  function boot() {
    applyTheme();
    applyLang();
    setupEvents();
    setupInstall();
    registerSW();
    engine.start();
    engine.ready.then(loadCatalog).then(() => {
      state.engineStatus = "ready";
      applyLang();
      render();
    }).catch((e) => {
      state.engineStatus = "error";
      state.engineError = e && e.message || String(e);
      applyLang();
      showOutError(state.engineError);
      render();
    });
    const s = getSession();
    if (s) { state.user = s; showApp(); } else { showLogin(); }
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
