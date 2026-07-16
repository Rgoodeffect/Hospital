import frappe
from frappe import _
from frappe.model.document import Document

OCCUPYING_STATUSES = ("Available", "Reserved", "Allocated")


class DonorBankUnit(Document):
	def validate(self):
		validate_eligibility(self)
		validate_unit(self)

	def on_update(self):
		recompute_storage_usage(self)


def validate_eligibility(doc, method=None):
	"""A unit can only be made Available once its donor is Active, has passed
	screening, and has a current consent on file."""
	if doc.status != "Available":
		return

	donor = frappe.db.get_value(
		"Gamete Donor", doc.donor, ["status", "screening_status", "consent_on_file"], as_dict=True
	)
	if not donor:
		return

	if donor.status != "Active":
		frappe.throw(_("Donor {0} is not Active (current status: {1})").format(doc.donor, donor.status))
	if donor.screening_status != "Passed":
		frappe.throw(_("Donor {0} has not passed screening (current status: {1})").format(
			doc.donor, donor.screening_status
		))
	if not donor.consent_on_file:
		frappe.throw(_("Donor {0} has no active consent on file").format(doc.donor))


def validate_unit(doc, method=None):
	"""Prevent two bank units from occupying the same tank/canister/straw/position
	while both are physically in storage."""
	if doc.status not in OCCUPYING_STATUSES:
		return

	if not (doc.tank and doc.canister and doc.straw_number and doc.position):
		return

	duplicate = frappe.db.exists(
		"Donor Bank Unit",
		{
			"tank": doc.tank,
			"canister": doc.canister,
			"straw_number": doc.straw_number,
			"position": doc.position,
			"status": ["in", OCCUPYING_STATUSES],
			"name": ["!=", doc.name or ""],
		},
	)

	if duplicate:
		frappe.throw(
			_("Storage location Tank {0} / Canister {1} / Straw {2} / Position {3} is already occupied by {4}").format(
				doc.tank, doc.canister, doc.straw_number, doc.position, duplicate
			)
		)


def recompute_storage_usage(doc, method=None):
	from fertility_suite.storage_tank_management.doctype.storage_tank.storage_tank import (
		recompute_tank_usage,
	)
	from fertility_suite.storage_tank_management.doctype.storage_canister.storage_canister import (
		recompute_canister_usage,
	)

	for tank_name in filter(None, {doc.tank}):
		recompute_tank_usage(tank_name)

	for canister_name in filter(None, {doc.canister}):
		recompute_canister_usage(canister_name)
