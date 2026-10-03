# CharterCore deployment

1. Install the current GenLayer SDK and Direct Mode test dependencies.
2. Run the repository preflight: `python scripts/preflight.py`.
3. Run the Direct Mode tests with the current GenLayer test runner.
4. Deploy `contracts/charter.py` through GenLayer Studio or the supported deployment workflow.
5. Record the actual deployed contract address and transaction in `deployment-template.json`.
6. Open the frontend and set the deployed address in `frontend/config.js` if you want the dashboard to point at the live contract.

Do not submit placeholder deployment data as if it were a live receipt.
