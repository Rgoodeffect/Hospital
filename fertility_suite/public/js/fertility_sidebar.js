// Fertility & IVF Suite - permanent left sidebar navigation.
//
// Frappe's own workspace sidebar only shows the current workspace's own
// shortcuts and changes shape per page. The demo prototype instead has one
// fixed, always-visible nav rail. We inject that rail once, directly under
// <body> (a sibling of Frappe's router-managed #body), so client-side route
// changes never touch or remove it - only the injected .active class moves.

(function () {
	"use strict";

	var ICONS = "/assets/frappe/icons/lucide/icons.svg";

	var NAV_ITEMS = [
		{ label: "Dashboard", route: "/app/fertility-command-center", icon: "layout-dashboard" },
		{ label: "Patients", route: "/app/patient", icon: "users" },
		{ label: "Appointments", route: "/app/patient-appointment", icon: "calendar-check" },
		{ label: "Fertility Cases", route: "/app/fertility-case", icon: "clipboard-list" },
		{ label: "Treatment Plans", route: "/app/treatment-plan", icon: "clipboard-pen" },
		{ label: "IVF Cycles", route: "/app/ivf-cycle", icon: "activity" },
		{ label: "Monitoring", route: "/app/monitoring-visit", icon: "stethoscope" },
		{ label: "Egg Retrieval", route: "/app/egg-retrieval", icon: "syringe" },
		{ label: "Embryology", route: "/app/embryology-record", icon: "microscope" },
		{ label: "Embryo Bank", route: "/app/gamete-donor", icon: "snowflake" },
		{ label: "Transfers", route: "/app/embryo-transfer", icon: "test-tube" },
		{ label: "Pregnancy Follow-up", route: "/app/pregnancy-follow-up", icon: "baby" },
		{ label: "Insurance", route: "/app/insurance-claim", icon: "shield-check" },
		{ label: "Billing", route: "/app/sales-invoice", icon: "credit-card" },
		{ label: "Reports", route: "/app/executive", icon: "trending-up" },
		{ label: "Administration", route: "/app/user", icon: "shield-user" },
	];

	function icon_svg(name) {
		return (
			'<svg class="fs-sidebar-icon" aria-hidden="true">' +
			'<use href="' + ICONS + "#icon-" + name + '"></use>' +
			"</svg>"
		);
	}

	function build_sidebar() {
		var wrap = document.createElement("div");
		wrap.id = "fertility-sidebar";
		wrap.innerHTML =
			'<div class="fs-sidebar-brand">' +
			'<span class="fs-sidebar-brand-mark">FS</span>' +
			'<span class="fs-sidebar-brand-text">Fertility Suite</span>' +
			"</div>" +
			'<nav class="fs-sidebar-nav">' +
			NAV_ITEMS.map(function (item, i) {
				return (
					'<a class="fs-sidebar-link" data-route="' + item.route + '" href="' + item.route + '">' +
					icon_svg(item.icon) +
					'<span class="fs-sidebar-label">' + item.label + "</span>" +
					"</a>"
				);
			}).join("") +
			"</nav>" +
			'<button type="button" class="fs-sidebar-toggle" title="Collapse sidebar">' +
			icon_svg("chevrons-left") +
			"</button>";

		document.body.insertBefore(wrap, document.body.firstChild);
		document.body.classList.add("fs-sidebar-active");

		wrap.querySelector(".fs-sidebar-toggle").addEventListener("click", function () {
			document.body.classList.toggle("fs-sidebar-collapsed");
			try {
				localStorage.setItem(
					"fertility_sidebar_collapsed",
					document.body.classList.contains("fs-sidebar-collapsed") ? "1" : "0"
				);
			} catch (e) {}
		});

		if (window.innerWidth <= 900) {
			document.body.classList.add("fs-sidebar-collapsed");
		} else {
			try {
				if (localStorage.getItem("fertility_sidebar_collapsed") === "1") {
					document.body.classList.add("fs-sidebar-collapsed");
				}
			} catch (e) {}
		}

		return wrap;
	}

	function normalize_path(path) {
		// frappe.get_route() returns factory tokens (["List", "Patient",
		// "List"], ["Form", "Patient", "PAT-0001"], ...), not the URL slug,
		// and Frappe canonicalizes /app/* to /desk/* - so comparing against
		// data-route via the actual browser path (with either prefix
		// stripped) is the one representation that's accurate for every
		// view type (list, form, report, our own page).
		return path.replace(/^\/(app|desk)(?=\/|$)/, "");
	}

	function highlight_active(wrap) {
		var current = normalize_path(window.location.pathname);
		var links = wrap.querySelectorAll(".fs-sidebar-link");
		var best = null;
		links.forEach(function (link) {
			link.classList.remove("fs-active");
			var link_route = link.getAttribute("data-route");
			var link_path = normalize_path(link_route);
			if (current.indexOf(link_path) === 0 && (!best || link_path.length > best.length)) {
				best = link_route;
			}
		});
		if (best) {
			wrap.querySelector('.fs-sidebar-link[data-route="' + best + '"]').classList.add("fs-active");
		}
	}

	function init() {
		// app_include_js runs synchronously during initial HTML parse - well
		// before frappe.ready exists (that's only wired up once frappe's own
		// desk bundle reaches its internal $(document).ready). frappe.boot
		// and frappe.router, however, are set up earlier during that same
		// synchronous bundle execution, so we just wait for DOMContentLoaded
		// (same safe pattern fertility_ui.js already uses) and poll briefly
		// for frappe.session/frappe.router to exist.
		if (!window.frappe || !frappe.session || frappe.session.user === "Guest") return;
		if (!frappe.router) return;
		if (document.getElementById("fertility-sidebar")) return;

		var wrap = build_sidebar();
		highlight_active(wrap);
		frappe.router.on("change", function () {
			highlight_active(wrap);
		});
	}

	function safe_init(retries) {
		try {
			if (!window.frappe || !frappe.router) {
				if (retries > 0) {
					setTimeout(function () {
						safe_init(retries - 1);
					}, 200);
				}
				return;
			}
			init();
		} catch (e) {
			// A sidebar bug must never take down the desk.
			console.error("fertility_sidebar init failed", e);
		}
	}

	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", function () {
			safe_init(15);
		});
	} else {
		safe_init(15);
	}
})();
