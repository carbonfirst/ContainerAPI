import "strings"
import "date"
powerTable = from(bucket: "power_consumption")
   |> range(start: {start_time} , stop: {stop_time})
   |> filter(fn: (r) => r["_measurement"] == "power_consumption")
   |> filter(fn: (r) => r["_field"] == "power")
   |> filter(fn: (r) => r["target"] == "{target}" or strings.hasPrefix(v: r["target"], prefix:"{target}"))
   |> map(fn: (r) => ({{r with _time: date.truncate(t: r._time, unit: 1s)}}))
   |> sort(columns: ["_time"])
   |> group(columns: ["_time"])
   |> sum(column: "_value")
   |> map(fn: (r) => ({{r with power: r._value}}))
   |> map(fn: (r) => ({{r with _measurement: "power_consumption"}}))

carbonTable = from(bucket: "carbon_intensity")
   |> range(start: {start_time_carbon_intensity} , stop: {stop_time})
   |> filter(fn: (r) => r["_measurement"] == "carbon_intensity")
   |> filter(fn: (r) => r["zoneName"] == "{zone}")
   |> map(fn: (r) => ({{r with carbonIntensityAvg: r._value}}))
   |> keep(columns: ["_time", "_measurement", "carbonIntensityAvg", "zoneName"])

union(tables: [powerTable, carbonTable])
   |> group()
   |> range(start: {start_time_carbon_intensity} , stop: {stop_time})
   |> sort(columns: ["_time"])
   |> fill(column: "carbonIntensityAvg", usePrevious: true)
   |> map(fn: (r) => ({{r with _value: r.power * float(v:r.carbonIntensityAvg)}}))
   |> filter( fn: (r) => r["_measurement"] == "power_consumption")
   |> integral(unit:1s)
   |> map(fn: (r) => ({{r with carbon_emission: r._value/ 3600000.0}}))
   |> keep(columns: ["carbon_emission"])
   |> yield()