"""Generates realistic, varied demo data across every Fertility Suite module -
patients, cases, cycles, monitoring, retrieval, embryology, embryo bank,
transfers, pregnancy follow-up, insurance, and donor bank - so a fresh
install looks and behaves like a populated clinic instead of an empty
schema.

Not part of after_install (a real production site should start empty).
Run explicitly:

    bench --site your-site.local execute fertility_suite.setup.demo_data.generate_demo_data
"""

import random

import frappe
from frappe.utils import add_days, today

random.seed(42)

FIRST_NAMES = [
	"Sara", "Fatima", "Noura", "Layla", "Maryam", "Aisha", "Hind", "Reem", "Dana", "Rania",
	"Amira", "Salma", "Yasmin", "Lina", "Huda", "Nadia", "Samar", "Ghada", "Iman", "Zainab",
	"Emily", "Sophia", "Olivia", "Emma", "Ava", "Isabella", "Mia", "Charlotte", "Amelia", "Grace",
	"Priya", "Anjali", "Meera", "Aylin", "Elif",
]
LAST_NAMES = [
	"Al-Sayed", "Al-Farsi", "Khan", "Hassan", "Mansour", "Al-Rashid", "Qureshi", "Haddad",
	"Karimi", "Osman", "Yousef", "Al-Amin", "Nasser", "Saleh", "Al-Zahrani", "Ibrahim",
	"Chowdhury", "Demir", "Fernandes", "Williams", "Johnson", "Brown", "Davies", "Martin",
]
DOCTOR_NAMES = [
	"Dr. Layla Haddad", "Dr. Omar Khalil", "Dr. Nadia Mansour", "Dr. James Whitfield",
	"Dr. Priya Nair", "Dr. Ahmed Farouk",
]
EMBRYOLOGIST_NAMES = ["Dr. Sana Idris", "Dr. Marco Rossi"]
DIAGNOSES = [
	"Unexplained Infertility", "Polycystic Ovary Syndrome (PCOS)", "Tubal Factor Infertility",
	"Male Factor Infertility", "Endometriosis", "Diminished Ovarian Reserve",
	"Advanced Maternal Age", "Recurrent Implantation Failure",
]
PROTOCOLS = ["Long Protocol", "Short Protocol", "Antagonist Protocol", "Natural Cycle", "Mini IVF"]
CYCLE_STAGES = [
	"Planned", "Stimulation", "Monitoring", "Trigger", "Retrieval",
	"Fertilization", "Embryology", "Transfer", "Pregnancy Test", "Completed", "Cancelled",
]
GRADES = ["AA", "AB", "BA", "BB", "AC", "BC", "CC"]
INSURANCE_COMPANY_NAMES = ["Gulf Shield Insurance", "MedTrust Assurance", "National Health Cover"]
PATIENT_BLOOD_GROUPS = [
	"A Positive", "A Negative", "AB Positive", "AB Negative",
	"B Positive", "B Negative", "O Positive", "O Negative",
]
DONOR_BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]


def generate_demo_data():
	if frappe.db.exists("Insurance Company", "Gulf Shield Insurance"):
		frappe.msgprint("Demo data already present - skipping. Delete demo records first to regenerate.")
		return

	doctors = _create_doctors()
	embryologists = _create_embryologists()
	tanks = _create_storage()
	insurance_plans = _create_insurance_plans()

	patients = [_create_patient(i) for i in range(35)]

	for i, patient in enumerate(patients):
		try:
			_build_patient_journey(i, patient, doctors, embryologists, tanks, insurance_plans)
			frappe.db.commit()
		except Exception:
			frappe.db.rollback()
			frappe.log_error(title="Demo data generation failed for a patient", message=frappe.get_traceback())

	try:
		_create_embryo_bank_data(tanks, patients)
		frappe.db.commit()
	except Exception:
		frappe.db.rollback()
		frappe.log_error(title="Demo data generation failed for Embryo Bank", message=frappe.get_traceback())

	try:
		_generate_kpi_and_dashboard_snapshots()
		frappe.db.commit()
	except Exception:
		frappe.db.rollback()
		frappe.log_error(title="Demo data generation failed for KPI/Dashboard snapshots", message=frappe.get_traceback())

	frappe.msgprint("Demo data generated across all Fertility Suite modules.")


# ---------------------------------------------------------------------------
# Masters: doctors, embryologists, storage, insurance
# ---------------------------------------------------------------------------

