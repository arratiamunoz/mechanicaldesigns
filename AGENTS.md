# Mechanical design repository conventions

Organize designs by existing category and keep one self-contained directory per design. Add or update one row in the root design dashboard. Match the consistency of the PCB design repository: a clear revision, concise design overview, relative links, native CAD, assembly views and verifiable release files.

Each project README includes an exploded CAD render, purpose, material and process, key dimensions and interfaces, file links and verification status. Keep:
- `cad/`: native CAD and assembled and exploded STEP, named by purpose.
- `source/`: editable modeling sources and regeneration steps.
- `drawings/`: dimensioned mechanical drawings, with sections and relevant interfacing tolerances.
- `images/`: native CAD-derived visual previews.
- `verification/`: actual checks on the released model and source.
- `quote/`: a supplier-only ZIP with drawing, per-part STEP files, material/BOM, quantities, finish, tolerances, joining scope and any stock or first-article requirements.

Keep only the current package in active project paths. Before updating the dashboard, reopen native CAD, validate STEP solids and critical fits, compare drawings and RFQ BOM to the same CAD revision, and check relative links and ZIP contents. Mark quote-ready separately from manufacturing release. Do not include proprietary PCB source or populated models, credentials, or personal procurement details in this public repository.
