// Fertility & IVF Suite - desk UI enhancements
//
// Purely additive: never touches Frappe's own rendering, routing, or state.
// Theme switching and sidebar collapse/expand are Frappe's own, real
// features (User Settings > Theme, sidebar toggle button) - this file does
// not reimplement them, it only makes sure our workspace Number Cards get
// the animated count-up treatment from design-system.md §12, matching the
// demo's KPI cards.

(function () {
	"use strict";

	var ANIMATED_FLAG = "fertilityCounterDone";

	// Shared counter animation: reused by both the workspace Number Card
	// scanner below and the Fertility Command Center KPI cards
	// (fertility_dashboard.js), so the count-up behaviour stays identical
	// everywhere in the app.
	function animateCounter(el, target, opts) {
		opts = opts || {};
		var prefix = opts.prefix || "";
		var suffix = opts.suffix || "";
		var isDecimal = !!opts.decimal;
		var steps = 30;
		var step = Math.max(Math.abs(target) / steps, isDecimal ? 0.1 : 1);
		var current = 0;
		var direction = target < 0 ? -1 : 1;

		var timer = setInterval(function () {
			current += step;
			if (current >= Math.abs(target)) {
				current = Math.abs(target);
				clearInterval(timer);
			}
			var value = direction * current;
			el.textContent = prefix + (isDecimal ? value.toFixed(1) : Math.round(value).toLocaleString()) + suffix;
		}, 16);
	}

	function animateNumber(el) {
		if (el.dataset[ANIMATED_FLAG]) return;

		var raw = (el.textContent || "").trim();
		var match = raw.match(/-?[\d,]+\.?\d*/);
		if (!match) return;

		var target = parseFloat(match[0].replace(/,/g, ""));
		if (isNaN(target)) return;

		el.dataset[ANIMATED_FLAG] = "1";

		animateCounter(el, target, {
			prefix: raw.slice(0, match.index),
			suffix: raw.slice(match.index + match[0].length),
			decimal: match[0].indexOf(".") !== -1,
		});
	}

	frappe.provide("fertility_suite");
	fertility_suite.animate_counter = animateCounter;

	function scanForNumberCards(root) {
		try {
			(root || document)
				.querySelectorAll(".number-widget-box .widget-content .number")
				.forEach(animateNumber);
		} catch (e) {
			// Never let a UI enhancement break the desk.
		}
	}

	function init() {
		scanForNumberCards(document);

		if (typeof MutationObserver === "undefined") return;

		var observer = new MutationObserver(function (mutations) {
			mutations.forEach(function (mutation) {
				mutation.addedNodes.forEach(function (node) {
					if (node.nodeType !== 1) return;
					if (node.matches && node.matches(".number-widget-box")) {
						scanForNumberCards(node.parentNode || document);
					} else if (node.querySelectorAll) {
						scanForNumberCards(node);
					}
				});
			});
		});

		observer.observe(document.body, { childList: true, subtree: true });
	}

	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", init);
	} else {
		init();
	}
})();
