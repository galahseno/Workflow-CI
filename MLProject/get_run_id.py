import mlflow
from mlflow.tracking import MlflowClient

mlflow.set_tracking_uri("file:///tmp/mlruns")
client = MlflowClient()

experiment = client.get_experiment_by_name("Cardiovascular_Classifier")
if experiment is None:
    raise Exception("Experiment not found.")

runs = client.search_runs(
    experiment_ids=[experiment.experiment_id],
    order_by=["start_time DESC"],
    max_results=1
)

if not runs:
    raise Exception("No runs found.")

run_id = runs[0].info.run_id
print(f"::set-output name=run_id::{run_id}")