def _create_doctors():
	names = []
	for full_name in DOCTOR_NAMES:
		if frappe.db.exists("Healthcare Practitioner", {"practitioner_name": full_name}):
			names.append(frappe.db.get_value("Healthcare Practitioner", {"practitioner_name": full_name}, "name"))
			continue
		doc = frappe.get_doc({
			"doctype": "Healthcare Practitioner",
			"first_name": full_name,
			"practitioner_name": full_name,
		}).insert(ignore_permissions=True, ignore_mandatory=True)
		names.append(doc.name)
	return names


def _create_embryologists():
	names = []
	for full_name in EMBRYOLOGIST_NAMES:
		email = full_name.lower().replace("dr. ", "").replace(" ", ".") + "@fertility-suite.demo"
		if frappe.db.exists("User", email):
			names.append(email)
			continue
		user = frappe.get_doc({
			"doctype": "User",
			"email": email,
			"first_name": full_name,
			"send_welcome_email": 0,
		}).insert(ignore_permissions=True)
		user.add_roles("Embryologist")
		names.append(user.name)
	return names


def _create_storage():
	tanks = []
	for t in range(1, 4):
		tank_id = f"TANK-DEMO-{t:02d}"
		if frappe.db.exists("Storage Tank", tank_id):
			tank = frappe.get_doc("Storage Tank", tank_id)
		else:
			tank = frappe.get_doc({
				"doctype": "Storage Tank",
				"tank_id": tank_id,
				"location": f"Cryo Room {t}",
				"capacity": 200,
				"nitrogen_level": random.randint(65, 95),
			}).insert(ignore_permissions=True)
		canisters = []
		for c in range(1, 3):
			canister_id = f"CAN-DEMO-{t:02d}-{c}"
			if frappe.db.exists("Storage Canister", canister_id):
				canister = frappe.get_doc("Storage Canister", canister_id)
			else:
				canister = frappe.get_doc({
					"doctype": "Storage Canister",
					"canister_id": canister_id,
					"tank": tank.name,
					"capacity": 40,
				}).insert(ignore_permissions=True)
			canisters.append(canister.name)
		tanks.append({"tank": tank.name, "canisters": canisters})
	return tanks


def _create_insurance_plans():
	plans = []
	billing_types = ["Insurance", "Co-Payment", "Mixed Billing", "Cash"]
	for i, company_name in enumerate(INSURANCE_COMPANY_NAMES):
		if frappe.db.exists("Insurance Company", company_name):
			company = frappe.get_doc("Insurance Company", company_name)
		else:
			company = frappe.get_doc({
				"doctype": "Insurance Company",
				"company_name": company_name,
				"contact_person": random.choice(FIRST_NAMES) + " " + random.choice(LAST_NAMES),
				"phone": f"+971-4-{random.randint(1000000, 9999999)}",
			}).insert(ignore_permissions=True)

		plan_name = f"{company_name} - Fertility Plan"
		if frappe.db.exists("Insurance Plan", plan_name):
			plans.append(plan_name)
			continue
		frappe.get_doc({
			"doctype": "Insurance Plan",
			"plan_name": plan_name,
			"insurance_company": company.name,
			"billing_type": billing_types[i % len(billing_types)],
			"coverage_percent": random.choice([50, 60, 70, 80]),
			"co_payment_percent": random.choice([10, 20, 30]),
			"max_coverage_amount": random.choice([20000, 30000, 50000]),
		}).insert(ignore_permissions=True)
		plans.append(plan_name)
	return plans


def _create_patient(index):
	first = random.choice(FIRST_NAMES)
	last = random.choice(LAST_NAMES)
	patient_name = f"Demo Patient {index + 1:02d} - {first} {last}"
	age = random.randint(25, 43)
	dob = add_days(today(), -365 * age - random.randint(0, 300))
	patient = frappe.get_doc({
		"doctype": "Patient",
		"first_name": first,
		"last_name": last,
		"patient_name": patient_name,
		"sex": "Female",
		"dob": dob,
		"blood_group": random.choice(PATIENT_BLOOD_GROUPS),
		"mobile": f"+971-5{random.randint(0,9)}-{random.randint(1000000,9999999)}",
	}).insert(ignore_permissions=True, ignore_mandatory=True)
	return patient


# ---------------------------------------------------------------------------
# Per-patient cascade
# ---------------------------------------------------------------------------

CASE_STATUS_WEIGHTS = [
	("Draft", 0.15), ("Assessment", 0.15), ("Treatment", 0.20),
	("IVF Active", 0.25), ("Pregnant", 0.15), ("Closed", 0.07), ("Cancelled", 0.03),
]


