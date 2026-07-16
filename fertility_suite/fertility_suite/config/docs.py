"""Configuration for docs generation of the Fertility Suite app."""

source_link = "https://github.com/rgoodeffect/hospital"
docs_base_url = "https://github.com/rgoodeffect/hospital/tree/main/docs"
headline = "Fertility, IVF, Embryology and Embryo Bank Management for ERPNext"
sub_heading = "A complete fertility clinic operating system built on ERPNext Healthcare"


def get_context(context):
	context.brand_html = "Fertility Suite"
