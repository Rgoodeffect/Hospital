# User Guide

## Clinical staff: running a fertility case

1. **Open a case** — Clinical workspace > Fertility Case > New. Link the Patient (create one
   first under Healthcare if needed) and the treating Doctor. A patient can only have one active
   (non-Closed/Cancelled) Fertility Case at a time — the form will block a second one.
2. **Record an assessment** — from the case, use **Create > New Fertility Assessment** to log AMH,
   FSH, LH, estradiol, TSH, prolactin, antral follicle counts, endometrium thickness, and male
   factor / semen analysis / DNA fragmentation.
3. **Build a Treatment Plan** — choose a protocol (Long / Short / Antagonist / Natural Cycle /
   Mini IVF) and move it through its own Draft → Review → Approved → Active → Completed workflow.
4. **Start an IVF Cycle** — from the case, **Create > New IVF Cycle**. Only one active cycle
   (not Completed/Cancelled) is allowed per patient at a time.

## Running an IVF cycle

The IVF Cycle's `status` field drives its workflow: Planned → Stimulation → Monitoring → Trigger
→ Retrieval → Fertilization → Embryology → Transfer → Pregnancy Test → Completed (Cancel is
available from the early stages).

- **Monitoring Visit** — log follicle sizes per ovary (a grid of Right/Left + size in mm) and
  endometrium thickness at each visit. The "Follicle Growth Timeline" (used by the IVF Progress
  portal view and available as a whitelisted method) plots the max follicle size per ovary per
  visit date.
- **Egg Retrieval** — record retrieved/mature/immature oocyte counts; mature can never exceed
  retrieved (validated on save).
- **Embryology Record** — record the fertilization method (IVF/ICSI/PICSI/IMSI) and outcome
  counts (fertilized, abnormal, Day 3/5/6, blastocysts). Fertilized oocytes can't exceed the
  linked Egg Retrieval's mature count, and blastocysts can't exceed Day 5 + Day 6 embryos.
- **Embryo Inventory** — one record per embryo, created from an Embryology Record, tracking
  stage/grade/status and (once frozen) its Tank/Canister/Straw/Position. Two embryos can never
  share the same physical location while both are in storage, and every status change is logged
  to the record's own audit trail (Status History).
- **Embryo Transfer** — a submittable document: pick embryos from inventory (only Frozen/Stored/
  Reserved embryos are eligible), submit to mark them Transferred and move the cycle to the
  Transfer state. An embryo can never be transferred twice.
- **Pregnancy Follow-up** — record beta HCG, ultrasound findings and outcome. Live
  Birth/Miscarriage/Negative outcomes automatically complete the IVF Cycle; Clinical
  Pregnancy/Ongoing Pregnancy/Live Birth mark the Fertility Case "Pregnant".

## Insurance desk

- **Insurance Company** / **Insurance Plan** are simple masters — a plan carries a billing type
  (Cash / Insurance / Co-Payment / Mixed Billing), coverage %, co-payment %, and an optional max
  coverage cap.
- **Pre Authorization** — request an amount against a plan; use the "Approve" action to set the
  approved amount and status.
- **Insurance Claim** — enter the total amount; `insurance_amount`, `co_payment_amount` and
  `patient_payable_amount` are computed automatically from the linked plan's billing type. Use
  "Approve Claim" to move it to Approved/Partially Approved and notify the patient.

## Patient portal

Patients with a linked User account (Patient.user_id) and the **Fertility Patient** role can sign
in and visit `/fertility-portal` to see their Treatment Plans, IVF Progress, Embryo Status and
Insurance Claims. Nothing there is desk UI — it's a lightweight portal page backed by the
whitelisted endpoints in `fertility_suite/api.py`, all of which pin a portal patient to their own
record regardless of what's passed in.
