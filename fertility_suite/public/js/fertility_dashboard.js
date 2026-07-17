// Fertility & IVF Suite - Fertility Command Center dashboard.
//
// Renders the fully custom KPI + Chart.js dashboard used by the
// "fertility-command-center" Page. Deliberately does not use Frappe's
// Number Card / Dashboard Chart widgets - the demo prototype's dashboard is
// reproduced directly with our own markup, our own theme classes, and the
// real Chart.js library (vendored locally, loaded on-demand for this page
// only via frappe.require so it never weighs down the rest of the desk).

frappe.provide("fertility_suite");

(function () {
	"use strict";

	var CHART_JS_URL = "/assets/fertility_suite/js/vendor/chart.umd.min.js";

	var PALETTE = {
		brand: "#7c5cff",
		blue: "#2f9bff",
		teal: "#00b8a9",
		amber: "#ffa62b",
		rose: "#ff5c8a",
		green: "#12b76a",
		red: "#f04438",
		gray: "#9096a8",
	};

	var KPI_DEFS = [
		{ key: "total_patients", label: "Total Patients", icon: "users", color: "blue", type: "int" },
		{ key: "todays_appointments", label: "Today's Appointments", icon: "calendar-check", color: "brand", type: "int" },
		{ key: "active_ivf_cycles", label: "Active IVF Cycles", icon: "activity", color: "teal", type: "int" },
		{ key: "pregnancy_rate", label: "Pregnancy Rate", icon: "heart-pulse", color: "rose", type: "percent" },
		{ key: "embryos_stored", label: "Embryos Stored", icon: "snowflake", color: "amber", type: "int" },
		{ key: "revenue", label: "Revenue (90d)", icon: "dollar-sign", color: "green", type: "currency" },
	];

	function currency_prefix() {
		// frappe.format() renders Currency fields as an HTML string (a
		// right-aligned <div> with the symbol) meant for .innerHTML, not
		// .textContent - using it here would print raw markup. We only need
		// the plain symbol, so derive it straight from Intl instead.
		try {
			var code = (frappe.boot && frappe.boot.sysdefaults && frappe.boot.sysdefaults.currency) || "USD";
			var parts = new Intl.NumberFormat(frappe.boot.lang || "en", { style: "currency", currency: code }).formatToParts(0);
			var symbol = parts.filter(function (p) { return p.type === "currency"; }).map(function (p) { return p.value; }).join("");
			return symbol ? symbol + " " : "";
		} catch (e) {
			return "";
		}
	}

	function icon_svg(name) {
		return (
			'<svg class="fs-kpi-icon" aria-hidden="true">' +
			'<use href="/assets/frappe/icons/lucide/icons.svg#icon-' + name + '"></use>' +
			"</svg>"
		);
	}

	fertility_suite.CommandCenterDashboard = class CommandCenterDashboard {
		constructor(wrapper) {
			this.wrapper = wrapper;
			this.$body = $(wrapper).find(".layout-main-section");
			this.render_skeleton();
			this.load_kpis();
			this.load_charts();
		}

		render_skeleton() {
			var kpi_cards = KPI_DEFS.map(function (def) {
				return (
					'<div class="fs-kpi-card fs-color-' + def.color + '" data-kpi="' + def.key + '">' +
					'<div class="fs-kpi-icon-wrap">' + icon_svg(def.icon) + "</div>" +
					'<div class="fs-kpi-body">' +
					'<div class="fs-kpi-value" data-value="0">-</div>' +
					'<div class="fs-kpi-label">' + def.label + "</div>" +
					"</div>" +
					"</div>"
				);
			}).join("");

			this.$body.html(
				'<div class="fertility-command-center">' +
				'<div class="fs-dashboard-hero">' +
				"<h2>" + __("Fertility Command Center") + "</h2>" +
				'<p class="text-muted">' + __("Clinic-wide overview - patients, cycles, embryology and revenue at a glance") + "</p>" +
				"</div>" +
				'<div class="fs-kpi-grid">' + kpi_cards + "</div>" +
				'<div class="fs-chart-grid">' +
				this.chart_card("revenue_trend", __("Revenue Trend")) +
				this.chart_card("ivf_success_rate", __("IVF Outcome Distribution")) +
				this.chart_card("embryo_inventory", __("Embryo Inventory")) +
				this.chart_card("claims_status", __("Claims Status")) +
				"</div>" +
				"</div>"
			);
		}

		chart_card(key, title) {
			return (
				'<div class="fs-chart-card">' +
				'<div class="fs-chart-card-title">' + title + "</div>" +
				'<div class="fs-chart-canvas-wrap"><canvas data-chart="' + key + '"></canvas></div>' +
				"</div>"
			);
		}

		load_kpis() {
			var me = this;
			frappe.call({
				method: "fertility_suite.api.get_command_center_kpis",
				callback: function (r) {
					if (!r.message) return;
					KPI_DEFS.forEach(function (def) {
						var raw = r.message[def.key] || 0;
						var el = me.$body.find('.fs-kpi-card[data-kpi="' + def.key + '"] .fs-kpi-value')[0];
						if (!el) return;

						if (def.type === "currency") {
							fertility_suite.animate_counter(el, raw, { prefix: currency_prefix() });
						} else if (def.type === "percent") {
							fertility_suite.animate_counter(el, raw, { decimal: true, suffix: "%" });
						} else {
							fertility_suite.animate_counter(el, raw);
						}
					});
				},
			});
		}

		load_charts() {
			var me = this;
			frappe.require(CHART_JS_URL).then(function () {
				frappe.call({
					method: "fertility_suite.api.get_command_center_charts",
					callback: function (r) {
						if (!r.message) return;
						me.render_charts(r.message);
					},
				});
			});
		}

		render_charts(data) {
			this.draw_line("revenue_trend", data.revenue_trend, PALETTE.brand);
			this.draw_doughnut("ivf_success_rate", data.ivf_success_rate, [
				PALETTE.gray, PALETTE.amber, PALETTE.blue, PALETTE.teal, PALETTE.green, PALETTE.red,
			]);
			this.draw_bar("embryo_inventory", data.embryo_inventory, PALETTE.teal);
			this.draw_doughnut("claims_status", data.claims_status, [
				PALETTE.gray, PALETTE.amber, PALETTE.blue, PALETTE.green, PALETTE.red,
			]);
		}

		canvas(key) {
			var el = this.$body.find('canvas[data-chart="' + key + '"]')[0];
			return el ? el.getContext("2d") : null;
		}

		draw_line(key, series, color) {
			var ctx = this.canvas(key);
			if (!ctx || !series) return;
			new Chart(ctx, {
				type: "line",
				data: {
					labels: series.labels,
					datasets: [{
						data: series.values,
						borderColor: color,
						backgroundColor: color + "33",
						fill: true,
						tension: 0.35,
						pointRadius: 3,
					}],
				},
				options: base_options(false),
			});
		}

		draw_bar(key, series, color) {
			var ctx = this.canvas(key);
			if (!ctx || !series) return;
			new Chart(ctx, {
				type: "bar",
				data: {
					labels: series.labels,
					datasets: [{ data: series.values, backgroundColor: color, borderRadius: 6 }],
				},
				options: base_options(false),
			});
		}

		draw_doughnut(key, series, colors) {
			var ctx = this.canvas(key);
			if (!ctx || !series) return;
			new Chart(ctx, {
				type: "doughnut",
				data: {
					labels: series.labels,
					datasets: [{ data: series.values, backgroundColor: colors, borderWidth: 0 }],
				},
				options: base_options(true),
			});
		}
	};

	function base_options(is_donut) {
		return {
			responsive: true,
			maintainAspectRatio: false,
			plugins: {
				legend: { display: is_donut, position: "bottom", labels: { boxWidth: 10, padding: 12 } },
			},
			scales: is_donut ? {} : {
				y: { beginAtZero: true, grid: { color: "rgba(120,120,140,0.08)" } },
				x: { grid: { display: false } },
			},
		};
	}
})();
