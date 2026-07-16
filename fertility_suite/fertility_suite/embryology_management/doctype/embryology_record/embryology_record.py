import frappe
from frappe import _
from frappe.model.document import Document


class EmbryologyRecord(Document):
	def validate(self):
		self.validate_against_egg_retrieval()
		self.validate_development_counts()

	def validate_against_egg_retrieval(self):
		if not self.egg_retrieval:
			return

		mature_oocytes = frappe.db.get_value("Egg Retrieval", self.egg_retrieval, "mature_oocytes") or 0
		fertilized = self.fertilized_oocytes or 0

		if fertilized > mature_oocytes:
			frappe.throw(
				_("Fertilized Oocytes ({0}) cannot exceed Mature Oocytes ({1}) from {2}").format(
					fertilized, mature_oocytes, self.egg_retrieval
				)
			)

	def validate_development_counts(self):
		fertilized = self.fertilized_oocytes or 0
		day3 = self.day3_embryos or 0
		blastocysts = self.blastocysts or 0
		day5 = self.day5_embryos or 0
		day6 = self.day6_embryos or 0

		if day3 > fertilized:
			frappe.throw(_("Day 3 Embryos ({0}) cannot exceed Fertilized Oocytes ({1})").format(day3, fertilized))

		if blastocysts > (day5 + day6):
			frappe.throw(
				_("Blastocysts ({0}) cannot exceed Day 5 + Day 6 Embryos ({1})").format(
					blastocysts, day5 + day6
				)
			)