def _weighted_choice(weighted):
	options, weights = zip(*weighted)
	return random.choices(options, weights=weights, k=1)[0]


def _build_patient_journey(index, patient, doctors, embryologists, tanks, insurance_plans):
	doctor = random.choice(doctors)
	case_status = _weighted_choice(CASE_STATUS_WEIGHTS)

	case = frappe.get_doc({
		"doctype": "Fertility Case",
		"patient": patient.name,
		"doctor": doctor,
		"case_opened_on": add_days(today(), -random.randint(10, 400)),
		"partner_name": random.choice(FIRST_NAMES) + " " + random.choice(LAST_NAMES),
		"marriage_duration_years": round(random.uniform(1, 12), 1),
		"diagnosis": f"<p>{random.choice(DIAGNOSES)}</p>",
	}).insert(ignore_permissions=True)
	if case_status != "Draft":
		frappe.db.set_value("Fertility Case", case.name, "status", case_status)

	_create_fertility_assessment(case, doctor)

	plan_status = {
		"Draft": "Draft", "Assessment": "Review", "Treatment": "Active",
		"IVF Active": "Active", "Pregnant": "Completed", "Closed": "Completed", "Cancelled": "Draft",
	}[case_status]
	plan = frappe.get_doc({
		"doctype": "Treatment Plan",
		"fertility_case": case.name,
		"doctor": doctor,
		"protocol_type": random.choice(PROTOCOLS),
		"start_date": add_days(today(), -random.randint(5, 300)),
		"plan_notes": f"<p>{random.choice(PROTOCOLS)} recommended based on ovarian reserve assessment.</p>",
	}).insert(ignore_permissions=True)
	if plan_status != "Draft":
		frappe.db.set_value("Treatment Plan", plan.name, "status", plan_status)

	if case_status in ("Draft", "Assessment"):
		# no IVF cycle yet at this stage of care
		if random.random() < 0.4:
			_create_insurance_flow(patient, case, plan, insurance_plans, "Pre Authorization Only")
		return

	target_stage = _pick_cycle_stage(case_status)
	cycle = _create_ivf_cycle(case, plan, doctor, target_stage)
	_cascade_cycle_artifacts(cycle, target_stage, doctor, embryologists, tanks)

	if random.random() < 0.6:
		_create_insurance_flow(patient, case, plan, insurance_plans, "Full Claim")


def _pick_cycle_stage(case_status):
	if case_status == "IVF Active":
		return _weighted_choice([
			("Planned", 0.1), ("Stimulation", 0.15), ("Monitoring", 0.15), ("Trigger", 0.1),
			("Retrieval", 0.15), ("Fertilization", 0.1), ("Embryology", 0.15), ("Transfer", 0.1),
		])
	if case_status == "Pregnant":
		return _weighted_choice([("Pregnancy Test", 0.3), ("Completed", 0.7)])
	if case_status == "Closed":
		return _weighted_choice([("Completed", 0.85), ("Cancelled", 0.15)])
	if case_status == "Cancelled":
		return _weighted_choice([("Cancelled", 0.7), ("Planned", 0.3)])
	return "Planned"


def _create_fertility_assessment(case, doctor):
	frappe.get_doc({
		"doctype": "Fertility Assessment",
		"fertility_case": case.name,
		"assessment_date": add_days(case.case_opened_on, random.randint(1, 14)),
		"amh": round(random.uniform(0.5, 4.5), 2),
		"fsh": round(random.uniform(3, 12), 2),
		"lh": round(random.uniform(2, 10), 2),
		"estradiol": round(random.uniform(20, 80), 1),
		"tsh": round(random.uniform(0.5, 4.0), 2),
		"prolactin": round(random.uniform(5, 25), 1),
		"afc_right": random.randint(3, 15),
		"afc_left": random.randint(3, 15),
		"endometrium_thickness": round(random.uniform(6, 12), 1),
	}).insert(ignore_permissions=True)


def _create_ivf_cycle(case, plan, doctor, target_stage):
	start_date = add_days(today(), -random.randint(5, 90))
	cycle = frappe.get_doc({
		"doctype": "IVF Cycle",
		"fertility_case": case.name,
		"treatment_plan": plan.name,
		"doctor": doctor,
		"cycle_start_date": start_date,
		"trigger_date": add_days(start_date, 10) if CYCLE_STAGES.index(target_stage) >= CYCLE_STAGES.index("Trigger") else None,
	}).insert(ignore_permissions=True)
	if target_stage != "Planned":
		frappe.db.set_value("IVF Cycle", cycle.name, "status", target_stage)
		cycle.status = target_stage
	return cycle


