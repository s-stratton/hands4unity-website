/**
 * Hands 4 Unity — website form handler.
 *
 * Receives the contact, get involved and newsletter forms from hands4unity.org,
 * saves each submission as a row in this spreadsheet and emails it to info@.
 *
 * Lives in the Apps Script project attached to the "Hands 4 Unity website" Google Sheet
 * (Extensions → Apps Script). After changing this file, paste it into that editor and
 * redeploy: Deploy → Manage deployments → edit → Version: New version → Deploy.
 *
 * No secrets belong in this file: it is published in the public website repository.
 */

var NOTIFY_EMAIL = "info@hands4unity.org";
var MIN_FILL_MS = 3000;            // faster than this is a bot
var MAX_PER_10_MIN = 40;           // overall cap, protects the daily email quota
var MAX_LEN = { name: 120, email: 200, phone: 40, subject: 200, message: 5000, page: 300 };

var FORMS = {
  contact: {
    tab: "Messages",
    headers: ["Received", "Name", "Email", "Phone", "Subject", "Message", "Page"],
    required: ["name", "email", "subject", "message", "consent"],
    row: function (d) { return [d.name, d.email, d.phone, d.subject, d.message, d.page]; }
  },
  involve: {
    tab: "Get Involved",
    headers: ["Received", "Name", "Email", "Phone", "Interested in", "Message", "Page"],
    required: ["name", "email", "consent"],
    row: function (d) { return [d.name, d.email, d.phone, d.interests, d.message, d.page]; }
  },
  newsletter: {
    tab: "Newsletter",
    headers: ["Received", "Email", "Page"],
    required: ["email"],
    row: function (d) { return [d.email, d.page]; }
  }
};

function doPost(e) {
  try {
    var p = (e && e.parameter) || {};
    var form = FORMS[p.form];
    if (!form) return reply_(false, "Unknown form.");

    // Spam checks. Bots get a normal-looking success so they don't retry.
    if (p._gotcha) return reply_(true);
    if (!(Number(p._elapsed) >= MIN_FILL_MS)) return reply_(true);
    if (!underRateLimit_()) return reply_(false, "Too many messages right now. Please email us instead.");

    var d = {
      name: clean_(p.name, MAX_LEN.name),
      email: clean_(p.email, MAX_LEN.email).toLowerCase(),
      phone: clean_(p.phone, MAX_LEN.phone),
      subject: clean_(p.subject, MAX_LEN.subject),
      message: clean_(p.message, MAX_LEN.message),
      interests: ((e.parameters && e.parameters.interest) || []).map(function (v) { return clean_(v, 60); }).join(", "),
      consent: p.consent ? "yes" : "",
      page: clean_(p.page, MAX_LEN.page)
    };
    for (var i = 0; i < form.required.length; i++) {
      if (!d[form.required[i]]) return reply_(false, "Please fill in all the required fields.");
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(d.email)) return reply_(false, "Please enter a valid email address.");

    var sheet = sheetFor_(form);
    sheet.appendRow([new Date()].concat(form.row(d).map(safeCell_)));
    notify_(p.form, form, d);
    return reply_(true);
  } catch (err) {
    console.error(err);
    return reply_(false, "Something went wrong.");
  }
}

// A plain GET (someone opening the URL) just confirms the script is running.
function doGet() {
  return reply_(true, "Hands 4 Unity form handler is running.");
}

function sheetFor_(form) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(form.tab);
  if (!sheet) {
    sheet = ss.insertSheet(form.tab);
    sheet.appendRow(form.headers);
    sheet.setFrozenRows(1);
    sheet.getRange(1, 1, 1, form.headers.length).setFontWeight("bold");
  }
  return sheet;
}

function notify_(key, form, d) {
  var subject = key === "newsletter" ? "Newsletter sign-up: " + d.email
    : key === "involve" ? "Get involved: " + d.name
    : "Website message: " + d.subject;
  var lines = [];
  var labels = form.headers.slice(1);
  form.row(d).forEach(function (v, i) { if (v) lines.push(labels[i] + ": " + v); });
  lines.push("", "Saved in the sheet: " + SpreadsheetApp.getActiveSpreadsheet().getUrl());
  MailApp.sendEmail({ to: NOTIFY_EMAIL, replyTo: d.email, subject: subject, body: lines.join("\n") });
}

function underRateLimit_() {
  var cache = CacheService.getScriptCache();
  var n = Number(cache.get("count") || 0) + 1;
  cache.put("count", String(n), 600);
  return n <= MAX_PER_10_MIN;
}

function clean_(v, max) {
  return String(v == null ? "" : v).replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/g, "").trim().slice(0, max);
}

// Stop text like "=HYPERLINK(...)" being treated as a formula in the sheet.
function safeCell_(v) {
  return /^[=+\-@]/.test(v) ? "'" + v : v;
}

function reply_(ok, message) {
  return ContentService.createTextOutput(JSON.stringify({ ok: ok, message: message || "" }))
    .setMimeType(ContentService.MimeType.JSON);
}

// Run this once from the editor (select it, click Run) to create the tabs and grant permissions.
function setup() {
  Object.keys(FORMS).forEach(function (k) { sheetFor_(FORMS[k]); });
  var first = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];
  if (first.getName() === "Sheet1" && first.getLastRow() === 0) SpreadsheetApp.getActiveSpreadsheet().deleteSheet(first);
  MailApp.getRemainingDailyQuota();
}
