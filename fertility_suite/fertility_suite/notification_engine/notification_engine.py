"""Multi-channel notification dispatch for Fertility Suite events.

Channels are dispatched based on the ``channels`` MultiSelectPills field on
each Notification Template:

- Email: sent via ``frappe.sendmail`` (uses the site's configured Email Account).
- System Notification: written to Frappe's core ``Notification Log`` so it
  shows up in the bell icon / desk.
- Push Notification: broadcast via ``frappe.publish_realtime`` for any
  connected desk/portal session.
- SMS / WhatsApp: enqueued through ``dispatch_sms``/``dispatch_whatsapp``,
  which are intentionally thin integration points - wire up a real gateway
  (Twilio, Meta Cloud API, a local telco aggregator, etc.) there.
"""

import frappe
from frappe import _

DEFAULT_TEMPLATES = [
	{
		"name": "Appointment Reminder",
		"template_name": "Appointment Reminder",
		"event": "Appointment Reminder",
		"channels": "Email\nSMS\nSystem Notification",
		"subject": "Reminder: Upcoming appointment on {{ appointment_date }}",
		"message": "Dear {{ patient_name }}, this is a reminder of your appointment on {{ appointment_date }} with {{ practitioner_name }}.",
	},
	{
		"name": "Lab Result Ready",
		"template_name": "Lab Result Ready",
		"event": "Lab Result Ready",
		"channels": "Email\nSystem Notification",
		"subject": "Your lab results are ready",
		"message": "Dear {{ patient_name }}, your lab results for {{ test_name }} are now available in the patient portal.",
	},
	{
		"name": "Claim Approved",
		"template_name": "Claim Approved",
		"event": "Claim Approved",
		"channels": "Email\nSystem Notification",
		"subject": "Insurance claim {{ claim_name }} approved",
		"message": "Your insurance claim {{ claim_name }} for {{ approved_amount }} has been approved.",
	},
	{
		"name": "Cycle Started",
		"template_name": "Cycle Started",
		"event": "Cycle Started",
		"channels": "Email\nSystem Notification\nPush Notification",
		"subject": "Your IVF cycle {{ cycle_name }} has started",
		"message": "Dear {{ patient_name }}, your IVF cycle {{ cycle_name }} has moved to status {{ status }}.",
	},
	{
		"name": "Embryo Transfer Scheduled",
		"template_name": "Embryo Transfer Scheduled",
		"event": "Embryo Transfer Scheduled",
		"channels": "Email\nSMS\nSystem Notification",
		"subject": "Embryo transfer scheduled on {{ transfer_date }}",
		"message": "Dear {{ patient_name }}, your embryo transfer is scheduled on {{ transfer_date }}.",
	},
	{
		"name": "Pregnancy Test Reminder",
		"template_name": "Pregnancy Test Reminder",
		"event": "Pregnancy Test Reminder",
		"channels": "Email\nSMS\nSystem Notification",
		"subject": "Beta HCG test due",
		"message": "Dear {{ patient_name }}, your beta HCG pregnancy test is due on {{ test_date }}.",
	},
	{
		"name": "Storage Tank Alert",
		"template_name": "Storage Tank Alert",
		"event": "Storage Tank Alert",
		"channels": "Email\nSystem Notification\nPush Notification",
		"subject": "Storage Tank {{ tank_id }} needs attention",
		"message": "Tank {{ tank_id }} has triggered an alert: {{ alert_reason }}.",
	},
]


