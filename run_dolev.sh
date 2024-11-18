
NUM_NODES=10
python -m cs4545.system.util compose $NUM_NODES topologies/mydolev.yaml dolev
docker compose build
docker compose up