def _cascade_cycle_artifacts(cycle, target_stage, doctor, embryologists, tanks):
	stage_idx = CYCLE_STAGES.index(target_stage)
	if target_stage == "Cancelled":
		if random.random() < 0.5:
			_create_monitoring_visits(cycle, count=random.randint(1, 2))
		return

	if stage_idx >= CYCLE_STAGES.index("Monitoring"):
		_create_monitoring_visits(cycle, count=random.randint(2, 4))

	if stage_idx < CYCLE_STAGES.index("Retrieval"):
		return

	retrieved = random.randint(6, 18)
	mature = random.randint(int(retrieved * 0.6), retrieved)
	retrieval = frappe.get_doc({
		"doctype": "Egg Retrieval",
		"ivf_cycle": cycle.name,
		"doctor": doctor,
		"retrieval_date": add_days(cycle.cycle_start_date, 12),
		"retrieved_oocytes": retrieved,
		"mature_oocytes": mature,
		"immature_oocytes": retrieved - mature,
	}).insert(ignore_permissions=True)

	if stage_idx < CYCLE_STAGES.index("Fertilization"):
		return

	fertilized = random.randint(int(mature * 0.6), mature)
	day5 = random.randint(int(fertilized * 0.3), max(1, int(fertilized * 0.6)))
	day6 = random.randint(0, max(0, fertilized - day5))
	blastocysts = random.randint(1, day5 + day6) if (day5 + day6) else 0

	embryology = frappe.get_doc({
		"doctype": "Embryology Record",
		"ivf_cycle": cycle.name,
		"egg_retrieval": retrieval.name,
		"embryologist": random.choice(embryologists),
		"fertilization_method": random.choice(["IVF", "ICSI", "PICSI"]),
		"fertilization_date": add_days(retrieval.retrieval_date, 1),
		"fertilized_oocytes": fertilized,
		"abnormal_oocytes": mature - fertilized,
		"embryo_grades": ", ".join(random.sample(GRADES, k=min(3, len(GRADES)))),
		"day3_embryos": fertilized,
		"day5_embryos": day5,
		"day6_embryos": day6,
		"blastocysts": blastocysts,
	}).insert(ignore_permissions=True)

	if stage_idx < CYCLE_STAGES.index("Embryology"):
		return

	embryos = _create_embryo_inventory(embryology, blastocysts or 1, tanks)
	frozen_embryos = [e["name"] for e in embryos if e["status"] == "Frozen"]

	if stage_idx < CYCLE_STAGES.index("Transfer") or not frozen_embryos:
		return

	transfer_count = min(len(frozen_embryos), random.randint(1, 2))
	transfer_embryos = frozen_embryos[:transfer_count]
	transfer = frappe.get_doc({
		"doctype": "Embryo Transfer",
		"ivf_cycle": cycle.name,
		"doctor": doctor,
		"transfer_date": add_days(embryology.fertilization_date, 5),
		"embryos": [{"embryo": e} for e in transfer_embryos],
		"notes": "<p>Single/double embryo transfer under ultrasound guidance.</p>",
	}).insert(ignore_permissions=True)
	transfer.submit()

	if stage_idx < CYCLE_STAGES.index("Pregnancy Test"):
		return

	outcome = _weighted_choice([
		("Negative", 0.35), ("Biochemical", 0.1), ("Clinical Pregnancy", 0.15),
		("Ongoing Pregnancy", 0.15), ("Live Birth", 0.2), ("Miscarriage", 0.05),
	])
	frappe.get_doc({
		"doctype": "Pregnancy Follow Up",
		"ivf_cycle": cycle.name,
		"embryo_transfer": transfer.name,
		"follow_up_date": add_days(transfer.transfer_date, 14),
		"beta_hcg": round(random.uniform(1, 5), 1) if outcome == "Negative" else round(random.uniform(50, 4000), 1),
		"outcome": outcome,
		"ultrasound_findings": f"<p>{outcome} on follow-up beta hCG and ultrasound.</p>",
	}).insert(ignore_permissions=True)


