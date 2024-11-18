
NUM_NODES=4
python -m cs4545.system.util compose $NUM_NODES topologies/election.yaml ring
docker compose build
docker compose up