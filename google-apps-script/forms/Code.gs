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
var ADMIN_URL = "https://hands4unity.org/admin/";   // the private dashboard
var EMAIL_FORMS = ["contact", "involve", "newsletter"];   // which forms email info@
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

    // Lock so the row number we read back is the row we just added.
    var lock = LockService.getScriptLock();
    lock.waitLock(10000);
    var row;
    try {
      var sheet = sheetFor_(form);
      sheet.appendRow([new Date()].concat(form.row(d).map(safeCell_)));
      row = sheet.getLastRow();
    } finally {
      lock.releaseLock();
    }
    if (EMAIL_FORMS.indexOf(p.form) >= 0) notify_(p.form, form, d, row);
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

// Emails info@ about a new submission, with a button that opens it in the dashboard.
// Reply-To is the sender, so replying to the email answers them directly.
function notify_(key, form, d, row) {
  var who = d.name || d.email;
  var subject = key === "newsletter" ? "Newsletter sign-up: " + d.email
    : key === "involve" ? "Get involved: " + d.name
    : "Website message: " + d.subject;
  var heading = key === "newsletter" ? d.email + " joined the newsletter"
    : key === "involve" ? d.name + " wants to get involved"
    : "New message from " + d.name;
  var link = ADMIN_URL + "?open=" + encodeURIComponent(form.tab + "|" + row);
  var labels = form.headers.slice(1);
  var fields = [];
  form.row(d).forEach(function (v, i) {
    if (v && labels[i] !== "Message" && labels[i] !== "Page") fields.push([labels[i], v]);
  });

  var text = [heading, ""].concat(fields.map(function (f) { return f[0] + ": " + f[1]; }))
    .concat(d.message ? ["", d.message] : [])
    .concat(["", "Open it in the dashboard: " + link, "Reply to this email to answer " + who + " directly."]).join("\n");

  var esc = function (v) {
    return String(v).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; });
  };
  var html =
    '<div style="font-family:Arial,Helvetica,sans-serif;color:#1f1a17;max-width:560px">' +
    '<h2 style="font-size:20px;margin:0 0 16px">' + esc(heading) + '</h2>' +
    '<table style="border-collapse:collapse;font-size:14px;margin-bottom:16px">' +
    fields.map(function (f) {
      var v = f[0] === "Email" ? '<a href="mailto:' + esc(f[1]) + '" style="color:#b4500d">' + esc(f[1]) + '</a>' : esc(f[1]);
      return '<tr><td style="padding:4px 16px 4px 0;color:#6b6058;vertical-align:top">' + esc(f[0]) + '</td><td style="padding:4px 0">' + v + '</td></tr>';
    }).join("") + '</table>' +
    (d.message ? '<div style="font-size:15px;line-height:1.6;white-space:pre-wrap;background:#fbf1e6;border-radius:8px;padding:14px 16px;margin-bottom:20px">' + esc(d.message) + '</div>' : "") +
    '<a href="' + esc(link) + '" style="display:inline-block;background:#b4500d;color:#ffffff;text-decoration:none;font-weight:bold;font-size:14px;padding:10px 20px;border-radius:999px">Open in the dashboard</a>' +
    '<p style="font-size:13px;color:#6b6058;margin:20px 0 0">Reply to this email to answer ' + esc(who) + ' directly. Sent from hands4unity.org' + esc(d.page || "") + '.</p>' +
    '</div>';

  MailApp.sendEmail({ to: NOTIFY_EMAIL, replyTo: d.email, name: "Hands 4 Unity website", subject: subject, body: text, htmlBody: html });
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

// Keep values exactly as typed: stop "=HYPERLINK(...)" becoming a formula, and stop
// numbers like "087 003 0568" losing their leading zero. The ' prefix is hidden in Sheets.
function safeCell_(v) {
  return /^[=+\-@]/.test(v) || /^[\d\s()\-.]+$/.test(v) ? "'" + v : v;
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
