/* Hands 4 Unity — site behaviour. No dependencies. */
(function () {
  "use strict";

  /*
   * Forms.
   * FORM_ENDPOINT is the Google Apps Script web app in google-apps-script/forms/,
   * which saves each submission to the charity's Google Sheet and emails info@.
   * While it is empty, forms open the visitor's email app with the message filled in.
   */
  var FORM_ENDPOINT = "https://script.google.com/macros/s/AKfycbyowOgA_RzHloXGJr2atyE3U9A0sbsAvbOlQSBBWi9CWdAdhBTeGWwmGyGu_NX2Yioy0w/exec";
  var CONTACT_EMAIL = "info@hands4unity.org";

  var pageLoadedAt = Date.now();

  var header = document.querySelector(".site-header");
  var toggle = document.querySelector(".nav-toggle");

  // Mobile menu
  if (toggle) {
    toggle.addEventListener("click", function () {
      var open = document.body.classList.toggle("nav-open");
      toggle.setAttribute("aria-expanded", String(open));
    });
    document.addEventListener("keydown", function (ev) {
      if (ev.key === "Escape" && document.body.classList.contains("nav-open")) {
        document.body.classList.remove("nav-open");
        toggle.setAttribute("aria-expanded", "false");
        toggle.focus();
      }
    });
  }

  // Header shadow once the page scrolls
  if (header) {
    var onScroll = function () { header.classList.toggle("is-scrolled", window.scrollY > 8); };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  // Project filters
  var filterButtons = document.querySelectorAll("[data-filter]");
  var filterable = document.querySelector("[data-filterable]");
  if (filterButtons.length && filterable) {
    filterButtons.forEach(function (btn) {
      btn.addEventListener("click", function () {
        var kind = btn.getAttribute("data-filter");
        filterButtons.forEach(function (b) {
          var on = b === btn;
          b.classList.toggle("is-active", on);
          b.setAttribute("aria-pressed", String(on));
        });
        filterable.querySelectorAll(".card").forEach(function (card) {
          card.hidden = kind !== "all" && card.getAttribute("data-kind") !== kind;
        });
      });
    });
  }

  // Team bio dialogs
  document.querySelectorAll("[data-dialog]").forEach(function (btn) {
    var dlg = document.getElementById(btn.getAttribute("data-dialog"));
    if (!dlg || typeof dlg.showModal !== "function") return;
    btn.addEventListener("click", function () { dlg.showModal(); });
  });
  document.querySelectorAll("dialog").forEach(function (dlg) {
    dlg.addEventListener("click", function (ev) {
      if (ev.target === dlg || ev.target.closest(".dialog-close, .lightbox-close")) dlg.close();
    });
  });

  // Gallery lightbox
  var lightbox = document.querySelector(".lightbox");
  var gallery = document.querySelector("[data-gallery]");
  if (lightbox && gallery && typeof lightbox.showModal === "function") {
    var items = Array.prototype.slice.call(gallery.querySelectorAll(".gallery-item"));
    var lbImg = lightbox.querySelector("img");
    var prev = lightbox.querySelector(".lightbox-prev");
    var next = lightbox.querySelector(".lightbox-next");
    var index = 0;
    var show = function (i) {
      index = (i + items.length) % items.length;
      lbImg.src = items[index].getAttribute("data-full");
      lbImg.alt = "Photo " + (index + 1) + " of " + items.length;
    };
    prev.hidden = next.hidden = items.length < 2;
    items.forEach(function (item, i) {
      item.addEventListener("click", function () { show(i); lightbox.showModal(); });
    });
    prev.addEventListener("click", function () { show(index - 1); });
    next.addEventListener("click", function () { show(index + 1); });
    lightbox.addEventListener("keydown", function (ev) {
      if (ev.key === "ArrowLeft") show(index - 1);
      if (ev.key === "ArrowRight") show(index + 1);
    });
  }

  // Pre-fill the contact subject from ?subject=
  var subjectField = document.getElementById("c-subject");
  if (subjectField) {
    try {
      var subj = new URLSearchParams(window.location.search).get("subject");
      if (subj) subjectField.value = subj;
    } catch (e) { /* older browsers: ignore */ }
  }

  // Forms
  var EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  function validate(form) {
    var ok = true;
    form.querySelectorAll("[required]").forEach(function (el) {
      var bad = el.type === "checkbox" ? !el.checked : !el.value.trim();
      if (!bad && el.type === "email") bad = !EMAIL_RE.test(el.value.trim());
      el.classList.toggle("is-invalid", bad);
      el.setAttribute("aria-invalid", String(bad));
      if (bad && ok) { el.focus(); ok = false; }
    });
    return ok;
  }

  function summarise(form) {
    var data = new FormData(form);
    var lines = [];
    var interests = data.getAll("interest");
    var labels = { name: "Name", email: "Email", phone: "Phone", message: "Message" };
    Object.keys(labels).forEach(function (k) {
      var v = (data.get(k) || "").toString().trim();
      if (v) lines.push(labels[k] + ": " + v);
    });
    if (interests.length) lines.push("Interested in: " + interests.join(", "));
    return { subject: (data.get("subject") || "Website enquiry").toString(), body: lines.join("\n") };
  }

  document.querySelectorAll("form[data-form]").forEach(function (form) {
    var status = form.querySelector(".form-status");
    var setStatus = function (msg, kind) {
      status.textContent = msg;
      status.className = "form-status" + (kind ? " is-" + kind : "");
    };
    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      setStatus("");
      if (form.querySelector('[name="_gotcha"]').value) return;
      if (!validate(form)) {
        setStatus("Please fill in the highlighted fields.", "error");
        return;
      }
      var msg = summarise(form);

      if (!FORM_ENDPOINT) {
        window.location.href = "mailto:" + CONTACT_EMAIL +
          "?subject=" + encodeURIComponent(msg.subject) +
          "&body=" + encodeURIComponent(msg.body);
        setStatus("Your email app should open with your message ready to send. If it doesn't, email us at " + CONTACT_EMAIL + ".", "success");
        return;
      }

      var button = form.querySelector('button[type="submit"]');
      button.disabled = true;
      setStatus("Sending…");
      // URL-encoded body keeps this a "simple" CORS request, which Apps Script accepts.
      var data = new URLSearchParams(new FormData(form));
      data.set("form", form.getAttribute("data-form"));
      data.set("page", window.location.pathname);
      data.set("_elapsed", String(Date.now() - pageLoadedAt));
      fetch(FORM_ENDPOINT, { method: "POST", body: data })
        .then(function (res) { return res.json(); })
        .then(function (res) {
          if (!res.ok) throw new Error(res.message);
          form.reset();
          setStatus(form.getAttribute("data-form") === "newsletter"
            ? "Thank you. You're on the list."
            : "Thank you. Your message has been sent and we'll be in touch soon.", "success");
        })
        .catch(function () {
          setStatus("Sorry, something went wrong. Please email us at " + CONTACT_EMAIL + ".", "error");
        })
        .then(function () { button.disabled = false; });
    });
    form.addEventListener("input", function (ev) {
      if (ev.target.classList.contains("is-invalid")) {
        ev.target.classList.remove("is-invalid");
        ev.target.removeAttribute("aria-invalid");
      }
    });
  });
})();
