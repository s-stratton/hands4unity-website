/**
 * Hands 4 Unity — admin dashboard.
 *
 * A private web page with an inbox of website form submissions (from the
 * "Hands 4 Unity website" Google Sheet) and website visits (from Cloudflare Web Analytics).
 * The page polls getInbox() every 30 seconds; read/unread/archived is stored in a "Status"
 * column in each tab of the Sheet, so everyone sees the same state.
 *
 * A standalone Apps Script project in the info@hands4unity.org account, separate from the
 * forms script so that its access can be limited to hands4unity.org accounts.
 * Files: Code.gs (this file) and Dashboard.html.
 *
 * Settings live in Project Settings → Script properties, never in this file
 * (it is published in the public website repository):
 *   CF_API_TOKEN   read-only Cloudflare token (Account Analytics: Read)
 *   CF_ACCOUNT_ID  Cloudflare account ID
 *   CF_SITE_TAG    Web Analytics site tag for hands4unity.org
 *   SHEET_ID       ID of the "Hands 4 Unity website" Google Sheet (from its URL)
 */

var RANGES = [7, 30, 90];   // Cloudflare allows up to about 13 weeks per query
var CACHE_SECONDS = 600;
var INBOX_LIMIT = 500;
var STATUSES = ["unread", "read", "archived"];
var TABS = [
  { tab: "Messages", type: "message" },
  { tab: "Get Involved", type: "involve" },
  { tab: "Newsletter", type: "newsletter" }
];

function doGet() {
  return HtmlService.createHtmlOutputFromFile("Dashboard")
    .setTitle("Hands 4 Unity dashboard")
    .addMetaTag("viewport", "width=device-width, initial-scale=1")
    .setFaviconUrl("https://hands4unity.org/assets/favicon.png");
}

// The functions below are called from the page with google.script.run.
// Everything they return must be plain JSON (no Date objects).

function getVisits(days) {
  days = RANGES.indexOf(Number(days)) >= 0 ? Number(days) : 30;
  var out = getVisits_(PropertiesService.getScriptProperties().getProperties(), days);
  out.days = days;
  out.generated = new Date().toISOString();
  return out;
}

/* ---------- Cloudflare Web Analytics ---------- */

function getVisits_(props, days) {
  ["CF_API_TOKEN", "CF_ACCOUNT_ID", "CF_SITE_TAG"].forEach(function (k) {
    if (!props[k]) throw new Error("Missing script property " + k);
  });
  var cache = CacheService.getScriptCache();
  var key = "visits-" + days;
  var hit = cache.get(key);
  if (hit) return JSON.parse(hit);

  // Cloudflare returns exact figures only for short ranges; longer ranges come back as rough
  // samples, which are useless for a small site. So fetch 7-day chunks and add them up here.
  var end = new Date();
  var start = new Date(end.getTime() - (days - 1) * 86400000);
  var query = "query($a: String!, $f: AccountRumPageloadEventsAdaptiveGroupsFilter_InputObject) {" +
    " viewer { accounts(filter: { accountTag: $a }) {" +
    " rows: rumPageloadEventsAdaptiveGroups(limit: 5000, filter: $f) {" +
    " count sum { visits } dimensions { date requestPath refererHost countryName deviceType } } } } }";
  var requests = [];
  for (var from = start; from <= end; from = new Date(from.getTime() + 7 * 86400000)) {
    var to = new Date(Math.min(from.getTime() + 6 * 86400000, end.getTime()));
    requests.push({
      url: "https://api.cloudflare.com/client/v4/graphql",
      method: "post",
      contentType: "application/json",
      headers: { Authorization: "Bearer " + props.CF_API_TOKEN },
      payload: JSON.stringify({ query: query, variables: {
        a: props.CF_ACCOUNT_ID,
        f: { siteTag: props.CF_SITE_TAG, date_geq: isoDate_(from), date_leq: isoDate_(to) }
      } }),
      muteHttpExceptions: true
    });
  }
  var rows = [];
  UrlFetchApp.fetchAll(requests).forEach(function (res) {
    var body = JSON.parse(res.getContentText());
    if (body.errors && body.errors.length) throw new Error("Cloudflare: " + body.errors[0].message);
    rows = rows.concat(body.data.viewer.accounts[0].rows);
  });

  var out = { visits: 0, views: 0, daily: [] };
  var byDate = {}, pages = {}, sources = {}, countries = {}, devices = {};
  var add = function (map, key, n) { if (n) map[key] = (map[key] || 0) + n; };
  rows.forEach(function (r) {
    var d = r.dimensions, views = r.count, visits = r.sum.visits;
    out.views += views;
    out.visits += visits;
    byDate[d.date] = byDate[d.date] || { visits: 0, views: 0 };
    byDate[d.date].visits += visits;
    byDate[d.date].views += views;
    add(pages, d.requestPath, views);
    add(sources, d.refererHost, visits);   // clicks within the site have 0 visits, so drop out
    add(countries, d.countryName, visits);
    add(devices, d.deviceType, visits);
  });
  for (var i = 0; i < days; i++) {
    var day = isoDate_(new Date(start.getTime() + i * 86400000));
    out.daily.push({ date: day, visits: (byDate[day] || {}).visits || 0, views: (byDate[day] || {}).views || 0 });
  }
  var top = function (map, n) {
    return Object.keys(map).map(function (k) { return { label: k, value: map[k] }; })
      .sort(function (x, y) { return y.value - x.value; }).slice(0, n);
  };
  out.pages = top(pages, 10);
  out.sources = top(sources, 10);
  out.countries = top(countries, 10);
  out.devices = top(devices, 5);
  cache.put(key, JSON.stringify(out), CACHE_SECONDS);
  return out;
}

