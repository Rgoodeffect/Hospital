# Fertility Suite - production image
# Builds a Frappe bench with ERPNext + Healthcare + Fertility Suite baked in,
# using the standard frappe_docker multi-stage layered build approach.

FROM frappe/erpnext:version-16 AS base

USER root

WORKDIR /home/frappe/frappe-bench

COPY apps.json /home/frappe/frappe-bench/apps.json
COPY docker-entrypoint-wrapper.sh /usr/local/bin/docker-entrypoint-wrapper.sh
RUN chmod +x /usr/local/bin/docker-entrypoint-wrapper.sh

USER frappe

# Get the Healthcare and Fertility Suite apps into the bench image, then build
# fertility_suite's own frontend assets (CSS/JS), baked into the image.
# Scoped to --app fertility_suite: a full `bench build` also tries to build
# Healthcare's separate Vite sub-app (patient_portal), which needs
# sites/common_site_config.json keys (e.g. socketio_port) that don't exist
# yet at image-build time, before any site has been created.
RUN bench get-app --skip-assets healthcare https://github.com/frappe/health --branch version-16 \
	&& bench get-app --skip-assets fertility_suite https://github.com/rgoodeffect/hospital --branch main \
	&& bench setup procfile \
	&& bench build --app fertility_suite

EXPOSE 8000 9000 6787

ENTRYPOINT ["/usr/local/bin/docker-entrypoint-wrapper.sh"]
CMD ["bench", "start"]
