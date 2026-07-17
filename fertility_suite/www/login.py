from frappe.www.login import get_context as _get_context

no_cache = True


def get_context(context):
	"""Reuse Frappe's real login context (redirects, social login providers,
	LDAP, signup/email-link flags, CSRF, etc.) - only the template markup in
	login.html is themed, the actual auth logic is untouched."""
	return _get_context(context)