def _create_monitoring_visits(cycle, count):
	for v in range(count):
		visit_date = add_days(cycle.cycle_start_date, 3 + v * 2)
		frappe.get_doc({
			"doctype": "Monitoring Visit",
			"ivf_cycle": cycle.name,
			"visit_date": visit_date,
			"endometrium_thickness": round(random.uniform(6, 13), 1),
			"follicle_measurements": [
				{"ovary": "Right", "follicle_size": round(random.uniform(8, 20), 1)}
				for _ in range(random.randint(2, 5))
			] + [
				{"ovary": "Left", "follicle_size": round(random.uniform(8, 20), 1)}
				for _ in range(random.randint(2, 5))
			],
		}).insert(ignore_permissions=True)


def _create_embryo_inventory(embryology, count, tanks):
	embryos = []
	for i in range(count):
		outcome = _weighted_choice([("Frozen", 0.55), ("Transferred", 0.15), ("Discarded", 0.15), ("Created", 0.15)])
		doc_fields = {
			"doctype": "Embryo Inventory",
			"embryology_record": embryology.name,
			"embryo_stage": "Blastocyst",
			"embryo_grade": random.choice(GRADES),
			"status": "Created",
			"freeze_date": embryology.fertilization_date if outcome in ("Frozen", "Stored") else None,
		}
		if outcome in ("Frozen", "Stored"):
			slot = _next_storage_slot(tanks)
			doc_fields.update(slot)
		embryo = frappe.get_doc(doc_fields).insert(ignore_permissions=True)
		if outcome != "Created":
			embryo.status = outcome
			embryo.save(ignore_permissions=True)
		embryos.append({"name": embryo.name, "status": embryo.status})
	return embryos


_slot_counter = {"n": 0}