def notify(event: str, context: dict, roles: list[str] | None = None, users: list[str] | None = None):
	"""Render the Notification Template for ``event`` and dispatch it over its
	configured channels to the given roles and/or explicit users."""

	template = frappe.db.get_value(
		"Notification Template", {"event": event, "disabled": 0}, ["name", "subject", "message", "channels"], as_dict=True
	)
	if not template:
		frappe.logger("fertility_suite").info(f"No active Notification Template for event '{event}'")
		return

	subject = frappe.render_template(template.subject or event, context)
	message = frappe.render_template(template.message or "", context)
	channels = [c.strip() for c in (template.channels or "").split("\n") if c.strip()]

	recipients = set(users or [])
	for role in roles or []:
		recipients.update(frappe.get_all("Has Role", filters={"role": role, "parenttype": "User"}, pluck="parent"))

	recipients.discard("Administrator")
	recipients.discard("Guest")

	if not recipients:
		return

	for channel in channels:
		try:
			if channel == "Email":
				dispatch_email(recipients, subject, message)
			elif channel == "System Notification":
				dispatch_system_notification(recipients, subject, message, context)
			elif channel == "Push Notification":
				dispatch_push_notification(recipients, subject, message)
			elif channel == "SMS":
				dispatch_sms(recipients, message)
			elif channel == "WhatsApp":
				dispatch_whatsapp(recipients, message)
		except Exception:
			frappe.log_error(title=f"Notification dispatch failed ({channel}/{event})")


def dispatch_email(recipients, subject, message):
	emails = [
		e for e in frappe.get_all("User", filters={"name": ["in", list(recipients)]}, pluck="email") if e
	]
	if emails:
		frappe.sendmail(recipients=emails, subject=subject, message=message)


def dispatch_system_notification(recipients, subject, message, context=None):
	context = context or {}
	for user in recipients:
		frappe.get_doc({
			"doctype": "Notification Log",
			"subject": subject,
			"for_user": user,
			"type": "Alert",
			"document_type": context.get("reference_doctype"),
			"document_name": context.get("reference_name"),
			"email_content": message,
		}).insert(ignore_permissions=True)


def dispatch_push_notification(recipients, subject, message):
	for user in recipients:
		frappe.publish_realtime(
			event="fertility_suite:push_notification",
			message={"subject": subject, "message": message},
			user=user,
		)


def dispatch_sms(recipients, message):
	"""Integration point for an SMS gateway. Queues for delivery; plug in a
	real provider (Twilio, a local aggregator, etc.) by replacing the body."""
	frappe.enqueue(_send_sms_via_gateway, recipients=list(recipients), message=message, queue="short")


def dispatch_whatsapp(recipients, message):
	"""Integration point for WhatsApp Business/Cloud API."""
	frappe.enqueue(_send_whatsapp_via_gateway, recipients=list(recipients), message=message, queue="short")


def _send_sms_via_gateway(recipients, message):
	frappe.logger("fertility_suite").info(f"[SMS] to={recipients} message={message}")


def _send_whatsapp_via_gateway(recipients, message):
	frappe.logger("fertility_suite").info(f"[WhatsApp] to={recipients} message={message}")


# ---------------------------------------------------------------------------
# Scheduled reminder jobs (registered in hooks.py -> scheduler_events.daily)
# ---------------------------------------------------------------------------

def send_appointment_reminders():
	tomorrow = frappe.utils.add_days(frappe.utils.today(), 1)
	appointments = frappe.get_all(
		"Patient Appointment",
		filters={"appointment_date": tomorrow, "status": ["not in", ["Cancelled", "Closed"]]},
		fields=["name", "patient", "patient_name", "practitioner", "practitioner_name", "appointment_date"],
	)
	for appt in appointments:
		notify(
			"Appointment Reminder",
			{
				"patient_name": appt.patient_name,
				"appointment_date": appt.appointment_date,
				"practitioner_name": appt.practitioner_name,
				"reference_doctype": "Patient Appointment",
				"reference_name": appt.name,
			},
			roles=["Fertility Patient"],
		)


def send_pregnancy_test_reminders():
	due_today = frappe.get_all(
		"IVF Cycle",
		filters={"status": "Pregnancy Test"},
		fields=["name", "patient", "patient_name"],
	)
	for cycle in due_today:
		notify(
			"Pregnancy Test Reminder",
			{
				"patient_name": cycle.patient_name or cycle.patient,
				"test_date": frappe.utils.today(),
				"reference_doctype": "IVF Cycle",
				"reference_name": cycle.name,
			},
			roles=["Fertility Patient", "IVF Coordinator"],
		)