function isoDate_(d) {
  return Utilities.formatDate(d, "UTC", "yyyy-MM-dd");
}

/* ---------- Inbox: form submissions from the Sheet ---------- */

function getInbox() {
  var ss = spreadsheet_();
  var items = [], subscribers = [];
  TABS.forEach(function (t) {
    var sheet = ss.getSheetByName(t.tab);
    if (!sheet || sheet.getLastRow() < 2) return;
    var col = statusColumn_(sheet);
    var values = sheet.getRange(1, 1, sheet.getLastRow(), Math.max(sheet.getLastColumn(), col)).getValues();
    var headers = values[0].map(String);
    for (var i = 1; i < values.length; i++) {
      var r = values[i];
      if (!(r[0] instanceof Date)) continue;
      var o = {};
      headers.forEach(function (h, j) { o[h] = r[j]; });
      var status = String(r[col - 1]);
      items.push({
        id: t.tab + "|" + (i + 1) + "|" + r[0].getTime(),
        type: t.type,
        received: r[0].toISOString(),
        name: str_(o.Name),
        email: str_(o.Email),
        phone: str_(o.Phone),
        subject: str_(o.Subject),
        message: str_(o.Message),
        interests: str_(o["Interested in"]),
        page: str_(o.Page),
        status: STATUSES.indexOf(status) >= 0 ? status : "unread"
      });
      if (t.type === "newsletter") subscribers.push({ email: str_(o.Email), received: r[0].toISOString() });
    }
  });
  var newest = function (x, y) { return x.received < y.received ? 1 : -1; };
  items.sort(newest);
  subscribers.sort(newest);
  return {
    user: Session.getActiveUser().getEmail(),
    sheetUrl: ss.getUrl(),
    generated: new Date().toISOString(),
    items: items.slice(0, INBOX_LIMIT),
    subscribers: subscribers
  };
}

// ids come from getInbox: "Tab|row|receivedMillis". Rows can move if someone edits the
// Sheet, so each id is checked against its timestamp and looked up again if it has moved.
function setStatus(ids, status) {
  if (STATUSES.indexOf(status) < 0) throw new Error("Unknown status " + status);
  var lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    var ss = spreadsheet_();
    var byTab = {};
    (ids || []).forEach(function (id) {
      var p = String(id).split("|");
      (byTab[p[0]] = byTab[p[0]] || []).push({ row: Number(p[1]), ms: Number(p[2]) });
    });
    Object.keys(byTab).forEach(function (tab) {
      if (!TABS.some(function (t) { return t.tab === tab; })) return;
      var sheet = ss.getSheetByName(tab);
      if (!sheet || sheet.getLastRow() < 2) return;
      var col = statusColumn_(sheet);
      var n = sheet.getLastRow();
      var times = sheet.getRange(1, 1, n, 1).getValues().map(function (r) { return r[0] instanceof Date ? r[0].getTime() : null; });
      var statusRange = sheet.getRange(1, col, n, 1);
      var statuses = statusRange.getValues();
      byTab[tab].forEach(function (ref) {
        var row = times[ref.row - 1] === ref.ms ? ref.row : times.indexOf(ref.ms) + 1;
        if (row > 1) statuses[row - 1][0] = status;
      });
      statusRange.setValues(statuses);
    });
  } finally {
    lock.releaseLock();
  }
  return true;
}

function spreadsheet_() {
  var id = PropertiesService.getScriptProperties().getProperty("SHEET_ID");
  if (!id) throw new Error("Missing script property SHEET_ID");
  return SpreadsheetApp.openById(id);
}

// The forms script writes the submission columns; this adds a "Status" column after them.
// An empty Status means unread.
function statusColumn_(sheet) {
  var lastCol = Math.max(sheet.getLastColumn(), 1);
  var headers = sheet.getRange(1, 1, 1, lastCol).getValues()[0].map(String);
  var i = headers.indexOf("Status");
  if (i >= 0) return i + 1;
  sheet.getRange(1, lastCol + 1).setValue("Status").setFontWeight("bold");
  return lastCol + 1;
}

function str_(v) {
  return v instanceof Date ? v.toISOString() : String(v == null ? "" : v);
}

// Run once from the editor to grant permissions and check the settings work.
function setup() {
  var inbox = getInbox();
  console.log("Sheet OK: " + inbox.items.length + " items, " + inbox.subscribers.length + " newsletter sign-ups");
  try {
    console.log("Visits OK: " + getVisits(7).visits + " in the last 7 days");
  } catch (err) {
    console.log("Visits failed: " + err.message);
  }
}
