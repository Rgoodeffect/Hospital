import frappe
from frappe.model.document import Document


class InsuranceClaim(Document):
	def validate(self):
		calculate_claim(self)


def calculate_claim(doc, method=None):
	"""Compute insurance_amount / co_payment_amount / patient_payable_amount
	from total_amount based on the Insurance Plan's billing type.

	- Cash: patient pays the full amount.
	- Insurance: insurer covers coverage_percent of the total (capped at the
	  plan's max_coverage_amount, if set); patient pays the remainder.
	- Co-Payment: patient pays a fixed co_payment_percent of the total; the
	  insurer covers the rest.
	- Mixed Billing: insurer covers coverage_percent of the total, and the
	  patient co-pays co_payment_percent of what's left after that coverage.
	"""
	total = doc.total_amount or 0
	coverage_percent = doc.coverage_percent or 0
	co_payment_percent = doc.co_payment_percent or 0

	insurance_amount = 0
	co_payment_amount = 0

	if doc.billing_type == "Cash":
		pass

	elif doc.billing_type == "Insurance":
		insurance_amount = total * coverage_percent / 100
		insurance_amount = _cap_to_plan_max(doc, insurance_amount)

	elif doc.billing_type == "Co-Payment":
		co_payment_amount = total * co_payment_percent / 100
		insurance_amount = total - co_payment_amount

	elif doc.billing_type == "Mixed Billing":
		insurance_amount = _cap_to_plan_max(doc, total * coverage_percent / 100)
		remainder = total - insurance_amount
		co_payment_amount = remainder * co_payment_percent / 100

	doc.insurance_amount = round(insurance_amount, 2)
	doc.co_payment_amount = round(co_payment_amount, 2)
	doc.patient_payable_amount = round(total - doc.insurance_amount, 2)


def _cap_to_plan_max(doc, insurance_amount):
	if not doc.insurance_plan:
		return insurance_amount

	max_coverage = frappe.db.get_value("Insurance Plan", doc.insurance_plan, "max_coverage_amount")
	if max_coverage:
		return min(insurance_amount, max_coverage)
	return insurance_amount


@frappe.whitelist()
def approve_claim(claim_name: str, approved_amount: float | None = None):
	doc = frappe.get_doc("Insurance Claim", claim_name)

	if approved_amount is not None and approved_amount < doc.insurance_amount:
		doc.insurance_amount = approved_amount
		doc.patient_payable_amount = doc.total_amount - approved_amount
		doc.status = "Partially Approved"
	else:
		doc.status = "Approved"

	doc.save()

	from fertility_suite.notification_engine.notification_engine import notify

	notify(
		"Claim Approved",
		{
			"claim_name": doc.name,
			"approved_amount": doc.insurance_amount,
			"reference_doctype": "Insurance Claim",
			"reference_name": doc.name,
		},
		roles=["Fertility Patient"],
	)
	return doc.name
