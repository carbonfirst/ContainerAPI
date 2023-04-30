import "strings"
import "date"
query = from(bucket: "power_consumption")
    |> range(start: {start_time} , stop: {stop_time})
    |> filter(fn: (r) => r["_measurement"] == "power_consumption")
    |> filter(fn: (r) => r["_field"] == "power")
    |> filter(fn: (r) => r["target"] == "{application_name}" or strings.hasPrefix(v: r["target"], prefix:"{application_name}"))
    |> map(fn: (r) => ({{r with _time: date.truncate(t: r._time, unit: 1s)}}))
    |> sort(columns: ["_time"])
    |> group(columns: ["_time"])
    |> sum(column: "_value")
    |> map(fn: (r) => ({{r with power: r._value}}))
    |> map(fn: (r) => ({{r with _measurement: "power_consumption"}}))
    |> yield()
