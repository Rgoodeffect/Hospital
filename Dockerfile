# Fertility Suite - production image
# Builds a Frappe bench with ERPNext + Healthcare + Fertility Suite baked in,
# using the standard frappe_docker multi-stage layered build approach.

FROM frappe/erpnext:version-16 AS base

USER root

WORKDIR /home/frappe/frappe-bench

COPY apps.json /home/frappe/frappe-bench/apps.json

USER frappe

# Get the Healthcare and Fertility Suite apps into the bench image.
RUN bench get-app healthcare https://github.com/frappe/health --branch develop \
	&& bench get-app fertility_suite https://github.com/rgoodeffect/hospital --branch main

EXPOSE 8000 9000 6787

CMD ["bench", "start"]
