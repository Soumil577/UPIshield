# UPIShield — Immersive UI Update

This build keeps the existing UPIShield backend/API architecture and extends the Lovable-inspired visual frontend with a more immersive command-centre shell.

## Visual updates

- Integrated the reference screenshot's institutional header language:
  - National Cybercrime Intelligence Workspace label
  - Financial fraud surveillance subtitle
  - Larger search control
  - Systems Operational status block
  - Notification control
  - Operator control
- Added a persistent, restrained intelligence-grid background and vertical command rail.
- Increased top-level workspace breathing room while preserving information density.
- Added subtle environmental gradients and depth rather than heavy glassmorphism/neon effects.
- Strengthened the Command Centre hero, map and operational surfaces with depth and hierarchy.
- Preserved the green/cream/orange visual identity established by the Lovable design.

## Functional preservation

The existing routes and API integration are retained:

- `/`
- `/cases/[id]`
- `/cashout`
- `/alerts`

Existing FastAPI endpoints, NetworkX investigation visualization, GIS map, risk scoring, cash-out prediction, complaints, cases and alerts are preserved.

## Run

```bash
cd frontend
npm install
npm run dev
```

The backend can be run from the project root with the existing UPIShield instructions.
