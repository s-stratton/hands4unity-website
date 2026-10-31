/**
 * Hands 4 Unity — admin dashboard.
 *
 * A private web page showing website visits (from Cloudflare Web Analytics) alongside
 * form messages and newsletter sign-ups (from the "Hands 4 Unity website" Google Sheet).
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
var RECENT_LIMIT = 10;

function doGet() {
  return HtmlService.createHtmlOutputFromFile("Dashboard")
    .setTitle("Hands 4 Unity dashboard")
    .addMetaTag("viewport", "width=device-width, initial-scale=1")
    .setFaviconUrl("https://hands4unity.org/assets/favicon.png");
}

// Called from the page with google.script.run. Everything returned must be plain JSON.
function getDashboard(days) {
  days = RANGES.indexOf(Number(days)) >= 0 ? Number(days) : 30;
  var props = PropertiesService.getScriptProperties().getProperties();
  var result = { days: days, generated: new Date().toISOString(), user: Session.getActiveUser().getEmail() };

  try {
    result.visits = getVisits_(props, days);
  } catch (err) {
    console.error(err);
    result.visitsError = String(err.message || err);
  }
  try {
    result.forms = getForms_(props, days);
  } catch (err) {
    console.error(err);
    result.formsError = String(err.message || err);
  }
  return result;
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

/* ---------- Form submissions from the Sheet ---------- */

function getForms_(props, days) {
  if (!props.SHEET_ID) throw new Error("Missing script property SHEET_ID");
  var ss = SpreadsheetApp.openById(props.SHEET_ID);
  var since = Date.now() - days * 86400000;
  var read = function (tab) {
    var sheet = ss.getSheetByName(tab);
    if (!sheet || sheet.getLastRow() < 2) return { headers: [], rows: [] };
    var values = sheet.getDataRange().getValues();
    var headers = values.shift().map(String);
    var rows = values.filter(function (r) { return r[0] instanceof Date; }).map(function (r) {
      var o = {};
      headers.forEach(function (h, i) { o[h] = r[i] instanceof Date ? r[i].toISOString() : String(r[i]); });
      return o;
    });
    rows.sort(function (x, y) { return x.Received < y.Received ? 1 : -1; });
    return { headers: headers, rows: rows };
  };
  var summary = function (tab) {
    var t = read(tab);
    return {
      total: t.rows.length,
      inRange: t.rows.filter(function (r) { return Date.parse(r.Received) >= since; }).length,
      recent: t.rows.slice(0, RECENT_LIMIT)
    };
  };
  var newsletter = read("Newsletter");
  return {
    sheetUrl: ss.getUrl(),
    messages: summary("Messages"),
    involve: summary("Get Involved"),
    newsletter: {
      total: newsletter.rows.length,
      inRange: newsletter.rows.filter(function (r) { return Date.parse(r.Received) >= since; }).length,
      recent: newsletter.rows.slice(0, RECENT_LIMIT),
      all: newsletter.rows.map(function (r) { return { Received: r.Received, Email: r.Email }; })
    }
  };
}

// Run once from the editor to grant permissions and check the settings work.
function setup() {
  var data = getDashboard(7);
  console.log(data.visitsError || ("Visits OK: " + data.visits.visits + " in the last 7 days"));
  console.log(data.formsError || ("Sheet OK: " + data.forms.messages.total + " messages"));
}