def _next_storage_slot(tanks):
	_slot_counter["n"] += 1
	n = _slot_counter["n"]
	tank_group = tanks[n % len(tanks)]
	canister = tank_group["canisters"][n % len(tank_group["canisters"])]
	row = "ABCDE"[(n // 10) % 5]
	col = (n % 10) + 1
	return {
		"tank": tank_group["tank"],
		"canister": canister,
		"straw_number": str(n),
		"position": f"{row}{col}",
	}


def _create_insurance_flow(patient, case, plan, insurance_plans, mode):
	insurance_plan = random.choice(insurance_plans)
	pre_auth = frappe.get_doc({
		"doctype": "Pre Authorization",
		"patient": patient.name,
		"insurance_plan": insurance_plan,
		"fertility_case": case.name,
		"treatment_plan": plan.name,
		"request_date": add_days(today(), -random.randint(1, 60)),
		"requested_amount": random.choice([8000, 12000, 18000, 25000]),
	}).insert(ignore_permissions=True)

	pa_status = _weighted_choice([("Submitted", 0.2), ("Approved", 0.65), ("Rejected", 0.1), ("Expired", 0.05)])
	if pa_status == "Approved":
		frappe.db.set_value("Pre Authorization", pre_auth.name, {
			"status": "Approved", "approved_amount": pre_auth.requested_amount,
		})
	elif pa_status != "Draft":
		frappe.db.set_value("Pre Authorization", pre_auth.name, "status", pa_status)

	if mode != "Full Claim" or pa_status != "Approved":
		return

	claim = frappe.get_doc({
		"doctype": "Insurance Claim",
		"patient": patient.name,
		"insurance_plan": insurance_plan,
		"pre_authorization": pre_auth.name,
		"fertility_case": case.name,
		"claim_date": add_days(pre_auth.request_date, random.randint(5, 20)),
		"total_amount": pre_auth.requested_amount,
	}).insert(ignore_permissions=True)
	claim_status = _weighted_choice([("Submitted", 0.25), ("Approved", 0.35), ("Partially Approved", 0.15), ("Paid", 0.2), ("Rejected", 0.05)])
	if claim_status != "Draft":
		frappe.db.set_value("Insurance Claim", claim.name, "status", claim_status)


# ---------------------------------------------------------------------------
# Embryo Bank (donor registry)
# ---------------------------------------------------------------------------

def _create_embryo_bank_data(tanks, patients):
	from fertility_suite.embryo_bank.doctype.gamete_donor.gamete_donor import (
		recompute_consent_status,
		recompute_screening_status,
	)

	donor_types = ["Egg"] * 8 + ["Sperm"] * 6 + ["Embryo"] * 3
	donors = []
	for i, donor_type in enumerate(donor_types):
		donor = frappe.get_doc({
			"doctype": "Gamete Donor",
			"donor_type": donor_type,
			"anonymous": 1,
			"blood_group": random.choice(DONOR_BLOOD_GROUPS),
			"date_of_birth": add_days(today(), -365 * random.randint(21, 34)),
			"ethnicity": random.choice(["Middle Eastern", "South Asian", "East Asian", "European", "African"]),
			"height_cm": round(random.uniform(155, 190), 1),
			"weight_kg": round(random.uniform(50, 90), 1),
			"eye_color": random.choice(["Brown", "Hazel", "Green", "Blue"]),
			"hair_color": random.choice(["Black", "Brown", "Blonde", "Dark Brown"]),
			"education_level": random.choice(["Bachelor's Degree", "Master's Degree", "PhD", "Diploma"]),
			"registered_on": add_days(today(), -random.randint(30, 500)),
		}).insert(ignore_permissions=True)
		donors.append(donor)

		screening_result = _weighted_choice([("Passed", 0.85), ("Failed", 0.1), ("Pending", 0.05)])
		screening = frappe.get_doc({
			"doctype": "Donor Screening",
			"donor": donor.name,
			"screening_type": random.choice([
				"Infectious Disease Panel", "Genetic Carrier Panel", "Psychological Evaluation", "Physical Examination",
			]),
			"screening_date": add_days(donor.registered_on, random.randint(1, 14)),
			"result": screening_result,
		}).insert(ignore_permissions=True)
		if screening_result != "Pending":
			screening.submit()
			recompute_screening_status(donor.name)

		if screening_result == "Passed" and random.random() < 0.9:
			consent = frappe.get_doc({
				"doctype": "Donor Consent",
				"donor": donor.name,
				"consent_type": random.choice([
					"Donation for Treatment", "Donation for Research", "Anonymous Donation",
				]),
				"signed_date": add_days(donor.registered_on, random.randint(1, 20)),
				"witnessed_by": random.choice(DOCTOR_NAMES),
			}).insert(ignore_permissions=True)
			consent.submit()
			recompute_consent_status(donor.name)

	eligible_donors = [
		d for d in donors
		if frappe.db.get_value("Gamete Donor", d.name, "screening_status") == "Passed"
		and frappe.db.get_value("Gamete Donor", d.name, "consent_on_file")
	]

	units = []
	for donor in eligible_donors:
		for _ in range(random.randint(1, 3)):
			status = _weighted_choice([("Available", 0.5), ("Reserved", 0.15), ("Allocated", 0.1), ("Used", 0.15), ("Pending QC", 0.1)])
			unit_fields = {
				"doctype": "Donor Bank Unit",
				"donor": donor.name,
				"quantity": random.randint(1, 6),
				"status": "Pending QC",
				"grade": random.choice(GRADES),
				"freeze_date": add_days(today(), -random.randint(5, 400)),
			}
			if status in ("Available", "Reserved", "Allocated"):
				slot = _next_storage_slot(tanks)
				unit_fields.update(slot)
			unit = frappe.get_doc(unit_fields).insert(ignore_permissions=True)
			if status != "Pending QC":
				unit.status = status
				unit.save(ignore_permissions=True)
			units.append(unit)

	allocatable = [u for u in units if u.status == "Available"]
	for unit in random.sample(allocatable, k=min(5, len(allocatable))):
		recipient = random.choice(patients).name
		allocation = frappe.get_doc({
			"doctype": "Donor Allocation",
			"donor_bank_unit": unit.name,
			"recipient_patient": recipient,
			"allocation_date": add_days(today(), -random.randint(1, 60)),
			"matching_criteria": "Blood group and physical characteristics matched per clinic protocol.",
			"consent_confirmed": 1,
			"status": "Allocated",
		}).insert(ignore_permissions=True)
		allocation.submit()


# ---------------------------------------------------------------------------
# KPI / Dashboard snapshots (so the Executive workspace has trend history)
# ---------------------------------------------------------------------------

def _generate_kpi_and_dashboard_snapshots():
	# These engines always snapshot as of today() (no historical backfill
	# parameter exists), so we just seed one real snapshot of each kind
	# against the demo data just generated.
	from fertility_suite.analytics_and_kpi_engine.kpi_engine import generate_daily_kpi_snapshot
	from fertility_suite.executive_dashboards.dashboard_engine import (
		generate_clinical_dashboard_snapshot,
		generate_weekly_executive_snapshot,
	)

	generate_daily_kpi_snapshot()
	generate_clinical_dashboard_snapshot()
	generate_weekly_executive_snapshot()
