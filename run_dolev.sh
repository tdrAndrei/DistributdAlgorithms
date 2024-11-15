
NUM_NODES=9
python -m cs4545.system.util compose $NUM_NODES topologies/dolev.yaml dolev
docker compose build
docker compose up