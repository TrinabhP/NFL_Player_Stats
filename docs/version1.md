Group Project: V1 Get something working
The goal of version 1 of your application is getting your service initially deployed and a single end-to-end use case working. Take one of the example workflows you previously defined and implement it. The workflow must be one that includes at least one endpoint that modifies data (either creates or updates) in your database. Your service must be deployed on render and wired into a production database.

You will need to provide test results for executing your example workflow in a file named v1_manual_test_results.md that looks like the following:

# Example workflow
<copy and paste the workflow you had described in the
early group project assignment that you will first implement>

# Testing results
<Repeated for each step of the workflow>
1. The curl statement called. You can find this in the /docs site for your 
API under each endpoint. For example, for my site the /catalogs/ endpoint 
curl call looks like:
curl -X 'GET' \
  'https://centralcoastcauldrons.vercel.app/catalog/' \
  -H 'accept: application/json'
2. The response you received in executing the curl statement.
Additionally, make sure you have alembic versions that create the schema required for your service. Someone should be able to run alembic upgrade head after cloning your repo and it should successfully build your service in their local postgres.

Please submit a link to your team's github as the submission statement.