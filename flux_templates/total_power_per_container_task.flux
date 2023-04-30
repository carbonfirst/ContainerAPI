import "strings"

option task = {name: "power_integration", every: 1s, offset: 7s}

containers_power = from(bucket: "power_consumption")
	|> range(start: -10s)
    |> filter(fn: (r) => (r["target"] != "rapl" and r["target"] != "global" and r["target"] != "system"))
    |> group(columns: ["target", "sensor"])
	|> keep(columns: ["_time", "_value", "_measurement", "_field", "sensor", "target"])
	|> to(bucket: "per_container_power")