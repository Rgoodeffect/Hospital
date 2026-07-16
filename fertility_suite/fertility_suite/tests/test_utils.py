"""Shared helpers for creating minimal Healthcare master records in tests."""

import frappe


def create_test_patient(first_name="Fertility", sex="Female"):
	patient_name = f"{first_name}-{frappe.generate_hash(length=6)}"
	if frappe.db.exists("Patient", {"patient_name": patient_name}):
		return frappe.get_doc("Patient", {"patient_name": patient_name})

	patient = frappe.get_doc({
		"doctype": "Patient",
		"first_name": first_name,
		"patient_name": patient_name,
		"sex": sex,
		"dob": "1992-01-01",
	}).insert(ignore_permissions=True, ignore_mandatory=True)
	return patient


def create_test_practitioner(first_name="Dr Test"):
	name = f"{first_name}-{frappe.generate_hash(length=6)}"
	practitioner = frappe.get_doc({
		"doctype": "Healthcare Practitioner",
		"first_name": name,
		"practitioner_name": name,
	}).insert(ignore_permissions=True, ignore_mandatory=True)
	return practitioner


def create_test_fertility_case(patient=None, doctor=None, status="Draft"):
	patient = patient or create_test_patient().name
	doctor = doctor or create_test_practitioner().name

	case = frappe.get_doc({
		"doctype": "Fertility Case",
		"patient": patient,
		"doctor": doctor,
		"status": status,
	}).insert(ignore_permissions=True)
	return case


def create_test_ivf_cycle(case=None, status="Planned"):
	case = case or create_test_fertility_case()
	cycle = frappe.get_doc({
		"doctype": "IVF Cycle",
		"fertility_case": case.name,
		"doctor": case.doctor,
		"status": status,
	}).insert(ignore_permissions=True)
	return cycle


def create_test_embryology_record(cycle=None, fertilized_oocytes=6, day5_embryos=3, day6_embryos=1, blastocysts=3):
	cycle = cycle or create_test_ivf_cycle()
	retrieval = frappe.get_doc({
		"doctype": "Egg Retrieval",
		"ivf_cycle": cycle.name,
		"doctor": cycle.doctor,
		"retrieved_oocytes": fertilized_oocytes + 2,
		"mature_oocytes": fertilized_oocytes,
	}).insert(ignore_permissions=True)

	record = frappe.get_doc({
		"doctype": "Embryology Record",
		"ivf_cycle": cycle.name,
		"egg_retrieval": retrieval.name,
		"embryologist": "Administrator",
		"fertilization_method": "ICSI",
		"fertilized_oocytes": fertilized_oocytes,
		"day5_embryos": day5_embryos,
		"day6_embryos": day6_embryos,
		"blastocysts": blastocysts,
	}).insert(ignore_permissions=True)
	return record


def create_test_storage_tank(capacity=20):
	tank = frappe.get_doc({
		"doctype": "Storage Tank",
		"tank_id": f"TANK-{frappe.generate_hash(length=6)}",
		"capacity": capacity,
		"nitrogen_level": 80,
	}).insert(ignore_permissions=True)
	return tank


def create_test_storage_canister(tank=None, capacity=10):
	tank = tank or create_test_storage_tank()
	canister = frappe.get_doc({
		"doctype": "Storage Canister",
		"canister_id": f"CAN-{frappe.generate_hash(length=6)}",
		"tank": tank.name,
		"capacity": capacity,
	}).insert(ignore_permissions=True)
	return canister


def create_test_insurance_plan(billing_type="Insurance", coverage_percent=80, co_payment_percent=20,
                                max_coverage_amount=None):
	company = frappe.get_doc({
		"doctype": "Insurance Company",
		"company_name": f"Test Insurer {frappe.generate_hash(length=6)}",
	}).insert(ignore_permissions=True)

	plan = frappe.get_doc({
		"doctype": "Insurance Plan",
		"plan_name": f"Test Plan {frappe.generate_hash(length=6)}",
		"insurance_company": company.name,
		"billing_type": billing_type,
		"coverage_percent": coverage_percent,
		"co_payment_percent": co_payment_percent,
		"max_coverage_amount": max_coverage_amount,
	}).insert(ignore_permissions=True)
	return plan


def create_test_embryo(embryology_record=None, status="Frozen", tank=None, canister=None,
                        straw_number="1", position="A1"):
	embryology_record = embryology_record or create_test_embryology_record()
	embryo = frappe.get_doc({
		"doctype": "Embryo Inventory",
		"embryology_record": embryology_record.name,
		"embryo_stage": "Blastocyst",
		"embryo_grade": "AA",
		"status": status,
		"tank": tank,
		"canister": canister,
		"straw_number": straw_number if tank else None,
		"position": position if tank else None,
	}).insert(ignore_permissions=True)
	return embryo
